#!/usr/bin/python3

"""

    timer.py

    COSC364 RIP Assignment

    Date: 02/05/2019

    Written by:
     - Will Cowper (81163265)
     - Jesse Sheehan (53366509)
    
"""

import time

class Timer:

    def __init__(self, period, callback):
        """
            Creates a new Timer with a period and a callback.
        """
        self.__period = period
        self.__callback = callback
        self.__started = False
        self.__startedTime = 0
        self.__paused = False
        self.__pausedTime = 0
        self.__updateTime = 0

    def start(self):
        """
            Starts the timer.
        """
        if not self.__started:
            t = time.time()
            self.__started = True
            self.__startedTime = t
            self.__paused = False
            self.__pausedTime = 0
            self.__updateTime = t

    def stop(self):
        """
            Stops the timer.
        """
        if self.__started:
            self.__started = False
            self.__startedTime = 0
            self.__paused = False
            self.__pausedTime = 0
            self.__updateTime = 0

    def reset(self):
        """
            Resets the timer.
        """
        if self.__started:
            self.stop()
            self.start()

    def pause(self):
        """
            Pauses the timer.
        """
        if self.__started and not self.__paused:
            self.__paused = True
            self.__pausedTime = time.time() - self.__startedTime
            self.__startedTime = 0

    def resume(self):
        """
            Resumes the timer.
        """
        if self.__started and self.__paused:
            self.__startedTime = time.time() - self.__pausedTime
            self.__paused = False
            self.__pausedTime = 0

    def update(self):
        """
            Updates the timer. May call its callback.
        """
        if self.__started and not self.__paused:
            t = time.time()
            dt = t - self.__updateTime
            if dt > self.__period:
                self.__updateTime = t
                self.__callback(dt)
    
    def trigger(self):
        """
            Forcefully call the callback.
        """
        if self.__started and not self.__paused:
            t = time.time()
            dt = t - self.__updateTime
            self.__updateTime = t
            self.__callback(dt)

    def getElapsed(self):
        """
            Returns the time elapsed in seconds.
        """
        if self.__started:
            if self.__paused:
                return self.__pausedTime
            else:
                return time.time() - self.__startedTime
        return 0.0

    def isStarted(self):
        """
            Returns True if the timer has been started.
        
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
            Returns True if the timer has been paused.
        
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
        """
            Returns a string representation of the timer.
        """
        return "Timer <period={0:.3}s, started={1}, paused={2}, elapsed={3:.3}s>".format(self.__period, self.__started, self.__paused, self.getElapsed())

    def __repr__(self):
        """
            Returns a string representation of the timer.
        """
        return self.__str__()

# run doctests
if __name__ == "__main__":
    import doctest
    doctest.testmod()
