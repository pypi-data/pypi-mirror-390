# This file is placed in the Public Domain.


"non-blocking"


import logging
import os
import queue
import threading
import time
import _thread


class Thread(threading.Thread):

    def __init__(self, func, *args, daemon=True, **kwargs):
        super().__init__(None, self.run, None, (), daemon=daemon)
        self.name = kwargs.get("name", name(func))
        self.queue = queue.Queue()
        self.result = None
        self.starttime = time.time()
        self.stopped = threading.Event()
        self.queue.put((func, args))

    def __iter__(self):
        return self

    def __next__(self):
        yield from dir(self)

    def join(self, timeout=None):
        super().join(timeout)
        return  self.result

    def run(self):
        func, args = self.queue.get()
        self.result = func(*args)


def launch(func, *args, **kwargs):
    thread = Thread(func, *args, **kwargs)
    thread.start()
    return thread


def name(obj, short=False):
    typ = type(obj)
    res = ""
    if "__builtins__" in dir(typ):
        res = obj.__name__
    elif "__self__" in dir(obj):
        res = f"{obj.__self__.__class__.__name__}.{obj.__name__}"
    elif "__class__" in dir(obj) and "__name__" in dir(obj):
        res = f"{obj.__class__.__name__}.{obj.__name__}"
    elif "__class__" in dir(obj):
        res =  f"{obj.__class__.__module__}.{obj.__class__.__name__}"
    elif "__name__" in dir(obj):
        res = f"{obj.__class__.__name__}.{obj.__name__}"
    if short:
        res = res.split(".")[-1]
    return res


def threadhook(args):
    type, value, trace, thread = args
    exc = value.with_traceback(trace)
    if type not in (KeyboardInterrupt, EOFError):
        logging.exception(exc)
    _thread.interrupt_main()


threading.excepthook = threadhook


def __dir__():
    return (
        'Thread',
        'launch',
        'name'
   )
