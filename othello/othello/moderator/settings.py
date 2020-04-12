import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = True

OTHELLO_AI_HUMAN_PLAYER = "Yourself"

FIREJAIL_PROFILE = os.path.join(PROJECT_ROOT, "sandboxing", "sandbox.profile"),
JAILEDRUNNER_DRIVER = os.path.join(PROJECT_ROOT, "moderator", "wrapper.py")

if DEBUG:
    OTHELLO_AI_RUN_COMMAND = f"python3 -u {JAILEDRUNNER_DRIVER} {'{0}'}"
else:
    OTHELLO_AI_RUN_COMMAND = f"firejail --quiet --profile={FIREJAIL_PROFILE} --whitelist={'{0}'} --readonly={'{0}'} python3 -u {JAILEDRUNNER_DRIVER} {'{0}'}"
