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
        self.booten_active = False


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
        self.booten_active = True

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

    def pack_cfgword(self, cfgword):
        data = [0xFF] * 4
        data[0] &= ~(0 if cfgword['flashre'] else self.CFGWORD_FLASHRE_MSK)
        data[0] &= ~(0 if cfgword['nvrre'] else self.CFGWORD_NVRRE_MSK)
        data[0] &= ~(0 if cfgword['jtagen'] else self.CFGWORD_JTAGEN_MSK)
        data[0] &= ~(0 if cfgword['debugen'] else self.CFGWORD_DEBUGEN_MSK)
        data[0] &= ~(0 if cfgword['nvrwe'] else self.CFGWORD_NVRWE_MSK)
        data[0] &= ~(0 if cfgword['flashwe'] else self.CFGWORD_FLASHWE_MSK)
        data[0] &= ~(0 if cfgword['bmodedis'] else self.CFGWORD_BMODEDIS_MSK)
        res_str = ("FLASHRE=[%01d] NVRRE=[%01d] JTAGEN=[%01d] DEBUGEN=[%01d] NVRWE=[%01d] FLASHWE=[%01d] BMODEDIS=[%01d]" %
                   (cfgword['flashre'], cfgword['nvrre'], cfgword['jtagen'], cfgword['debugen'], cfgword['nvrwe'], cfgword['flashwe'], cfgword['bmodedis']))
        return (data, res_str)

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
        self.booten_active = False


