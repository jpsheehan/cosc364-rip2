# import signal

# __timer_period = None


# def __timer_handler_func(x, y): return None


# def init(period, handler):
#     global __timer_period, __timer_handler_func
#     __timer_period = period
#     __timer_handler_func = handler


# def start():
#     signal.signal(signal.SIGALRM, __timer_handler)
#     signal.alarm(__timer_period)


# def stop():
#     signal.alarm(0)


# def __timer_handler(signum, frame):
#     __timer_handler_func()
#     start()

import time


class Timer:

    def __init__(self, period, callback):
        self.__period = period
        self.__callback = callback
        self.__started = False
        self.__startedTime = 0
        self.__paused = False
        self.__pausedTime = 0
        self.__updateTime = 0

    def start(self):
        if not self.__started:
            t = time.time()
            self.__started = True
            self.__startedTime = t
            self.__paused = False
            self.__pausedTime = 0
            self.__updateTime = t

    def stop(self):
        if self.__started:
            self.__started = False
            self.__startedTime = 0
            self.__paused = False
            self.__pausedTime = 0
            self.__updateTime = 0

    def reset(self):
        if self.__started:
            self.stop()
            self.start()

    def pause(self):
        if self.__started and not self.__paused:
            self.__paused = True
            self.__pausedTime = time.time() - self.__startedTime
            self.__startedTime = 0

    def resume(self):
        if self.__started and self.__paused:
            self.__startedTime = time.time() - self.__pausedTime
            self.__paused = False
            self.__pausedTime = 0

    def update(self):
        if self.__started and not self.__paused:
            t = time.time()
            if t - self.__updateTime > self.__period:
                self.__updateTime = t
                self.__callback()

    def getElapsed(self):
        if self.__started:
            if self.__paused:
                return self.__pausedTime
            else:
                return time.time() - self.__startedTime
        return 0

    def isStarted(self):
        """
        >>> t = Timer(10, None)
        >>> t.isStarted()
        False
        >>> t.start()
        >>> t.isStarted()
        True
        >>> t.stop()
        >>> t.isStarted()
        False
        """
        return self.__started

    def isPaused(self):
        """
        >>> t = Timer(10, None)
        >>> t.isPaused()
        False
        >>> t.start()
        >>> t.isPaused()
        False
        >>> t.pause()
        >>> t.isPaused()
        True
        >>> t.resume()
        >>> t.isPaused()
        False
        >>> t.stop()
        >>> t.isPaused()
        False
        >>> t.start()
        >>> t.pause()
        >>> t.isPaused()
        True
        >>> t.stop()
        >>> t.isPaused()
        False
        """
        return self.__paused and self.__started

    def __str__(self):
        return "Timer <period={0}s, started={1}, paused={2}, elapsed={3}s>".format(self.__period, self.__started, self.__paused, self.getElapsed())


if __name__ == "__main__":
    import doctest
    doctest.testmod()
