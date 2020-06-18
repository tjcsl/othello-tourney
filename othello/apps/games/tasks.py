import logging
from datetime import datetime, timedelta
from time import sleep

from asgiref.sync import async_to_sync
from celery import shared_task
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from ...moderator.moderator import INITIAL_BOARD, InvalidMoveError, Moderator
from ...moderator.runners import PlayerRunner, ServerError, UserError, YourselfRunner
from ..games.models import Game, Player, Submission

logger = logging.getLogger("othello")
task_logger = get_task_logger(__name__)


def send_through_game_channel(game, event_type):
    print('sending' + event_type)
    task_logger.debug(f"sending {event_type}")
    async_to_sync(get_channel_layer().group_send)(game.channels_group_name, {"type": event_type})


def ping(game):
    if game.is_tournament:
        return True
    game.refresh_from_db()
    return (timezone.now() - game.last_heartbeat).seconds < settings.CLIENT_HEARTBEAT_INTERVAL * 2


def delete_game(game):
    if not game.is_tournament:
        game.delete()


@shared_task
def run_game(game_id):
    try:
        game = Game.objects.get(id=game_id)
        yourself = Submission.objects.get(user__username="Yourself")
    except Game.DoesNotExist:
        logger.error(f"Trying to play nonexistent game ({game_id}")
        return "game not found"

    mod, time_limit = Moderator(), game.time_limit
    game_over = False
    file_deleted = None

    try:
        black_runner = (
            YourselfRunner(game, settings.YOURSELF_TIMEOUT)
            if game.black == yourself
            else PlayerRunner(game.black, settings.JAILEDRUNNER_DRIVER)
        )
    except OSError:
        logger.error(f"Cannot find submission code file! {game.black.code.path}")
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
            else PlayerRunner(game.white, settings.JAILEDRUNNER_DRIVER)
        )
    except OSError:
        logger.error(f"Cannot find submission code file! {game.white.code.path}")
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
        send_through_game_channel(game, "game.error")
        raise RuntimeError("Cannot find a submission code file!")

    error = 0
    with black_runner as player_black, white_runner as player_white:
        last_move = game.moves.create(board=INITIAL_BOARD, player="-", possible=[26, 19, 44, 37])
        send_through_game_channel(game, "game.update")
        exception = None

        while not mod.is_game_over():
            if not ping(game):
                game.playing = False
                game.outcome = "T"
                game.forfeit = False
                game.save(update_fields=["playing", "outcome", "forfeit"])
                delete_game(game)
                return "no ping"
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
                logger.error(f"Error when getting move {game_id}, {current_player}, {str(e)}")
                task_logger.error(str(e))
                exception = e

            for log in running_turn:
                print(log)
                game.logs.create(
                    player=current_player.value, message=log,
                )
                send_through_game_channel(game, "game.log")
                sleep(1)
            submitted_move, error = running_turn.return_value

            if exception is not None:
                error = ServerError.UNEXPECTED

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
                send_through_game_channel(game, "game.error")
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
                send_through_game_channel(game, "game.error")
                task_logger.info(
                    f"{game_id}: {current_player.value} submitted invalid move {submitted}"
                )
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
                task_logger.info(f"GAME {game_id} OVER")
                break
            send_through_game_channel(game, "game.update")
    game.playing = False
    game.save(update_fields=["playing"])
    send_through_game_channel(game, "game.update")
    black_runner.stop()
    white_runner.stop()

    if error != 0 and isinstance(error, ServerError):
        if error.value[0] != -8:
            raise RuntimeError(f"Game {game_id} encountered a ServerError of value {error.value}")


@shared_task
def delete_old_games():
    logger.info("Deleting stale games")
    Game.objects.filter(is_tournament=False).filter(
        Q(playing=False) | Q(created_at__lt=datetime.now() - timedelta(hours=settings.STALE_GAME))
    ).delete()
