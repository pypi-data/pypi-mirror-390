# This file is placed in the Public Domain.


"write your own commands"


import importlib
import importlib.util
import inspect
import os
import sys


from typing import Callable


from .clients import Fleet
from .methods import parse
from .threads import launch


class Mods:

    dirs: dict[str, str] = {}
    ignore: list[str] = []

    @staticmethod
    def add(name, path=None):
        if path is None:
            path = name
        Mods.dirs[name] = path


class Commands:

    cmds: dict[str, Callable] = {}
    names: dict[str, str] = {}

    @staticmethod
    def add(*args):
        for func in args:
            name = func.__name__
            Commands.cmds[name] = func
            Commands.names[name] = func.__module__.split(".")[-1]

    @staticmethod
    def get(cmd):
        return Commands.cmds.get(cmd, None)


def command(evt):
    parse(evt, evt.text)
    func = Commands.get(evt.cmd)
    if func:
        func(evt)
        Fleet.display(evt)
    evt.ready()


def importer(name, pth):
    if not os.path.exists(pth):
        return
    spec = importlib.util.spec_from_file_location(name, pth)
    if not spec or not spec.loader:
        return
    mod = importlib.util.module_from_spec(spec)
    if not mod:
        return
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def inits(names):
    modz = []
    for name in names:
        if name in Mods.ignore:
            continue
        for modname, path in Mods.dirs.items():
            modpath = os.path.join(path, name + ".py")
            if not os.path.exists(modpath):
                continue
            pkgname = path.split(os.sep)[-1]
            mname = ".".join((pkgname, name))
            mod = importer(mname, modpath)
            if mod and "init" in dir(mod):
                thr = launch(mod.init)
                modz.append((mod, thr))
    return modz


def modules():
    mods = []
    for name, path in Mods.dirs.items():
        if name in Mods.ignore:
            continue
        if not os.path.exists(path):
            continue
        mods.extend([
            x[:-3] for x in os.listdir(path)
            if x.endswith(".py") and not x.startswith("__") and x not in Mods.ignore
        ])
    return sorted(mods)


def scan(module):
    for key, cmdz in inspect.getmembers(module, inspect.isfunction):
        if key.startswith("cb"):
            continue
        if 'event' in inspect.signature(cmdz).parameters:
            Commands.add(cmdz)


def scanner(names=[]):
    if not names:
        names = modules()
    mods = []
    for name in names:
        if name in Mods.ignore:
            continue
        for modname, path in Mods.dirs.items():
            modpath = os.path.join(path, name + ".py")
            if not os.path.exists(modpath):
                continue
            pkgname = path.split(os.sep)[-1] or path
            mname = ".".join((pkgname, name))
            mod = importer(mname, modpath)
            if mod:
                mods.append(mod)
                scan(mod)
    return mods


def __dir__():
    return (
        'Comamnds',
        'Mods',
        'command',
        'importer',
        'modules',
        'scan',
        'scanner'
    )
