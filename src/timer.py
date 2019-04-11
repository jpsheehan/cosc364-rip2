import signal

__timer_period = None


def __timer_handler_func(x, y): return None


def init(period, handler):
    global __timer_period, __timer_handler_func
    __timer_period = period
    __timer_handler_func = handler


def start():
    signal.signal(signal.SIGALRM, __timer_handler)
    signal.alarm(__timer_period)


def stop():
    signal.alarm(0)


def __timer_handler(signum, frame):
    __timer_handler_func()
    start()
