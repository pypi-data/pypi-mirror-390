# This file is placed in the Public Domain.


"persistence"


import datetime
import json
import os
import pathlib
import threading
import time


from tob.marshal import dump, load
from tob.objects import Object, deleted, fqn, search, update


lock = threading.RLock()


class Workdir:

    wdr = ""


class Cache:

    objs = Object()

    @staticmethod
    def add(path, obj):
        setattr(Cache.objs, path, obj)

    @staticmethod
    def get(path):
        return getattr(Cache.objs, path, None)

    @staticmethod
    def update(path, obj):
        setattr(Cache.objs, path, obj)


def cdir(path):
    pth = pathlib.Path(path)
    pth.parent.mkdir(parents=True, exist_ok=True)


def getpath(obj):
    return store(ident(obj))


def moddir(modname=None):
    return os.path.join(Workdir.wdr, modname or "mods")


def pidname(name):
    assert Workdir.wdr
    return os.path.join(Workdir.wdr, f"{name}.pid")


def skel():
    pth = pathlib.Path(store())
    pth.mkdir(parents=True, exist_ok=True)
    pth = pathlib.Path(moddir())
    pth.mkdir(parents=True, exist_ok=True)
    return str(pth)


def store(fnm=""):
    return os.path.join(Workdir.wdr, "store", fnm)


def types():
    return os.listdir(store())


"find"


def find(type=None, selector=None, removed=False, matching=False):
    if selector is None:
        selector = {}
    for pth in fns(type):
        obj = Cache.get(pth)
        if not obj:
            obj = Object()
            read(obj, pth)
            Cache.add(pth, obj)
        if not removed and deleted(obj):
            continue
        if selector and not search(obj, selector, matching):
            continue
        yield pth, obj


def fns(type=None):
    if type is not None:
        type = type.lower()
    path = store()
    for rootdir, dirs, _files in os.walk(path, topdown=True):
        for dname in dirs:
            if dname.count("-") != 2:
                continue
            ddd = os.path.join(rootdir, dname)
            if type and type not in ddd.lower():
                continue
            for fll in os.listdir(ddd):
                yield os.path.join(ddd, fll)


def fntime(daystr):
    datestr = " ".join(daystr.split(os.sep)[-2:])
    datestr = datestr.replace("_", " ")
    if "." in datestr:
        datestr, rest = datestr.rsplit(".", 1)
    else:
        rest = ""
    timed = time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))
    if rest:
        timed += float("." + rest)
    return float(timed)


def last(obj, selector=None):
    if selector is None:
        selector = {}
    result = sorted(
                    find(fqn(obj), selector),
                    key=lambda x: fntime(x[0])
                   )
    res = ""
    if result:
        inp = result[-1]
        update(obj, inp[-1])
        res = inp[0]
    return res


"disk"


def ident(obj):
    return os.path.join(fqn(obj), *str(datetime.datetime.now()).split())


def read(obj, path):
    with lock:
        with open(path, "r", encoding="utf-8") as fpt:
            try:
                update(obj, load(fpt))
            except json.decoder.JSONDecodeError as ex:
                ex.add_note(path)
                raise ex


def write(obj, path=None):
    with lock:
        if path is None:
            path = getpath(obj)
        cdir(path)
        with open(path, "w", encoding="utf-8") as fpt:
            dump(obj, fpt, indent=4)
        Cache.update(path, obj)
        return path


def __dir__():
    return (
        'Cache',
        'Workdir',
        'cdir',
        'find',
        'fntime',
        'read',
        'skel',
        'types',
        'write'
    )
