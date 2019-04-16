#!/user/bin/env python
# coding:utf-8

from k1921vkx_flasher import log_info


def init(port, baud):
    log_info("Открываю порт %s %s" % (port, baud))
    # return {'chipid': '0x5A298FE1', 'cpuid': '0xDEADBEEF', 'bootver': '0.1'}
    # return {'chipid': '0x3ABF2FD1', 'cpuid': '0xDEADBEEF', 'bootver': '0.1'}
    return {'chipid': '0x00000000', 'cpuid': '0xDEADBEEF', 'bootver': '0.1'}


def deinit():
    log_info("Закрываю порт")
    return True
