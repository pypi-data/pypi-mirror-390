# This file is placed in the Public Domain.


"modules"


import os


path = os.path.dirname(__file__)
pkgname = path.split(os.sep)[-1]


def modules():
    if not os.path.exists(path):
        return []
    return sorted([
                   x[:-3].split(".")[-1] for x in os.listdir(path)
                   if x.endswith(".py") and not x.startswith("__")
                  ])


__dir__ = modules
