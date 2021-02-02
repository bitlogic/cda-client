import psutil


def kill_access_controller():
    PROCNAME = "python3"

for proc in psutil.process_iter():
    # check whether the process name matches
    if proc.name() == PROCNAME:
        proc.kill()

kill_access_controller()