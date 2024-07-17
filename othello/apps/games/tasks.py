import logging
from datetime import datetime, timedelta
from typing import Optional

from asgiref.sync import async_to_sync
from celery import shared_task
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from ...moderator import INITIAL_BOARD
from ...moderator.moderator import InvalidMoveError, Moderator
from ...moderator.runners import PlayerRunner, ServerError, UserError, YourselfRunner
from ..games.models import Game, Player, Submission

logger = logging.getLogger("othello")
task_logger = get_task_logger(__name__)


def send_through_game_channel(game: Game, event_type: str, object_id: int) -> int:
    task_logger.debug(f"sending {event_type}")
    async_to_sync(get_channel_layer().group_send)(game.channels_group_name, {"type": event_type, "object_id": object_id})


def check_heartbeat(game: Game) -> bool:
    if game.is_tournament or game.is_ranked or game.is_gauntlet:
        return True
    game.refresh_from_db()
    return (timezone.now() - game.last_heartbeat).seconds < settings.CLIENT_HEARTBEAT_INTERVAL * 2


def delete_game(game: Game) -> None:
    if not game.is_tournament and not game.is_ranked and not game.is_gauntlet:
        game.delete()


@shared_task
def run_game(game_id: int) -> Optional[str]:
    try:
        game = Game.objects.get(id=game_id)
        yourself = Submission.objects.get(user__username="Yourself")
    except Game.DoesNotExist:
        logger.error(f"Trying to play nonexistent game ({game_id}")
        return "game not found"

    mod = Moderator()
    black_time_limit, white_time_limit = game.time_limit, game.time_limit
    game_over = False
    file_deleted = None

    try:
        black_runner = YourselfRunner(game, settings.YOURSELF_TIMEOUT) if game.black == yourself else PlayerRunner(game.black, settings.JAILEDRUNNER_DRIVER)
    except OSError:
        logger.error(f"Cannot find submission code file! {game.black.code.path}")
        black_runner = None
        file_deleted = game.errors.create(
            player=Player.BLACK.value,
            error_code=ServerError.FILE_DELETED.value[0],
            error_msg=ServerError.FILE_DELETED.value[1],
        )
    try:
        white_runner = YourselfRunner(game, settings.YOURSELF_TIMEOUT) if game.white == yourself else PlayerRunner(game.white, settings.JAILEDRUNNER_DRIVER)
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
        send_through_game_channel(game, "game.error", file_deleted.id)
        raise RuntimeError("Cannot find a submission code file!")

    # print("IM HERE NOW")

    try:
        error = 0
        with black_runner as player_black, white_runner as player_white:
            last_move = game.moves.create(board=INITIAL_BOARD, player="-", possible=[26, 19, 44, 37])
            send_through_game_channel(game, "game.update", game_id)
            exception = None

            while not mod.is_game_over():
                if not check_heartbeat(game) or not game.playing:
                    game.playing = False
                    game.outcome = "T"
                    game.forfeit = False
                    game.save(update_fields=["playing", "outcome", "forfeit"])
                    return "no ping"
                board, current_player = mod.get_game_state()
                # print(board)

                try:
                    if current_player == Player.BLACK:
                        running_turn = player_black.get_move(board, current_player, black_time_limit, last_move)
                    elif current_player == Player.WHITE:
                        running_turn = player_white.get_move(board, current_player, white_time_limit, last_move)
                except BaseException as e:
                    logger.error(f"Error when getting move {game_id}, {current_player}, {str(e)}")
                    task_logger.error(str(e))
                    exception = e

                for log in running_turn:
                    print(log)
                    game_log = game.logs.create(player=current_player.value, message=log)
                    send_through_game_channel(game, "game.log", game_log.id)
                submitted_move, error, extra_time = running_turn.return_value

                if exception is not None:
                    error = ServerError.UNEXPECTED

                if game.runoff:
                    if current_player == Player.BLACK:
                        black_time_limit = game.time_limit + extra_time
                    else:
                        white_time_limit = game.time_limit + extra_time

                if error != 0:
                    game_err = game.errors.create(player=current_player.value, error_code=error.value[0], error_msg=error.value[1])
                    if isinstance(error, ServerError):
                        game.forfeit = False
                        game.outcome = "T"
                    elif isinstance(error, UserError):
                        game.forfeit = True
                        game.outcome = Player.BLACK.value if current_player == Player.WHITE else Player.WHITE.value
                    game.playing = False
                    game.save(update_fields=["forfeit", "outcome", "playing"])
                    send_through_game_channel(game, "game.error", game_err.id)
                    break

                try:
                    if submitted := mod.submit_move(submitted_move):
                        possible = submitted
                    else:
                        game_over = True
                except InvalidMoveError as e:
                    game_err = game.errors.create(player=current_player.value, error_code=e.code, error_msg=e.message)
                    game.forfeit, game.playing = True, False
                    game.outcome = current_player.opposite_player().value
                    game.save(update_fields=["forfeit", "outcome", "playing"])
                    send_through_game_channel(game, "game.error", game_err.id)
                    task_logger.info(f"{game_id}: {current_player.value} submitted invalid move {submitted}")
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
                send_through_game_channel(game, "game.update", game_id)
    except BaseException as error:
        print(error)

    game.playing = False
    game.save(update_fields=["playing"])
    send_through_game_channel(game, "game.update", game_id)
    black_runner.stop()
    white_runner.stop()

    # print("DONE", game.playing, game.score)

    if error != 0 and isinstance(error, ServerError):
        if error.value[0] != -8:
            raise RuntimeError(f"Game {game_id} encountered a ServerError of value {error.value}")


@shared_task
def delete_old_games() -> None:
    logger.info("Deleting stale games")
    Game.objects.filter(is_tournament=False).filter(Q(playing=False) | Q(created_at__lt=datetime.now() - timedelta(hours=settings.STALE_GAME))).delete()
