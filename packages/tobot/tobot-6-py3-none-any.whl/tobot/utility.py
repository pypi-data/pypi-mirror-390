# This file is placed in the Public Domain.


"utilities"


import hashlib
import time


FORMATS = [
    "%Y-%M-%D %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d-%m",
    "%m-%d"
]


def elapsed(seconds, short=True):
    txt = ""
    nsec = float(seconds)
    if nsec < 1:
        return f"{nsec:.2f}s"
    yea     = 365 * 24 * 60 * 60
    week    = 7 * 24 * 60 * 60
    nday    = 24 * 60 * 60
    hour    = 60 * 60
    minute  = 60
    yeas    = int(nsec / yea)
    nsec   -= yeas * yea
    weeks   = int(nsec / week)
    nsec   -= weeks * week
    nrdays  = int(nsec / nday)
    nsec   -= nrdays * nday
    hours   = int(nsec / hour)
    nsec   -= hours * hour
    minutes = int(nsec / minute)
    nsec   -= int(minute * minutes)
    sec     = int(nsec)
    if yeas:
        txt += f"{yeas}y"
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += f"{nrdays}d"
    if short and txt:
        return txt.strip()
    if hours:
        txt += f"{hours}h"
    if minutes:
        txt += f"{minutes}m"
    if sec:
        txt += f"{sec}s"
    txt = txt.strip()
    return txt


def extract_date(daystr):
    daystr = daystr.encode('utf-8', 'replace').decode("utf-8")
    res = time.time()
    for fmat in FORMATS:
        try:
            res = time.mktime(time.strptime(daystr, fmat))
            break
        except ValueError:
            pass
    return res


def md5sum(path):
    with open(path, "r", encoding="utf-8") as file:
        txt = file.read().encode("utf-8")
        return hashlib.md5(txt).hexdigest()


def spl(txt):
    if txt.find(",") == -1:
        return []
    try:
        result = txt.split(",")
    except (TypeError, ValueError):
        result = []
    return [x for x in result if x]


def __dir__():
    return (
        'elapsed',
        'extract_date',
        'md5sum',
        'spl'
   )
