import os
import json
import shlex
import subprocess

BASE_DIR = os.path.dirname(__file__)
OTHELLO_AI_IMPORT_COMMAND = f"python3 {BASE_DIR}/import_wrapper.py {'{0}'}"


def import_strategy_sandboxed(path):
    cmd_args = shlex.split(OTHELLO_AI_IMPORT_COMMAND.format(path), posix=False)
    p = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode == 0:
        return 0
    else:
        return json.loads(error.decode())
