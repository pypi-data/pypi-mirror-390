import subprocess
import os.path
import json


def run_process_in_venv(dir: str, cmd: str, params):
    if not (os.path.exists(dir) and os.path.isdir(dir)):
        return f"dir {dir} not exists"

    cmd = [
        os.path.join(dir, "venv/bin/python"),
        os.path.join(dir, cmd),
        json.dumps(params) if isinstance(params, dict) else str(params),
    ]
    # print(cmd)
    completedProcess = subprocess.run(cmd, capture_output=True)
    r = str(completedProcess)
    return r
