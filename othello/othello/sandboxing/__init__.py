import os
import json
import shlex
import subprocess

DEBUG = False
BASE_DIR = os.path.dirname(__file__)
IMPORT_WRAPPER = os.path.join(BASE_DIR, "import_wrapper.py")
FIREJAIL_PROFILE = os.path.join(BASE_DIR, "sandbox.profile")

if DEBUG:
    OTHELLO_AI_IMPORT_COMMAND = f"python3 -u {IMPORT_WRAPPER} {'{0}'}"
else:
    OTHELLO_AI_IMPORT_COMMAND = f"firejail --quiet --profile={FIREJAIL_PROFILE} --whitelist={'{0}'} python3 -u {IMPORT_WRAPPER} {'{0}'}"


def import_strategy_sandboxed(path):
    cmd_args = shlex.split(OTHELLO_AI_IMPORT_COMMAND.format(path), posix=False)
    p = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode == 0:
        return 0
    else:
        try:
            return json.loads(error.decode())
        except:
            return {"message": "Unexpected error when validating submission"}
