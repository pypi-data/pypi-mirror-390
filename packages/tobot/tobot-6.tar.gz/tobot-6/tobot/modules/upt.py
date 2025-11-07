# This file is placed in the Public Domain.


"uptime"


import time


from tobot.runtime import STARTTIME
from tobot.utility import elapsed


def upt(event):
    event.reply(elapsed(time.time()-STARTTIME))
