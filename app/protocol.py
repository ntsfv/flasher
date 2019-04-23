#!/user/bin/env python
# coding:utf-8

import os


LogId = {
    "DEVICE": "\t@D: ",
    "HOST": "@H: ",
    "PROG": "",
}

SignCode = {
    "DEVICE": 0x7EA3,
    "HOST": 0x5C81,
}

CmdCode = {
    # Get commands
    "GET_INFO": 0x35,
    "GET_CFGWORD": 0x3A,
    # Set commands
    "SET_CFGWORD": 0x65,
    # Write commands
    "WRITE_PAGE": 0x9A,
    # Read commands
    "READ_PAGE": 0xA5,
    # Erase commands
    "ERASE_FULL": 0xC5,
    "ERASE_PAGE": 0xCA,
    # Misc
    "NONE": 0x00,
    "EXIT_BOOTLOADER": 0xF5,
    "MSG": 0xFA
}

MsgCode = {
    "NONE": 0,
    "ERR_CMD": 1,
    "ERR_CRC": 2,
    "READY": 3,
    "OK": 4,
    "FAIL": 5
}


# -- Misc functions -----------------------------------------------------------
def dictKey(mydict, dict_value):
    return list(mydict.keys())[list(mydict.values()).index(dict_value)]


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

# -- Classes ----------------------------------------------------------------


# -- API --------------------------------------------------------------------
def save_bin(win, name, data):
    log_dbg(win, "Save %0d bytes of data to %s" % (len(data), name))
    binfile = open(name, "wb")
    binfile.write(bytes(data))
    binfile.close()


def open_bin(win, name):
    binfile = open(name, "rb")
    data = []
    while True:
        current_byte = binfile.read(1)
        if (not current_byte):
            break
        data += [ord(current_byte)]
    binfile.close()
    log_dbg(win, "Loaded %0d bytes of data from %s" % (len(data), name))
    return data


def init(win, **kwargs):
    log_dbg(win, "%s->%s()" % (os.path.basename(__file__), win.whoami()))
    log_dbg(win, kwargs)
    return {'chipid': '0x5A298FE1', 'cpuid': '0xDEADBEEF', 'bootver': '0.1'}
    # return {'chipid': '0x3ABF2FD1', 'cpuid': '0xDEADBEEF', 'bootver': '0.1'}
    # return {'chipid': '0x00000000', 'cpuid': '0xDEADBEEF', 'bootver': '0.1'}


def deinit(win, **kwargs):
    log_dbg(win, "%s->%s()" % (os.path.basename(__file__), win.whoami()))
    log_dbg(win, kwargs)
    log_info(win, "Закрываю порт")
    return True


def write(win, **kwargs):
    log_dbg(win, "%s->%s()" % (os.path.basename(__file__), win.whoami()))
    log_dbg(win, kwargs)
    return True


def erase(win, **kwargs):
    log_dbg(win, "%s->%s()" % (os.path.basename(__file__), win.whoami()))
    log_dbg(win, kwargs)
    return True


def read(win, **kwargs):
    log_dbg(win, "%s->%s()" % (os.path.basename(__file__), win.whoami()))
    log_dbg(win, kwargs)
    return True
