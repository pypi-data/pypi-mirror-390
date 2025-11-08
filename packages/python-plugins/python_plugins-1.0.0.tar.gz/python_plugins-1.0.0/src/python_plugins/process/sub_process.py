import subprocess
import json


def run_process(cmd: str, params=None,shell=False):
    cmd_args = [
        cmd,
        json.dumps(params) if isinstance(params, dict) else str(params),
    ]
    completedProcess = subprocess.run(cmd_args, capture_output=True,shell=shell)
    r = str(completedProcess)
    return r
