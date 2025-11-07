# This file is placed in the Public Domain.


"handle events"


import queue
import threading
import time


from .threads import launch


class Event:

    def __init__(self):
        self._ready = threading.Event()
        self._thr = None
        self.channel = ""
        self.ctime = time.time()
        self.orig = ""
        self.result = {}
        self.txt = ""
        self.type = "event"

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        self.result[time.time()] = txt

    def wait(self, timeout=None):
        self._ready.wait()
        if self._thr:
            self._thr.join(timeout)


class Handler:

    def __init__(self):
        self.cbs = {}
        self.queue = queue.Queue()

    def callback(self, event):
        func = self.cbs.get(event.type, None)
        if func:
            name = event.txt and event.txt.split()[0]
            event._thr = launch(func, event, name=name)
        else:
            event.ready()

    def loop(self):
        while True:
            event = self.poll()
            if event is None:
                break
            event.orig = repr(self)
            self.callback(event)

    def poll(self):
        return self.queue.get()

    def put(self, event):
        self.queue.put(event)

    def register(self, type, callback):
        self.cbs[type] = callback

    def start(self):
        launch(self.loop)

    def stop(self):
        self.queue.put(None)


def __dir__():
    return (
        'Event',
        'Handler'
   )
