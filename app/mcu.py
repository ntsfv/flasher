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
        self.cpuid = '0xFFFFFFFF'
        self.name = 'k1921vkx'
        self.name_ru = 'К1921ВКххх'
        self.bootver = '0.0'
        self.flash = [{'name': 'flash0',
                       'region_main': Flash(size=(64 * K), pages=64),
                       'region_nvr': Flash(size=(4 * K), pages=4)},
                      {'name': 'flash1',
                       'region_main': Flash(size=(32 * K), pages=16),
                       'region_nvr': Flash(size=(8 * K), pages=4)}]


class K1921VK035:
    CFGWORD_FLASHRE_POS = 7
    CFGWORD_NVRRE_POS = 6
    CFGWORD_BMODEDIS_POS = 4
    CFGWORD_FLASHWE_POS = 3
    CFGWORD_NVRWE_POS = 2
    CFGWORD_DEBUGEN_POS = 1
    CFGWORD_JTAGEN_POS = 0
    CFGWORD_FLASHRE_MSK = 1 << CFGWORD_FLASHRE_POS
    CFGWORD_NVRRE_MSK = 1 << CFGWORD_NVRRE_POS
    CFGWORD_BMODEDIS_MSK = 1 << CFGWORD_BMODEDIS_POS
    CFGWORD_FLASHWE_MSK = 1 << CFGWORD_FLASHWE_POS
    CFGWORD_NVRWE_MSK = 1 << CFGWORD_NVRWE_POS
    CFGWORD_DEBUGEN_MSK = 1 << CFGWORD_DEBUGEN_POS
    CFGWORD_JTAGEN_MSK = 1 << CFGWORD_JTAGEN_POS

    def __init__(self):
        self.chipid = '0x5A298FE1'
        self.name = 'k1921vk035'
        self.name_ru = 'К1921ВК035'
        self.cpuid = '0xFFFFFFFF'
        self.bootver = '0.0'
        self.flash = [{'name': 'mflash',
                       'region_main': Flash(size=(64 * K), pages=64),
                       'region_nvr': Flash(size=(4 * K), pages=4)}]
        self.cfgword = {}
        self.flash[0]['region_nvr'].wr_lock[0:3] = [True] * 3
        self.flash[0]['region_nvr'].rd_lock[0:3] = [True] * 3

    def parse_cfgword(self, data):
        cfgword = {}
        cfgword['flashre'] = (data[0] & self.CFGWORD_FLASHRE_MSK) >> self.CFGWORD_FLASHRE_POS
        cfgword['nvrre'] = (data[0] & self.CFGWORD_NVRRE_MSK) >> self.CFGWORD_NVRRE_POS
        cfgword['jtagen'] = (data[0] & self.CFGWORD_JTAGEN_MSK) >> self.CFGWORD_JTAGEN_POS
        cfgword['debugen'] = (data[0] & self.CFGWORD_DEBUGEN_MSK) >> self.CFGWORD_DEBUGEN_POS
        cfgword['nvrwe'] = (data[0] & self.CFGWORD_NVRWE_MSK) >> self.CFGWORD_NVRWE_POS
        cfgword['flashwe'] = (data[0] & self.CFGWORD_FLASHWE_MSK) >> self.CFGWORD_FLASHWE_POS
        cfgword['bmodedis'] = (data[0] & self.CFGWORD_BMODEDIS_MSK) >> self.CFGWORD_BMODEDIS_POS
        cfgword['res_str'] = ("FLASHRE=[%01d] NVRRE=[%01d] JTAGEN=[%01d] DEBUGEN=[%01d] NVRWE=[%01d] FLASHWE=[%01d] BMODEDIS=[%01d]" %
                              (cfgword['flashre'], cfgword['nvrre'], cfgword['jtagen'], cfgword['debugen'], cfgword['nvrwe'], cfgword['flashwe'], cfgword['bmodedis']))
        return cfgword

    def apply_cfgword(self, cfgword):
        self.cfgword = cfgword
        for p in range(self.flash[0]['region_main'].pages):
            self.flash[0]['region_main'].rd_lock[p] = False if cfgword['flashre'] else True
        for p in range(self.flash[0]['region_nvr'].pages):
            self.flash[0]['region_nvr'].rd_lock[p] = False if cfgword['nvrre'] else True
        for p in range(self.flash[0]['region_main'].pages):
            self.flash[0]['region_main'].wr_lock[p] = False if cfgword['flashwe'] else True
        for p in range(self.flash[0]['region_nvr'].pages):
            self.flash[0]['region_nvr'].wr_lock[p] = False if cfgword['nvrwe'] else True
        # bootloader pages
        self.flash[0]['region_nvr'].wr_lock[0:3] = [True] * 3
        self.flash[0]['region_nvr'].rd_lock[0:3] = [True] * 3


class K1921VK028:
    def __init__(self):
        self.chipid = '0x3ABF2FD1'
        self.name = 'k1921vk028'
        self.name_ru = 'К1921ВК028'
        self.cpuid = '0xFFFFFFFF'
        self.bootver = '0.0'
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
        self.cpuid = '0xFFFFFFFF'
        self.bootver = '0.0'
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
