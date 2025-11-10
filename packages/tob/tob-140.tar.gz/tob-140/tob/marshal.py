# This file is placed in the Public Domain.


"serializer"


import json


class Encoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, dict):
            return o.items()
        if isinstance(o, list):
            return iter(o)
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            try:
                return vars(o)
            except TypeError:
                return repr(o)


def dump(*args, **kw):
    kw["cls"] = Encoder
    return json.dump(*args, **kw)


def dumps(*args, **kw):
    kw["cls"] = Encoder
    return json.dumps(*args, **kw)


def load(s, *args, **kw):
    return json.load(s, *args, **kw)


def loads(s, *args, **kw):
    return json.loads(s, *args, **kw)


def __dir__():
    return (
       'dump',
       'dumps',
       'load',
       'loads'
    )
