#!/user/bin/env python
# coding:utf-8

import os


# -- Misc functions -----------------------------------------------------------
def log_dbg(win, msg):
    win.log_dbg(msg)


def log_info(win, msg):
    win.log_info(msg)


def log_warn(win, msg):
    win.log_warn(msg)


def log_err(win, msg):
    win.log_err(msg)


def log_crit(win, msg):
    win.log_dbg(msg)


# -- API --------------------------------------------------------------------
def init(win, **kwargs):
    log_dbg(win, "%s->%s()" % (os.path.basename(__file__), win.whoami()))
    log_dbg(win, kwargs)
    log_info(win, "Открываю порт %s %s" % (kwargs['port'], kwargs['baud']))
    # return {'chipid': '0x5A298FE1', 'cpuid': '0xDEADBEEF', 'bootver': '0.1'}
    # return {'chipid': '0x3ABF2FD1', 'cpuid': '0xDEADBEEF', 'bootver': '0.1'}
    return {'chipid': '0x00000000', 'cpuid': '0xDEADBEEF', 'bootver': '0.1'}


def deinit(win, **kwargs):
    log_dbg(win, "%s->%s()" % (os.path.basename(__file__), win.whoami()))
    log_dbg(win, kwargs)
    log_info(win, "Закрываю порт")
    return True


def write(win, **kwargs):
    log_dbg(win, "%s->%s()" % (os.path.basename(__file__), win.whoami()))
    log_dbg(win, kwargs)
    return True
