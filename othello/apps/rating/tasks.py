import logging, random, time, sys
from datetime import datetime, timedelta
from typing import Optional

from asgiref.sync import async_to_sync
from celery import shared_task
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer

from django.conf import settings

from ..games.models import Submission, Game
from ..auth.models import User
from .models import Gauntlet, RankedManager
from ..games.tasks import run_game

from typing import Iterator, List, Tuple, TypeVar
T = TypeVar("T")

logger = logging.getLogger("othello")
task_logger = get_task_logger(__name__)


def chunks(v: List[T], n: int) -> Iterator[Tuple[T]]:
    for i in range(0, len(v), n):
        yield tuple(v[i: i + n])

@shared_task
def runGauntlet(user_id: int) -> str:
    user = User.objects.filter(id=user_id).first()
    myGauntlet = Gauntlet.objects.filter(user=user, finished=False).first()
    
    #with transaction.atomic():
    myGauntlet.running = True # this is redundancy
    myGauntlet.save()

    myGauntlet.game1.playing = True
    myGauntlet.game2.playing = True
    myGauntlet.game3.playing = True
    myGauntlet.game3.save()
    myGauntlet.game2.save()
    myGauntlet.game1.save()

    run_game(myGauntlet.game1.id)
    # myGauntlet.game1.refresh_from_db()
    # print("game 1 is finished")
    # print(myGauntlet.game1.outcome, myGauntlet.game1.playing, myGauntlet.game1.score)

    run_game(myGauntlet.game2.id)
    # myGauntlet.game2.refresh_from_db()
    # print("game 2 is finished")
    # print(myGauntlet.game2.outcome, myGauntlet.game2.playing, myGauntlet.game2.score)

    run_game(myGauntlet.game3.id)
    # myGauntlet.game3.refresh_from_db()
    # print("game 3 is finished")
    # print(myGauntlet.game3.outcome, myGauntlet.game3.playing, myGauntlet.game3.score)

    user.is_gauntlet_running = False
    user.save() #update_fields=["is_gauntlet_running"]

    myGauntlet.finished = True
    myGauntlet.save()

    myGauntlet.refresh_from_db()
    if myGauntlet.game1.outcome == myGauntlet.mySide1 and myGauntlet.game2.outcome == myGauntlet.mySide2 and myGauntlet.game3.outcome == myGauntlet.mySide3:
        myGauntlet.submission.gauntlet = True
        myGauntlet.submission.rating = myGauntlet.pastRating
        myGauntlet.submission.save()

    allGauntlets = Gauntlet.objects.filter(finished=False).order_by("-created_at")
    if allGauntlets.first():
        allGauntlets.first().running = True
        allGauntlets.first().save()
        runGauntlet.delay(allGauntlets.first().user.id)

def calculateElo(r1, r2, score):
    # Let K = 32
    # WHERE r1 >= r2
    assert r1 >= r2
    p = (1 / (1 + 10 ** ((r1-r2) / 400)))
    expected = 64 * (1-p) - 32

    score = score*p + (32 if score > 0 else -32 if score < 0 else 0)
    
    delta = (32 / 64) * (score - expected)
    return round(delta) 

