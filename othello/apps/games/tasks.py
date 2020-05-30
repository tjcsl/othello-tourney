from datetime import datetime, timedelta
from time import sleep

from asgiref.sync import async_to_sync
from celery import shared_task
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer

from django.conf import settings
from django.db.models import Q

from ...moderator import *
from ..games.models import Game, Player, Submission

task_logger = get_task_logger(__name__)


def send_through_socket(game, event_type):
    task_logger.error(f"sending {event_type}")
    async_to_sync(get_channel_layer().group_send)(game.channels_group_name, {"type": event_type})


def ping(game):
    if game.is_tournament:
        return True
    game.ping = False
    game.save(update_fields=["ping"])
    send_through_socket(game, "game.ping")
    sleep(0.5)
    game.refresh_from_db()
    return game.ping


def delete(game):
    if not game.is_tournament:
        game.delete()


@shared_task
def run_game(game_id):
    try:
        game = Game.objects.get(id=game_id)
        yourself = Submission.objects.get(user__username="Yourself")
    except Game.DoesNotExist:
        return
    except Submission.DoesNotExist:
        return

    mod, time_limit = Moderator(), game.time_limit
    game_over = False
    file_deleted = None

    try:
        black_runner = (
            YourselfRunner(game, settings.YOURSELF_TIMEOUT)
            if game.black == yourself
            else PlayerRunner(game.black.code.path, settings.JAILEDRUNNER_DRIVER, settings.DEBUG)
        )
    except OSError:
        black_runner = None
        file_deleted = game.errors.create(
            player=Player.BLACK.value,
            error_code=ServerError.FILE_DELETED.value[0],
            error_msg=ServerError.FILE_DELETED.value[1],
        )
    try:
        white_runner = (
            YourselfRunner(game, settings.YOURSELF_TIMEOUT)
            if game.white == yourself
            else PlayerRunner(game.white.code.path, settings.JAILEDRUNNER_DRIVER, settings.DEBUG)
        )
    except OSError:
        white_runner = None
        file_deleted = game.errors.create(
            player=Player.WHITE.value,
            error_code=ServerError.FILE_DELETED.value[0],
            error_msg=ServerError.FILE_DELETED.value[1],
        )

    if file_deleted is not None:
        game.forfeit = False
        game.outcome = "T"
        game.playing = False
        game.save(update_fields=["forfeit", "outcome", "playing"])
        send_through_socket(game, "game.error")
        return

    with black_runner as player_black, white_runner as player_white:
        last_move = game.moves.create(board=INITIAL_BOARD, player="-", possible=[26, 19, 44, 37])
        send_through_socket(game, "game.update")

        while not mod.is_game_over():
            if not ping(game):
                game.playing = False
                game.outcome = "T"
                game.forfeit = False
                game.save(update_fields=["playing", "outcome", "forfeit"])
                delete(game)
                return
            board, current_player = mod.get_game_state()

            try:
                if current_player == Player.BLACK:
                    running_turn = player_black.get_move(
                        board, current_player.value, time_limit, last_move
                    )
                elif current_player == Player.WHITE:
                    running_turn = player_white.get_move(
                        board, current_player.value, time_limit, last_move
                    )
            except BaseException as e:
                task_logger.error(str(e))

            for log in running_turn:
                game.logs.create(
                    player=current_player.value, message=log,
                )
                send_through_socket(game, "game.log")
                sleep(0.05)
            submitted_move, error = running_turn.return_value

            if error != 0:
                game.errors.create(
                    player=current_player.value,
                    error_code=error.value[0],
                    error_msg=error.value[1],
                )
                if isinstance(error, ServerError):
                    game.forfeit = False
                    game.outcome = "T"
                elif isinstance(error, UserError):
                    game.forfeit = True
                    game.outcome = (
                        Player.BLACK.value if current_player == Player.WHITE else Player.WHITE.value
                    )
                game.playing = False
                game.save(update_fields=["forfeit", "outcome", "playing"])
                send_through_socket(game, "game.error")
                break

            try:
                if submitted := mod.submit_move(submitted_move):
                    possible = submitted
                else:
                    game_over = True
            except InvalidMoveError as e:
                game.errors.create(
                    player=current_player.value, error_code=e.code, error_msg=e.message,
                )
                game.forfeit, game.playing = True, False
                game.outcome = (
                    Player.BLACK.value if current_player == Player.WHITE else Player.WHITE.value
                )
                game.save(update_fields=["forfeit", "outcome", "playing"])
                send_through_socket(game, "game.error")
                break

            last_move = game.moves.create(
                player=current_player.value,
                move=submitted_move,
                board=mod.get_board(),
                possible=possible,
            )
            if game_over:
                game.forfeit = False
                game.outcome = mod.outcome()
                game.score = mod.score()
                game.save(update_fields=["forfeit", "score", "outcome", "playing"])
                task_logger.error("GAME OVER")
                break
            send_through_socket(game, "game.update")
    game.playing = False
    game.save(update_fields=["playing"])
    send_through_socket(game, "game.update")
    black_runner.stop()
    white_runner.stop()


@shared_task
def delete_old_games():
    Game.objects.filter(is_tournament=False).filter(
        Q(playing=False) | Q(created_at__lt=datetime.now() - timedelta(hours=settings.STALE_GAME))
    ).delete()
