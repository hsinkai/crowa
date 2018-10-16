# -*- coding: utf-8 -*-

"""
Created on 2016年12月24日
@author: albin
"""

import logging
import os
import threading
import time
import sys


__version__ = '1.0.0'

_lock = threading.Lock()
LoggerClass = logging.getLoggerClass()


def make_handler(filename=None, format="[%(levelname)s][%(asctime)s] - %(message)s", capacity=1, flushInterval=120,
                 flushLevel=logging.ERROR):
    """Factory function that return a new instance of `logging.FileHandler`  or  `logging.StreamHandler` or `_MemoryHandler`(with buffer)
    according to the argument `capacity` and `filename`.
    :param filename: new an instance of `logging.StreamHandler` using `sys.stdout` as the underlying stream if None or it's omitted,
           otherwise new an instance of `logging.FileHandler`.
    :param format: Format string for handlers.
    :param capacity: It will be passed to create a `_MemoryHandler` if its value greater then 1.
    :param flushInterval: the argument of the `_MemoryHandler`.
    :param flushLevel: the argument of the `_MemoryHandler`.
    """
    # create a core handler
    if filename is None:
        handler = logging.StreamHandler(stream=sys.stdout)
    else:
        filename = os.path.abspath(filename)
        with _lock:
            if not os.path.exists(os.path.dirname(filename) or './'):
                os.makedirs(os.path.dirname(filename), )
        handler = logging.FileHandler(filename)

    # configure the core handler
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)

    # create a wrapper handler that with buffering
    if capacity > 1:
        raise RuntimeError('_MemoryHandler are not implemented.')
    return handler


class SimpleLogger(LoggerClass):
    """This class inherits ``logging.Logger`` or its derived class and the argument `name` as well as `level`
    will be passed directly to the super class. The keys of `handlerParams` can be 'filename' or 'format'
    which will be used to create a appropriate handler.
    E.g., Create and use SimpleLogger:
    >>> import logutil
    >>> # create a logger named 'log' and write messages to stdout
    >>> logger = logutil.SimpleLogger(name='log')
    >>> logger.info('msg')
        [INFO][2017-01-06 12:54:18,230] - msg
    >>>
    >>> # a file named 'error.log' will be created and write messages to it
    >>> logger = logutil.SimpleLogger(name='log', filename='error.log')
    >>> logger.info('msg')
    """

    def __init__(self, name=__name__, level='INFO', **handlerParams):
        """
        :param name: The name of this logger. `__name__` will be used if it's omitted.
        :param level: The level of this logger. 'INFO' will be assumed if it's omitted.
        :type level: `str` = {"DEBUG"|"INFO"|"WARNING"|"CRITICAL"|"ERROR"}
        :param handlerParams: Keyword arguments which key can be 'filename' or 'format'.
        """
        LoggerClass.__init__(self, name, level)
        self._handlerParams = handlerParams
        self._create_and_attache_handler()

    def _create_and_attache_handler(self):
        handler = make_handler(**self._handlerParams)
        self.addHandler(handler)

    def _del_handlers(self):
        with _lock:
            for h in self.handlers:
                h.close()
                self.removeHandler(h)


class TimedRotatingLogger(SimpleLogger):
    """This class inherits ``logutil.SimpleLogger``. This logger auto rotate file according to argument `suffixFmt`.
    if the keyword argument `filename` is present, a file named `{filename}.%Y-%m-%d` will be created every day
    at midnight by default.
    Note: this logger just maintains one handler, others clients added will be popped out when method
    `._rotate_handler()` be called.
    E.g., Create and use `TimedRotatingLogger`:
    >>> logger = TimedRotatingLogger(filename='error_log', suffixFmt='%S') # rotate file at each second
    >>> logger.info('msg')
    """

    def __init__(self, name=__name__, level='INFO', suffixFmt='%Y-%m-%d', **handlerParams):
        """
        :param name: The name of this logger. `__name__` will be used if it's omitted.
        :param level: The level of this logger. 'INFO' will be assumed if it's omitted.
        :type level: `str`={"DEBUG"|"INFO"|"WARNING"|"CRITICAL"|"ERROR"} or
        :param suffixFmt: It will be used to call time.strftime(suffixFmt) to generate a suffix of full_filename,
             full_filename = filename + '.' + time.strftime(suffixFmt).
             Default value: "%Y-%m-%d", it means that files will be rotated every day at midnight.
        :param handlerParams: Keyword arguments which key can be 'filename' or 'format'.
        """
        # assert handlerParams.get('filename', None), 'filename must be specified when initialize %s' % self.__class__
        self._suffixFmt = suffixFmt
        self._suffix = time.strftime(self._suffixFmt)
        self._baseFilename = handlerParams.get('filename', None)
        self._re_lock = threading.RLock()
        SimpleLogger.__init__(self, name, level, **handlerParams)

    def handle(self, record):
        """overwrite"""
        if self._suffix != time.strftime(self._suffixFmt):
            with self._re_lock:
                if self._suffix != time.strftime(self._suffixFmt):
                    self._suffix = time.strftime(self._suffixFmt)
                    self._rotate_handler()
        LoggerClass.handle(self, record)

    def _rotate_handler(self):
        """Removes the all handlers from this logger, and then rotate filename (new a `logging.FileHandler`
        which be attached to this logger)"""
        with self._re_lock:
            self._del_handlers()
            self._create_and_attache_handler()

    def _create_and_attache_handler(self):
        if self._baseFilename is not None:
            self._handlerParams['filename'] = self._baseFilename + '.' + self._suffix
        SimpleLogger._create_and_attache_handler(self)

