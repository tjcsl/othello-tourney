import logging, random, time, sys
from datetime import datetime, timedelta
from typing import Optional
from django.utils import timezone


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

gameQueue = []
lastTime = datetime.now()
# will not run the first task, to prevent a bunch of tasks built up all being run at once

@shared_task
def rankedSchedulerProcess():
    global lastTime

    if datetime.now() - lastTime < timedelta(seconds=45):
        print("skipping")
        return
    
    lastTime = datetime.now()
    
    manager = RankedManager.objects.first()
    if manager.game and not manager.game.playing:
        game = manager.game
        # the game finished, let's update ELO
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
    elif manager.game and manager.game.playing:
        return
    
    if manager.auto_run:
        global gameQueue
        if len(gameQueue) == 0: # then we have to queue the players!
            players = Submission.objects.rated()
            if players.count() < 2: 
                logger.warn("Too few players eligble for ranked!")
                return
            matches = doPairing(players.count())
            submissions = list(players)
            for tpl in matches:
                gameQueue.append((submissions[tpl[0]], submissions[tpl[1]]))
            logger.warn(f"Created game queue: {str(gameQueue)}")

        if not manager.running:
            black = gameQueue[-1][0]
            white = gameQueue[-1][1]
            logger.warn(f"Queueing ranked game --> {black} vs. {white}")
            
            game = Game.objects.create(
                black=black,
                white=white,
                blackRating=black.rating,
                whiteRating=white.rating,
                time_limit=5,
                playing=True,
                last_heartbeat=timezone.now(),
                runoff=False,
                is_ranked=True,
            )

            manager.game = game
            manager.running = True
            manager.save()

            run_game.delay(manager.game.id)
            gameQueue.pop()

    manager.save()    