class K1921VK01T:
    CFGWORD_UFIFBRE_POS = 26
    CFGWORD_UFRE_POS = 25
    CFGWORD_LOCKIFBUF_POS = 24
    CFGWORD_BFIFBRE_POS = 18
    CFGWORD_BFRE_POS = 17
    CFGWORD_LOCKIFBLF_POS = 16
    CFGWORD_PORTNUM_POS = 12
    CFGWORD_PINNUM_POS = 8
    CFGWORD_EXTMEMSEL_POS = 3
    CFGWORD_ENGPIO_POS = 1
    CFGWORD_BOOTFROMIFB_POS = 0
    CFGWORD_UFIFBRE_MSK = (1 << CFGWORD_UFIFBRE_POS)
    CFGWORD_UFRE_MSK = (1 << CFGWORD_UFRE_POS)
    CFGWORD_LOCKIFBUF_MSK = (1 << CFGWORD_LOCKIFBUF_POS)
    CFGWORD_BFIFBRE_MSK = (1 << CFGWORD_BFIFBRE_POS)
    CFGWORD_BFRE_MSK = (1 << CFGWORD_BFRE_POS)
    CFGWORD_LOCKIFBLF_MSK = (1 << CFGWORD_LOCKIFBLF_POS)
    CFGWORD_PORTNUM_MSK = (0xF << CFGWORD_PORTNUM_POS)
    CFGWORD_PINNUM_MSK = (0xF << CFGWORD_PINNUM_POS)
    CFGWORD_EXTMEMSEL_MSK = (3 << CFGWORD_EXTMEMSEL_POS)
    CFGWORD_ENGPIO_MSK = (1 << CFGWORD_ENGPIO_POS)
    CFGWORD_BOOTFROMIFB_MSK = (1 << CFGWORD_BOOTFROMIFB_POS)

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
        self.cfgword = {}
        self.flash[0]['region_nvr'].wr_lock[0] = True
        self.flash[0]['region_nvr'].rd_lock[0] = True
        self.flash[0]['region_main'].rd_lock[0] = True
        self.booten_active = False

    def parse_cfgword(self, data):
        cfgword = {}
        temp = (data[3] << 24) | (data[2] << 16) | (data[1] << 8) | (data[0] << 0)
        cfgword['boot_from_ifb'] = (temp & self.CFGWORD_BOOTFROMIFB_MSK) >> self.CFGWORD_BOOTFROMIFB_POS
        cfgword['en_gpio'] = (temp & self.CFGWORD_ENGPIO_MSK) >> self.CFGWORD_ENGPIO_POS
        cfgword['extmem_sel'] = (temp & self.CFGWORD_EXTMEMSEL_MSK) >> self.CFGWORD_EXTMEMSEL_POS
        cfgword['pinnum'] = (temp & self.CFGWORD_PINNUM_MSK) >> self.CFGWORD_PINNUM_POS
        cfgword['portnum'] = (temp & self.CFGWORD_PORTNUM_MSK) >> self.CFGWORD_PORTNUM_POS
        cfgword['lock_ifb_lf'] = (temp & self.CFGWORD_LOCKIFBLF_MSK) >> self.CFGWORD_LOCKIFBLF_POS
        cfgword['bfre'] = (temp & self.CFGWORD_BFRE_MSK) >> self.CFGWORD_BFRE_POS
        cfgword['bfifbre'] = (temp & self.CFGWORD_BFIFBRE_MSK) >> self.CFGWORD_BFIFBRE_POS
        cfgword['lock_ifb_uf'] = (temp & self.CFGWORD_LOCKIFBUF_MSK) >> self.CFGWORD_LOCKIFBUF_POS
        cfgword['ufre'] = (temp & self.CFGWORD_UFRE_MSK) >> self.CFGWORD_UFRE_POS
        cfgword['ufifbre'] = (temp & self.CFGWORD_UFIFBRE_MSK) >> self.CFGWORD_UFIFBRE_POS
        cfgword['res_str'] = ("BOOTFROMIFB=[%01d] ENGPIO=[%01d] EXTMEMSEL=[%01d] PINNUM=[%02d] PORTNUM=[%02d] LOCKIFBLF=[%01d] BFRE=[%01d] BFIFBRE=[%01d] LOCKIFBUF=[%01d] UFRE=[%01d] UFIFBRE=[%01d]" %
                              (cfgword['boot_from_ifb'], cfgword['en_gpio'], cfgword['extmem_sel'], cfgword['pinnum'], cfgword['portnum'],
                               cfgword['lock_ifb_lf'], cfgword['bfre'], cfgword['bfifbre'], cfgword['lock_ifb_uf'], cfgword['ufre'], cfgword['ufifbre']))
        _bflock = ''
        for b in range(16):
            _bflock = bin(data[4 + b])[2:].zfill(8) + _bflock
        bflock = _bflock[::-1]
        _uflock = ''
        for b in range(32):
            _uflock = bin(data[20 + b])[2:].zfill(8) + _uflock
        uflock = _uflock[::-1]
        cfgword['bflock'] = [1] * self.flash[0]['region_main'].pages
        cfgword['uflock'] = [1] * self.flash[1]['region_main'].pages
        for p in range(len(bflock)):
            cfgword['bflock'][p] = int(bflock[p])
        for p in range(len(uflock)):
            cfgword['uflock'][p] = int(uflock[p])
        return cfgword

    def pack_cfgword(self, cfgword):
        data = [0xFF] * (4 + 16 + 32)
        temp = 0xFFFFFFFF
        temp &= ~(0 if cfgword['boot_from_ifb'] else self.CFGWORD_BOOTFROMIFB_MSK)
        temp &= ~(0 if cfgword['en_gpio'] else self.CFGWORD_ENGPIO_MSK)
        temp = (temp & (~self.CFGWORD_EXTMEMSEL_MSK)) | (cfgword['extmem_sel'] << self.CFGWORD_EXTMEMSEL_POS)
        temp = (temp & (~self.CFGWORD_PINNUM_MSK)) | (cfgword['pinnum'] << self.CFGWORD_PINNUM_POS)
        temp = (temp & (~self.CFGWORD_PORTNUM_MSK)) | (cfgword['portnum'] << self.CFGWORD_PORTNUM_POS)
        temp &= ~(0 if cfgword['lock_ifb_lf'] else self.CFGWORD_LOCKIFBLF_MSK)
        temp &= ~(0 if cfgword['bfre'] else self.CFGWORD_BFRE_MSK)
        temp &= ~(0 if cfgword['bfifbre'] else self.CFGWORD_BFIFBRE_MSK)
        temp &= ~(0 if cfgword['lock_ifb_uf'] else self.CFGWORD_LOCKIFBUF_MSK)
        temp &= ~(0 if cfgword['ufre'] else self.CFGWORD_UFRE_MSK)
        temp &= ~(0 if cfgword['ufifbre'] else self.CFGWORD_UFIFBRE_MSK)
        data[0] = (temp >> 0) & 0xFF
        data[1] = (temp >> 8) & 0xFF
        data[2] = (temp >> 16) & 0xFF
        data[3] = (temp >> 24) & 0xFF
        for p in range(0, len(cfgword['bflock'])):
            data[4 + (p // 8)] &= ~(0 if cfgword['bflock'][p] else (1 << (p % 8)))
        for p in range(0, len(cfgword['uflock'])):
            data[20 + (p // 8)] &= ~(0 if cfgword['uflock'][p] else (1 << (p % 8)))
        res_str = ("BOOTFROMIFB=[%01d] ENGPIO=[%01d] EXTMEMSEL=[%01d] PINNUM=[%02d] PORTNUM=[%02d] LOCKIFBLF=[%01d] BFRE=[%01d] BFIFBRE=[%01d] LOCKIFBUF=[%01d] UFRE=[%01d] UFIFBRE=[%01d]" %
                   (cfgword['boot_from_ifb'], cfgword['en_gpio'], cfgword['extmem_sel'], cfgword['pinnum'], cfgword['portnum'],
                    cfgword['lock_ifb_lf'], cfgword['bfre'], cfgword['bfifbre'], cfgword['lock_ifb_uf'], cfgword['ufre'], cfgword['ufifbre']))
        return (data, res_str)

    def apply_cfgword(self, cfgword):
        self.cfgword = cfgword
        for p in range(self.flash[0]['region_main'].pages):
            self.flash[0]['region_main'].rd_lock[p] = False if cfgword['bfre'] else True
        for p in range(self.flash[0]['region_nvr'].pages):
            self.flash[0]['region_nvr'].rd_lock[p] = False if cfgword['bfifbre'] else True
        for p in range(self.flash[0]['region_main'].pages):
            self.flash[0]['region_main'].wr_lock[p] = False if cfgword['bflock'][p] else True
        for p in range(self.flash[0]['region_nvr'].pages):
            self.flash[0]['region_nvr'].wr_lock[p] = False if cfgword['lock_ifb_lf'] else True
        for p in range(self.flash[1]['region_main'].pages):
            self.flash[1]['region_main'].rd_lock[p] = False if cfgword['ufre'] else True
        for p in range(self.flash[1]['region_nvr'].pages):
            self.flash[1]['region_nvr'].rd_lock[p] = False if cfgword['ufifbre'] else True
        for p in range(self.flash[1]['region_main'].pages):
            self.flash[1]['region_main'].wr_lock[p] = False if cfgword['uflock'][p] else True
        for p in range(self.flash[1]['region_nvr'].pages):
            self.flash[1]['region_nvr'].wr_lock[p] = False if cfgword['lock_ifb_uf'] else True
        # bootloader pages
        self.flash[0]['region_nvr'].wr_lock[0] = True
        self.flash[0]['region_nvr'].rd_lock[0] = True
        self.flash[0]['region_main'].rd_lock[0] = True


db = [K1921VKx(), K1921VK035(), K1921VK028(), K1921VK01T()]


def get_by_chipid(chipid):
    return next((x for x in db if x.chipid == chipid), None)


def get_by_name(name):
    return next((x for x in db if x.name == name), None)
