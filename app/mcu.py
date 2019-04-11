#!/user/bin/env python
# coding:utf-8

K = 1024
M = 1024 * K


class Flash:
    def __init__(self, size, pages):
        self.size = size
        self.pages = pages
        self.page_size = size // pages
        self.wr_lock = [False] * pages
        self.rd_lock = [False] * pages


class K1921VKx:
    def __init__(self):
        self.chipid = '0xFFFFFFFF'
        self.name = 'k1921vkx'
        self.name_ru = 'К1921ВКххх'
        self.flash = [{'name': 'flash0',
                       'region_main': Flash(size=(64 * K), pages=64),
                       'region_nvr': Flash(size=(4 * K), pages=4)},
                      {'name': 'flash1',
                       'region_main': Flash(size=(32 * K), pages=16),
                       'region_nvr': Flash(size=(8 * K), pages=4)}]


class K1921VK035:
    def __init__(self):
        self.chipid = '0x5A298FE1'
        self.name = 'k1921vk035'
        self.name_ru = 'К1921ВК035'
        self.flash = [{'name': 'mflash',
                       'region_main': Flash(size=(64 * K), pages=64),
                       'region_nvr': Flash(size=(4 * K), pages=4)}]


class K1921VK028:
    def __init__(self):
        self.chipid = '0x3ABF2FD1'
        self.name = 'k1921vk028'
        self.name_ru = 'К1921ВК028'
        self.flash = [{'name': 'mflash',
                       'region_main': Flash(size=(2 * M), pages=128),
                       'region_nvr': Flash(size=(64 * K), pages=4)},
                      {'name': 'bflash',
                       'region_main': Flash(size=(512 * K), pages=128),
                       'region_nvr': Flash(size=(16 * K), pages=4)}]


class K1921VK01T:
    def __init__(self):
        self.chipid = '0x00000000'
        self.name = 'k1921vk01t'
        self.name_ru = 'К1921ВК01Т'
        self.flash = [{'name': 'bootflash',
                       'region_main': Flash(size=(1 * M), pages=128),
                       'region_nvr': Flash(size=(8 * K), pages=1)},
                      {'name': 'userflash',
                       'region_main': Flash(size=(64 * K), pages=256),
                       'region_nvr': Flash(size=512, pages=2)}]


db = [K1921VKx(), K1921VK035(), K1921VK028(), K1921VK01T()]


def get_by_chipid(chipid):
    return next((x for x in db if x.chipid == chipid), None)


def get_by_name(name):
    return next((x for x in db if x.name == name), None)
