# This file is placed in the Public Domain.


"find"


import time


from tob.methods import fmt
from tob.persist import find, fntime
from tob.storage import types
from tob.utility import elapsed


def fn(event):
    if not event.rest:
        res = sorted([x.split('.')[-1].lower() for x in types()])
        if res:
            event.reply(",".join(res))
        else:
            event.reply("no data yet.")
        return
    otype = event.args[0]
    nmr = 0
    for fnm, obj in list(find(otype, event.gets)):
        event.reply(f"{nmr} {fmt(obj)} {elapsed(time.time()-fntime(fnm))}")
        nmr += 1
    if not nmr:
        event.reply("no result")
