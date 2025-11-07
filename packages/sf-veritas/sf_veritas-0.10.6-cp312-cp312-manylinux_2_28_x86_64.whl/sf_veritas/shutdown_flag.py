import atexit

is_shutting_down = False


def set_shutdown_flag():
    global is_shutting_down
    is_shutting_down = True


atexit.register(set_shutdown_flag)
