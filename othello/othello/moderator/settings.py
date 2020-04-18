# TODO: Delete in favor of deprecating JRC/GR for celery task

import os

DEBUG = True
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OTHELLO_AI_HUMAN_PLAYER = "Yourself"

JAILEDRUNNER_DRIVER = os.path.join(PROJECT_ROOT, "moderator", "wrapper.py")

if DEBUG:
    OTHELLO_AI_RUN_COMMAND = f"python3 -u {JAILEDRUNNER_DRIVER} {'{0}'}"
else:
    OTHELLO_AI_RUN_COMMAND = f"firejail --quiet --profile={FIREJAIL_PROFILE} --whitelist={'{0}'} python3 -u {JAILEDRUNNER_DRIVER} {'{0}'}"
