import os


def do_shell(command):
    try:
        status = os.system(command)
    except Exception as e:
        print(e)
        return None
    return status
