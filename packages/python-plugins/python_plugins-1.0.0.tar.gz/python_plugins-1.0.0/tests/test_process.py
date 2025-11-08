import pytest
from python_plugins.process import run_process

@pytest.mark.skip(reason="[test_shell_process] only for debug.")
def test_run_process():
    cmd = 'ls '
    params='-l'
    r = run_process(cmd,params,True)
    # print(r)