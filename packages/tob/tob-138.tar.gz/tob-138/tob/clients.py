# This file is placed in the Public Domain.


"clients"


import queue
import threading


from .handler import Handler
from .threads import launch


class Client(Handler):

    def __init__(self):
        Handler.__init__(self)
        self.olock = threading.RLock()
        self.oqueue = queue.Queue()
        self.silent = True
        Fleet.add(self)

    def announce(self, txt):
        if not self.silent:
            self.raw(txt)

    def display(self, event):
        with self.olock:
            for tme in sorted(event.result):
                self.dosay(
                           event.channel,
                           event.result[tme]
                          )

    def dosay(self, channel, txt):
        self.say(channel, txt)

    def raw(self, txt):
        raise NotImplementedError("raw")

    def say(self, channel, txt):
        self.raw(txt)


class Output(Client):

    def output(self):
        while True:
            event = self.oqueue.get()
            if event is None:
                self.oqueue.task_done()
                break
            self.display(event)
            self.oqueue.task_done()

    def start(self):
        launch(self.output)
        super().start()

    def stop(self):
        self.oqueue.put(None)
        super().stop()

    def wait(self):
        self.oqueue.join()


class Fleet:

    clients = {}

    @staticmethod
    def add(client):
        Fleet.clients[repr(client)] = client

    @staticmethod
    def all():
        return Fleet.clients.values()

    @staticmethod
    def announce(txt):
        for client in Fleet.all():
            client.announce(txt)

    @staticmethod
    def display(evt):
        client = Fleet.get(evt.orig)
        client.display(evt)

    @staticmethod
    def get(orig):
        return Fleet.clients.get(orig, None)

    @staticmethod
    def like(orig):
        for origin in Fleet.clients:
            if orig.split()[0] in origin.split()[0]:
                yield origin

    @staticmethod
    def say(orig, channel, txt):
        client = Fleet.get(orig)
        client.say(channel, txt)

    @staticmethod
    def shutdown():
        for client in Fleet.all():
            client.wait()
            client.stop()


def __dir__():
    return (
        'Client',
        'Fleet',
        'Output'
   )