def doPairing(n):
    assert n >= 2
    if n == 3:
        psbl = [
            [(0, 1), (1, 2), (0, 2)],
            [(1, 0), (1, 2), (0, 2)],
            [(0, 1), (2, 1), (0, 2)],
            [(1, 0), (2, 1), (0, 2)],
            [(0, 1), (1, 2), (2, 0)],
            [(1, 0), (1, 2), (2, 0)],
            [(0, 1), (2, 1), (2, 0)],
            [(1, 0), (2, 1), (2, 0)],
        ]
        return random.choice(psbl)
    elif n == 2:
        psbl = [
            [(0, 1), (1, 0)],
            [(1, 0), (0, 1)],
        ]
        return random.choice(psbl)

    pairs = []
    lst = [i for i in range(n)]
    
    maxDelta = max(2, min(n//10, 8)) #isn't a hard max, but is conducive

    while lst:
        l = lst[0]
        d = random.randint(1, min(maxDelta, len(lst)-1))
        pairs.append((l, lst[d]))
        lst.remove(lst[d])
        lst.remove(l)

        if len(lst) < 2: break

        r = lst[-1]
        d = random.randint(1, min(maxDelta, len(lst)-1))
        pairs.append((r, lst[-1-d]))
        lst.remove(lst[-1-d])
        lst.remove(r)

        if len(lst) < 2: break

    lst2 = [i for i in range(n)]
    if len(lst) == 1:
        d1 = random.randint(lst[0]+1, min(lst[0]+maxDelta, n-1))
        d2 = random.randint(max(0, lst[0]-maxDelta), lst[0]-1)
        pairs.append((lst[0], d1))
        pairs.append((lst[0], d2))
        lst2.remove(d1)
        lst2.remove(d2)
        lst2.remove(lst[0])

    lst = lst2
    while lst:
        l = lst[0]
        d = random.randint(1, min(maxDelta, len(lst)-1))
        pairs.append((l, lst[d]))
        lst.remove(lst[d])
        lst.remove(l)

        if len(lst) < 2: break

        r = lst[-1]
        d = random.randint(1, min(maxDelta, len(lst)-1))
        pairs.append((r, lst[-1-d]))
        lst.remove(lst[-1-d])
        lst.remove(r)

        if len(lst) < 2: break

    # print(pairs)
    # print(len(pairs))
        
    assert len(pairs) == n
    occur = [0 for _ in range(n)]
    for i, j in pairs:
        occur[i] += 1
        occur[j] += 1
    for i in range(n):
        assert occur[i] == 2
    
    return pairs


def deleteAllRankedGames():
    games = Game.objects.filter(is_ranked=True)
    games.delete()
    #games.save()

def getNextScrimTime():
    #batches happen monday, wednesday, friday, 4pm
    today = datetime.today()
    mon = (-today.weekday() + 7) % 7
    wed = (2-today.weekday()+7) % 7
    fri = (4-today.weekday()+7) % 7

    if mon == 0 or wed == 0 or fri == 0:
        if datetime.now().hour >= 16: # if its after 4pm, then we dont want to run today
            if mon == 0: mon = 1000
            if wed == 0: wed = 1000
            if fri == 0: fri = 1000

    if mon < wed and mon < fri:
        logger.warning("Next run is monday")
        today += timedelta(days=mon)
    elif wed < mon and wed < fri:
        logger.warning("Next run is wednesday")
        today += timedelta(days=wed)
    elif fri < mon and fri < wed:
        logger.warning("Next run is friday")
        today += timedelta(days=fri)

    today = today.replace(hour=16, minute=0, second=0, microsecond=0)

    return today

@shared_task
def runAllScrims():
    manager = RankedManager.objects.first()
    if manager.running:
        logger.warning("Did not run a batch since one already is running")
        return

    manager.running = True
    manager.save()

    deleteAllRankedGames()
    
    players = Submission.objects.rated()
    matches = doPairing(players.count())
    submissions = list(players)

    # print(matches, submissions)

    for round_matches in chunks(matches, 1 if sys.platform == "win32" else settings.CONCURRENT_GAME_LIMIT):
            games = []
            
            for i, j in round_matches:
                submissions[i].refresh_from_db()
                submissions[j].refresh_from_db()
                game = Game.objects.create(
                    black=submissions[i],
                    white=submissions[j],
                    blackRating=submissions[i].rating,
                    whiteRating=submissions[j].rating,
                    time_limit=5,
                    playing=True,
                    is_ranked=True
                )
                games.append(game)
                logger.warning(f"Upcoming matches: {str(game)}")
                run_game.delay(game.id)
            
            # tasks = {game: run_game.delay(game.id) for game in games}
            # return

            for it in range(1000): # if this doesn't finish in 15 minutes, just moves on
                running = False
                for game in games:
                                #tasks = {game: run_tournament_game.delay(game.id) for game in games}
                    game.refresh_from_db()
                    running = running or game.playing
                # print("check ", running)
                if not running: break
                time.sleep(1)

            running = False
            for game in games:
                running = running or game.playing
            if running:
                logger.warn("Some games didn't finish. Very bad.")
            
            for game in games:
                r1 = game.black.rating
                r2 = game.white.rating
                if r1 >= r2:
                    delta = calculateElo(r1, r2, game.score)
                    game.ratingDelta = delta
                    r1 += delta
                    r2 -= delta
                else:
                    delta = calculateElo(r2, r1, -game.score)
                    game.ratingDelta = -delta
                    r1 -= delta
                    r2 += delta
                game.black.rating = r1
                game.white.rating = r2
                game.black.save()
                game.white.save()
                
                game.save()

    manager.running = False
    
    # THIS IS NOT TESTED - has the precondition that this is the only task queued, so its safe to queue another runAllScrims
    if manager.auto_run:
        logger.warning("queueing batch for later")
        manager.next_auto_run = getNextScrimTime()
        task = runAllScrims.apply_async([], eta=manager.next_auto_run)
        manager.celery_task_id = task.id

    manager.save()
    return