import psutil


def kill_access_controller():
    processname = "python3"

    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == processname:
            proc.kill()

kill_access_controller()