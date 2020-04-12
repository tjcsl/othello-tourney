from othello.othello.moderator.runners import JailedRunnerCommunicator


def f(x):
    print(x)


jrc = JailedRunnerCommunicator("/home/abagali1/Testing/othello-tourney/othello/othello/submissions/2021abagali/strategy.py", f)
jrc.start()
print(jrc.get_move("board", "player", 5))

jrc.stop()
