import sys
import logging

from .runners import JailedRunner

log = logging.getLogger(__name__)


if __name__ == "__main__":
    path = sys.argv[-1]
    JailedRunner(path).run()
