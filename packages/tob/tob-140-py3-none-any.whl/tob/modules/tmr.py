# This file is placed in the Public Domain.


"timers"


import datetime
import logging
import random
import re
import time


from tob.clients import Fleet
from tob.methods import getpath
from tob.objects import Object, items
from tob.persist import last, write
from tob.repeats import Timed
from tob.utility import elapsed, extract_date


def init():
    Timers.path = last(Timers.timers) or getpath(Timers.timers)
    delete = []
    for tme, args in items(Timers.timers):
        orig, channel, txt = args
        for origin in Fleet.like(orig):
            if not origin:
                continue
            diff = float(tme) - time.time()
            if diff > 0:
                timer = Timed(diff, Fleet.say, origin, channel, txt)
                timer.start()
            else:
                delete.append(tme)
    for tme in delete:
        Timers.delete(tme)
    write(Timers.timers, Timers.path)
    logging.warning("%s timers", len(Timers.timers))


class NoDate(Exception):

    pass


class Timers:

    path = ""
    timers = Object()

    @staticmethod
    def add(tme, orig, channel,  txt):
        setattr(Timers.timers, tme, (orig, channel, txt))

    @staticmethod
    def delete(tme):
        delattr(Timers.timers, tme)


def get_day(daystr):
    day = None
    month = None
    yea = None
    try:
        ymdre = re.search(r'(\d+)-(\d+)-(\d+)', daystr)
        if ymdre:
            (day, month, yea) = ymdre.groups()
    except ValueError:
        try:
            ymre = re.search(r'(\d+)-(\d+)', daystr)
            if ymre:
                (day, month) = ymre.groups()
                yea = time.strftime("%Y", time.localtime())
        except Exception as ex:
            raise NoDate(daystr) from ex
    if day:
        day = int(day)
        month = int(month)
        yea = int(yea)
        date = f"{day} {MONTHS[month]} {yea}"
        return time.mktime(time.strptime(date, r"%d %b %Y"))
    raise NoDate(daystr)


def get_hour(daystr):
    try:
        hmsre = re.search(r'(\d+):(\d+):(\d+)', str(daystr))
        hours = 60 * 60 * (int(hmsre.group(1)))
        hoursmin = hours  + int(hmsre.group(2)) * 60
        hmsres = hoursmin + int(hmsre.group(3))
    except AttributeError:
        pass
    except ValueError:
        pass
    try:
        hmre = re.search(r'(\d+):(\d+)', str(daystr))
        hours = 60 * 60 * (int(hmre.group(1)))
        hmsres = hours + int(hmre.group(2)) * 60
    except AttributeError:
        return 0
    except ValueError:
        return 0
    return hmsres


def get_time(txt):
    try:
        target = get_day(txt)
    except NoDate:
        target = to_day(today())
    hour =  get_hour(txt)
    if hour:
        target += hour
    return target


def parse_time(txt):
    seconds = 0
    target = 0
    txt = str(txt)
    for word in txt.split():
        if word.startswith("+"):
            seconds = int(word[1:])
            return time.time() + seconds
        if word.startswith("-"):
            seconds = int(word[1:])
            return time.time() - seconds
    if not target:
        try:
            target = get_day(txt)
        except NoDate:
            target = to_day(today())
        hour =  get_hour(txt)
        if hour:
            target += hour
    return target


def to_day(daystr):
    previous = ""
    line = ""
    daystr = str(daystr)
    res = None
    for word in daystr.split():
        line = previous + " " + word
        previous = word
        try:
            res = extract_date(line.strip())
            break
        except ValueError:
            res = None
        line = ""
    return res


def today():
    return str(datetime.datetime.today()).split()[0]


def tmr(event):
    result = ""
    if not event.rest:
        nmr = 0
        for tme, txt in items(Timers.timers):
            lap = float(tme) - time.time()
            if lap > 0:
                event.reply(f'{nmr} {" ".join(txt)} {elapsed(lap)}')
                nmr += 1
        if not nmr:
            event.reply("no timers.")
        return result
    seconds = 0
    line = ""
    for word in event.args:
        if word.startswith("+"):
            try:
                seconds = int(word[1:])
            except (ValueError, IndexError):
                event.reply(f"{seconds} is not an integer")
                return result
        else:
            line += word + " "
    if seconds:
        target = time.time() + seconds
    else:
        try:
            target = get_day(event.rest)
        except NoDate:
            target = to_day(today())
        hour =  get_hour(event.rest)
        if hour:
            target += hour
    target += random.random() 
    if not target or time.time() > target:
        event.reply("already passed given time.")
        return result
    diff = target - time.time()
    txt = " ".join(event.args[1:])
    Timers.add(target, event.orig, event.channel, txt)
    write(Timers.timers, Timers.path)
    timer = Timed(diff, Fleet.say, event.orig, event.channel, txt)
    timer.start()
    event.reply("ok " +  elapsed(diff))


"data"


MONTHS = [
    'Bo',
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec'
]
