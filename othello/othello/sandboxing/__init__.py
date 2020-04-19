import os
import json
import shlex
import subprocess

from django.conf import settings

FIREJAIL_PROFILE = os.path.join(settings.BASE_DIR, "sandboxing", "sandbox.profile")
IMPORT_WRAPPER = os.path.join(settings.BASE_DIR, "sandboxing", "import_wrapper.py")
JAILEDRUNNER_DRIVER = os.path.join(settings.BASE_DIR, "moderator", "wrapper.py")


OTHELLO_AI_IMPORT_COMMAND = f"python3 -u {IMPORT_WRAPPER} {'{path!r}'}"


def import_strategy_sandboxed(path):
    cmd_args = get_sandbox_args(shlex.split(OTHELLO_AI_IMPORT_COMMAND.format(path=path), posix=False))
    p = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode == 0:
        return 0
    else:
        try:
            return json.loads(error.decode())
        except:
            return {"message": "Unexpected error when validating submission"}


def get_sandbox_args(cmd_args, *, whitelist=None, readonly=None, extra_args=None):
    if settings.DEBUG:
        return [*cmd_args]
    firejail_args = [
        "firejail",
        "--quiet",
        "--net=none"
        f"--profile={FIREJAIL_PROFILE}",
    ]

    if whitelist:
        for path in whitelist:
            firejail_args.append(f"--whitelist={path}")

    if readonly:
        for path in readonly:
            firejail_args.append(f"--readonly={path}")

    if extra_args:
        firejail_args.extend(extra_args)

    return [*firejail_args, *cmd_args]
