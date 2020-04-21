import sys

from othello.moderator.runners import JailedRunner

if __name__ == "__main__":
    path = sys.argv[-1]
    JailedRunner(path).run()
