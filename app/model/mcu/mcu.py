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


class MCU:
    def __init__(self):
        self.cpuid = "0xFFFFFFF0"
        self.bootver = "0.0"


class K1921Vx(MCU):
    def __init__(self):
        super().__init__()
        self.chipid = "0xFFFFFFF0"
        self.name = "k1921"
        self.name_ru = "К1921Вxххх"
        self.flash_base_address = 0x0
        self.flash = [
            {
                "name": "flash0",
                "region_main": Flash(size=(64 * K), pages=64),
                "region_nvr": Flash(size=(4 * K), pages=4),
                "bootflash_end_address": 0x0,
                "lockable": True,
            },
            {
                "name": "flash1",
                "region_main": Flash(size=(32 * K), pages=16),
                "region_nvr": Flash(size=(8 * K), pages=4),
                "bootflash_end_address": 0x0,
                "lockable": True,
            },
        ]
        self.booten_active = False


class K1921VG7T(MCU):
    CFGWORD_FLASHWE_POS = 0
    CFGWORD_JTAGEN_POS = 2
    CFGWORD_FLASHWE_MSK = 1 << CFGWORD_FLASHWE_POS
    CFGWORD_JTAGEN_MSK = 1 << CFGWORD_JTAGEN_POS

    def __init__(self):
        super().__init__()
        self.chipid = "0x04E4C400"
        self.name = "k1921vg7t"
        self.name_ru = "К1921ВГ7Т"
        self.flash_base_address = 0x00000000
        self.flash = [
            {
                "name": "flash",
                "region_main": Flash(size=(512 * K), pages=512),
                "region_nvr": Flash(size=(16 * K), pages=16),
                "bootflash_end_address": 0x2000,
                "base_address": 0x00000000,
                "start_page_main": 8,
                "start_page_nvr": 0,
                "lockable": False,
            }
        ]
        self.cfgword = {}
        self.flash[0]["region_nvr"].wr_lock[0:3] = [True] * 3
        self.flash[0]["region_nvr"].rd_lock[0:3] = [True] * 3
        self.booten_active = True

    def parse_cfgword(self, data):
        cfgword = {}
        cfgword["jtagen"] = (
            data[0] & self.CFGWORD_JTAGEN_MSK
        ) >> self.CFGWORD_JTAGEN_POS
        cfgword["flashwe"] = (
            data[0] & self.CFGWORD_FLASHWE_MSK
        ) >> self.CFGWORD_FLASHWE_POS
        cfgword["res_str"] = "JTAGEN=[%01d] FLASHWE=[%01d]" % (
            cfgword["jtagen"],
            cfgword["flashwe"],
        )
        print(data[0])
        return cfgword

    def pack_cfgword(self, cfgword):
        data = [0xFF] * 4
        data[0] = 0
        if cfgword["jtagen"]:
            data[0] |= 1 << self.CFGWORD_JTAGEN_POS
            data[1] |= 1 << self.CFGWORD_JTAGEN_POS
            data[2] |= 1 << self.CFGWORD_JTAGEN_POS
            data[3] |= 1 << self.CFGWORD_JTAGEN_POS
        if cfgword["flashwe"]:
            data[0] |= 1 << self.CFGWORD_FLASHWE_POS
            data[1] |= 1 << self.CFGWORD_FLASHWE_POS
            data[2] |= 1 << self.CFGWORD_FLASHWE_POS
            data[3] |= 1 << self.CFGWORD_FLASHWE_POS
        print(f"PACKED CFGWORD = {data}")
        res_str = "JTAGEN=[%01d] FLASHWE=[%01d]" % (
            cfgword["flashwe"],
            cfgword["jtagen"],
        )
        return (data, res_str)

    def apply_cfgword(self, cfgword):
        self.cfgword = cfgword
        for p in range(self.flash[0]["region_main"].pages):
            self.flash[0]["region_main"].wr_lock[p] = (
                False if cfgword["flashwe"] else True
            )
        for p in range(self.flash[0]["region_nvr"].pages):
            self.flash[0]["region_nvr"].wr_lock[p] = (
                False if cfgword["flashwe"] else True
            )
        # bootloader pages
        self.flash[0]["region_nvr"].wr_lock[0:3] = [True] * 3
        self.flash[0]["region_nvr"].rd_lock[0:3] = [True] * 3


class K1921VG5T(MCU):
    CFGWORD_FLASHWE_POS = 0
    CFGWORD_JTAGEN_POS = 2
    CFGWORD_FLASHWE_MSK = 1 << CFGWORD_FLASHWE_POS
    CFGWORD_JTAGEN_MSK = 1 << CFGWORD_JTAGEN_POS

    def __init__(self):
        super().__init__()
        self.chipid = "0x04E4C300"
        self.name = "k1921vg5t"
        self.name_ru = "К1921ВГ5Т"
        self.flash_base_address = 0x00000000
        self.flash = [
            {
                "name": "flash",
                "region_main": Flash(size=(512 * K), pages=512),
                "region_nvr": Flash(size=(16 * K), pages=16),
                "bootflash_end_address": 0x2000,
                "base_address": 0x00000000,
                "start_page_main": 8,
                "start_page_nvr": 0,
                "lockable": False,
            }
        ]
        self.cfgword = {}
        self.flash[0]["region_nvr"].wr_lock[0:3] = [True] * 3
        self.flash[0]["region_nvr"].rd_lock[0:3] = [True] * 3
        self.booten_active = True

    def parse_cfgword(self, data):
        cfgword = {}
        cfgword["jtagen"] = (
            data[0] & self.CFGWORD_JTAGEN_MSK
        ) >> self.CFGWORD_JTAGEN_POS
        cfgword["flashwe"] = (
            data[0] & self.CFGWORD_FLASHWE_MSK
        ) >> self.CFGWORD_FLASHWE_POS
        cfgword["res_str"] = "JTAGEN=[%01d] FLASHWE=[%01d]" % (
            cfgword["jtagen"],
            cfgword["flashwe"],
        )
        print(data[0])
        return cfgword

    def pack_cfgword(self, cfgword):
        data = [0xFF] * 4
        data[0] = 0
        if cfgword["jtagen"]:
            data[0] |= 1 << self.CFGWORD_JTAGEN_POS
            data[1] |= 1 << self.CFGWORD_JTAGEN_POS
            data[2] |= 1 << self.CFGWORD_JTAGEN_POS
            data[3] |= 1 << self.CFGWORD_JTAGEN_POS
        if cfgword["flashwe"]:
            data[0] |= 1 << self.CFGWORD_FLASHWE_POS
            data[1] |= 1 << self.CFGWORD_FLASHWE_POS
            data[2] |= 1 << self.CFGWORD_FLASHWE_POS
            data[3] |= 1 << self.CFGWORD_FLASHWE_POS
        print(f"PACKED CFGWORD = {data}")
        res_str = "JTAGEN=[%01d] FLASHWE=[%01d]" % (
            cfgword["flashwe"],
            cfgword["jtagen"],
        )
        return (data, res_str)

    def apply_cfgword(self, cfgword):
        self.cfgword = cfgword
        for p in range(self.flash[0]["region_main"].pages):
            self.flash[0]["region_main"].wr_lock[p] = (
                False if cfgword["flashwe"] else True
            )
        for p in range(self.flash[0]["region_nvr"].pages):
            self.flash[0]["region_nvr"].wr_lock[p] = (
                False if cfgword["flashwe"] else True
            )
        # bootloader pages
        self.flash[0]["region_nvr"].wr_lock[0:3] = [True] * 3
        self.flash[0]["region_nvr"].rd_lock[0:3] = [True] * 3


class K1921VG3T(MCU):
    CFGWORD_FLASHWE_POS = 0
    CFGWORD_JTAGEN_POS = 2
    CFGWORD_FLASHWE_MSK = 1 << CFGWORD_FLASHWE_POS
    CFGWORD_JTAGEN_MSK = 1 << CFGWORD_JTAGEN_POS

    def __init__(self):
        super().__init__()
        self.chipid = "0x04E4C200"
        self.name = "k1921vg3t"
        self.name_ru = "К1921ВГ3Т"
        self.flash_base_address = 0x00000000
        self.flash = [
            {
                "name": "flash",
                "region_main": Flash(size=(1024 * K), pages=512),
                "region_nvr": Flash(size=(32 * K), pages=16),
                "bootflash_end_address": 0x2000,
                "base_address": 0x00000000,
                "start_page_main": 4,
                "start_page_nvr": 0,
                "lockable": False,
            }
        ]
        self.cfgword = {}
        self.flash[0]["region_nvr"].wr_lock[0:3] = [True] * 3
        self.flash[0]["region_nvr"].rd_lock[0:3] = [True] * 3
        self.booten_active = True

    def parse_cfgword(self, data):
        cfgword = {}
        cfgword["jtagen"] = (
            data[0] & self.CFGWORD_JTAGEN_MSK
        ) >> self.CFGWORD_JTAGEN_POS
        cfgword["flashwe"] = (
            data[0] & self.CFGWORD_FLASHWE_MSK
        ) >> self.CFGWORD_FLASHWE_POS
        cfgword["res_str"] = "JTAGEN=[%01d] FLASHWE=[%01d]" % (
            cfgword["jtagen"],
            cfgword["flashwe"],
        )
        print(data[0])
        return cfgword

    def pack_cfgword(self, cfgword):
        data = [0xFF] * 4
        data[0] = 0
        if cfgword["jtagen"]:
            data[0] |= 1 << self.CFGWORD_JTAGEN_POS
            data[1] |= 1 << self.CFGWORD_JTAGEN_POS
            data[2] |= 1 << self.CFGWORD_JTAGEN_POS
            data[3] |= 1 << self.CFGWORD_JTAGEN_POS
        if cfgword["flashwe"]:
            data[0] |= 1 << self.CFGWORD_FLASHWE_POS
            data[1] |= 1 << self.CFGWORD_FLASHWE_POS
            data[2] |= 1 << self.CFGWORD_FLASHWE_POS
            data[3] |= 1 << self.CFGWORD_FLASHWE_POS
        print(f"PACKED CFGWORD = {data}")
        res_str = "JTAGEN=[%01d] FLASHWE=[%01d]" % (
            cfgword["flashwe"],
            cfgword["jtagen"],
        )
        return (data, res_str)

    def apply_cfgword(self, cfgword):
        self.cfgword = cfgword
        print(cfgword)
        for p in range(self.flash[0]["region_main"].pages):
            self.flash[0]["region_main"].wr_lock[p] = (
                False if cfgword["flashwe"] else True
            )
        for p in range(self.flash[0]["region_nvr"].pages):
            self.flash[0]["region_nvr"].wr_lock[p] = (
                False if cfgword["flashwe"] else True
            )
        # bootloader pages
        self.flash[0]["region_nvr"].wr_lock[0:3] = [True] * 3
        self.flash[0]["region_nvr"].rd_lock[0:3] = [True] * 3


class K1921VG1T(MCU):
    CFGWORD_FLASHWE_POS = 0
    CFGWORD_JTAGEN_POS = 2
    CFGWORD_FLASHWE_MSK = 1 << CFGWORD_FLASHWE_POS
    CFGWORD_JTAGEN_MSK = 1 << CFGWORD_JTAGEN_POS

    def __init__(self):
        super().__init__()
        self.chipid = "0x04E4C100"
        self.name = "k1921vg1t"
        self.name_ru = "К1921ВГ1Т"
        self.flash_base_address = 0x00000000
        self.flash = [
            {
                "name": "flash",
                "region_main": Flash(size=(4096 * K), pages=2048),
                "region_nvr": Flash(size=(128 * K), pages=64),
                "bootflash_end_address": 0x2000,
                "base_address": 0x00000000,
                "start_page_main": 4,
                "start_page_nvr": 0,
                "lockable": False,
            }
        ]
        self.cfgword = {}
        self.flash[0]["region_nvr"].wr_lock[0:3] = [True] * 3
        self.flash[0]["region_nvr"].rd_lock[0:3] = [True] * 3
        self.booten_active = True

    def parse_cfgword(self, data):
        print(bin(data[0]))
        cfgword = {}
        cfgword["jtagen"] = (
            data[0] & self.CFGWORD_JTAGEN_MSK
        ) >> self.CFGWORD_JTAGEN_POS
        cfgword["flashwe"] = (
            data[0] & self.CFGWORD_FLASHWE_MSK
        ) >> self.CFGWORD_FLASHWE_POS
        cfgword["res_str"] = "JTAGEN=[%01d] FLASHWE=[%01d]" % (
            cfgword["jtagen"],
            cfgword["flashwe"],
        )
        print(data[0])
        return cfgword

    def pack_cfgword(self, cfgword):
        data = [0x0] * 4
        if cfgword["jtagen"]:
            data[0] |= 1 << self.CFGWORD_JTAGEN_POS
            data[1] |= 1 << self.CFGWORD_JTAGEN_POS
            data[2] |= 1 << self.CFGWORD_JTAGEN_POS
            data[3] |= 1 << self.CFGWORD_JTAGEN_POS
        if cfgword["flashwe"]:
            data[0] |= 1 << self.CFGWORD_FLASHWE_POS
            data[1] |= 1 << self.CFGWORD_FLASHWE_POS
            data[2] |= 1 << self.CFGWORD_FLASHWE_POS
            data[3] |= 1 << self.CFGWORD_FLASHWE_POS
        print(f"PACKED CFGWORD = {data}")
        res_str = "JTAGEN=[%01d] FLASHWE=[%01d]" % (
            cfgword["flashwe"],
            cfgword["jtagen"],
        )
        return (data, res_str)

    def apply_cfgword(self, cfgword):
        self.cfgword = cfgword
        for p in range(self.flash[0]["region_main"].pages):
            self.flash[0]["region_main"].wr_lock[p] = (
                False if cfgword["flashwe"] else True
            )
        for p in range(self.flash[0]["region_nvr"].pages):
            self.flash[0]["region_nvr"].wr_lock[p] = (
                False if cfgword["flashwe"] else True
            )
        # bootloader pages
        self.flash[0]["region_nvr"].wr_lock[0:3] = [True] * 3
        self.flash[0]["region_nvr"].rd_lock[0:3] = [True] * 3


class K1921VG015(MCU):
    CFGWORD_FLASHWE_POS = 0
    CFGWORD_NVRWE_POS = 1
    CFGWORD_JTAGEN_POS = 2
    CFGWORD_FLASHWE_MSK = 1 << CFGWORD_FLASHWE_POS
    CFGWORD_NVRWE_MSK = 1 << CFGWORD_NVRWE_POS
    CFGWORD_JTAGEN_MSK = 1 << CFGWORD_JTAGEN_POS

    def __init__(self):
        super().__init__()
        self.chipid = "0xDEADBEE0"
        self.name = "k1921vg015"
        self.name_ru = "К1921ВГ015"
        self.flash_base_address = 0x80000000
        self.flash = [
            {
                "name": "flash",
                "region_main": Flash(size=(1024 * K), pages=256),
                "region_nvr": Flash(size=(8 * K), pages=2),
                "bootflash_end_address": 0x2000,
                "base_address": 0x80000000,
                "start_page_main": 2,
                "start_page_nvr": 0,
                "lockable": False,
            }
        ]
        self.cfgword = {}
        self.flash[0]["region_nvr"].wr_lock[0:3] = [True] * 3
        self.flash[0]["region_nvr"].rd_lock[0:3] = [True] * 3
        self.booten_active = True

    def parse_cfgword(self, data):
        cfgword = {}
        cfgword["jtagen"] = (
            data[0] & self.CFGWORD_JTAGEN_MSK
        ) >> self.CFGWORD_JTAGEN_POS
        cfgword["nvrwe"] = (data[0] & self.CFGWORD_NVRWE_MSK) >> self.CFGWORD_NVRWE_POS
        cfgword["flashwe"] = (
            data[0] & self.CFGWORD_FLASHWE_MSK
        ) >> self.CFGWORD_FLASHWE_POS
        cfgword["res_str"] = "JTAGEN=[%01d] NVRWE=[%01d] FLASHWE=[%01d]" % (
            cfgword["jtagen"],
            cfgword["nvrwe"],
            cfgword["flashwe"],
        )
        # (cfgword['jtagen'], cfgword['nvrwe'], cfgword['flashwe'], cfgword['bmodedis']))
        return cfgword

    def pack_cfgword(self, cfgword):
        data = [0xFF] * 4
        data[0] &= 1
        data[0] &= 1
        data[0] &= ~(0 if cfgword["jtagen"] else self.CFGWORD_JTAGEN_MSK)
        data[0] &= 1
        data[0] &= ~(0 if cfgword["nvrwe"] else self.CFGWORD_NVRWE_MSK)
        data[0] &= ~(0 if cfgword["flashwe"] else self.CFGWORD_FLASHWE_MSK)
        data[0] &= 1
        res_str = (
            "FLASHRE=[%01d] NVRRE=[%01d] JTAGEN=[%01d] DEBUGEN=[%01d] NVRWE=[%01d] FLASHWE=[%01d] BMODEDIS=[%01d]"
            % (
                cfgword["flashre"],
                cfgword["nvrre"],
                cfgword["jtagen"],
                cfgword["debugen"],
                cfgword["nvrwe"],
                cfgword["flashwe"],
                cfgword["bmodedis"],
            )
        )
        return (data, res_str)

    def apply_cfgword(self, cfgword):
        self.cfgword = cfgword
        for p in range(self.flash[0]["region_main"].pages):
            self.flash[0]["region_main"].wr_lock[p] = (
                False if cfgword["flashwe"] else True
            )
        for p in range(self.flash[0]["region_nvr"].pages):
            self.flash[0]["region_nvr"].wr_lock[p] = False if cfgword["nvrwe"] else True
        # bootloader pages
        self.flash[0]["region_nvr"].wr_lock[0:3] = [True] * 3
        self.flash[0]["region_nvr"].rd_lock[0:3] = [True] * 3


class K1921VK035(MCU):
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
        super().__init__()
        self.chipid = "0x5A298FE1"
        self.name = "k1921vk035"
        self.name_ru = "К1921ВК035"
        self.flash_base_address = 0x0
        self.flash = [
            {
                "name": "mflash",
                "region_main": Flash(size=(64 * K), pages=64),
                "region_nvr": Flash(size=(4 * K), pages=4),
                "bootflash_end_address": 0x0,
                "base_address": 0x0,
                "lockable": True,
            }
        ]
        self.cfgword = {}
        self.flash[0]["region_nvr"].wr_lock[0:3] = [True] * 3
        self.flash[0]["region_nvr"].rd_lock[0:3] = [True] * 3
        self.booten_active = True

    def parse_cfgword(self, data):
        cfgword = {}
        cfgword["flashre"] = (
            data[0] & self.CFGWORD_FLASHRE_MSK
        ) >> self.CFGWORD_FLASHRE_POS
        cfgword["nvrre"] = (data[0] & self.CFGWORD_NVRRE_MSK) >> self.CFGWORD_NVRRE_POS
        cfgword["jtagen"] = (
            data[0] & self.CFGWORD_JTAGEN_MSK
        ) >> self.CFGWORD_JTAGEN_POS
        cfgword["debugen"] = (
            data[0] & self.CFGWORD_DEBUGEN_MSK
        ) >> self.CFGWORD_DEBUGEN_POS
        cfgword["nvrwe"] = (data[0] & self.CFGWORD_NVRWE_MSK) >> self.CFGWORD_NVRWE_POS
        cfgword["flashwe"] = (
            data[0] & self.CFGWORD_FLASHWE_MSK
        ) >> self.CFGWORD_FLASHWE_POS
        cfgword["bmodedis"] = (
            data[0] & self.CFGWORD_BMODEDIS_MSK
        ) >> self.CFGWORD_BMODEDIS_POS
        cfgword["res_str"] = (
            "FLASHRE=[%01d] NVRRE=[%01d] JTAGEN=[%01d] DEBUGEN=[%01d] NVRWE=[%01d] FLASHWE=[%01d] BMODEDIS=[%01d]"
            % (
                cfgword["flashre"],
                cfgword["nvrre"],
                cfgword["jtagen"],
                cfgword["debugen"],
                cfgword["nvrwe"],
                cfgword["flashwe"],
                cfgword["bmodedis"],
            )
        )
        return cfgword

    def pack_cfgword(self, cfgword):
        data = [0xFF] * 4
        data[0] &= ~(0 if cfgword["flashre"] else self.CFGWORD_FLASHRE_MSK)
        data[0] &= ~(0 if cfgword["nvrre"] else self.CFGWORD_NVRRE_MSK)
        data[0] &= ~(0 if cfgword["jtagen"] else self.CFGWORD_JTAGEN_MSK)
        data[0] &= ~(0 if cfgword["debugen"] else self.CFGWORD_DEBUGEN_MSK)
        data[0] &= ~(0 if cfgword["nvrwe"] else self.CFGWORD_NVRWE_MSK)
        data[0] &= ~(0 if cfgword["flashwe"] else self.CFGWORD_FLASHWE_MSK)
        data[0] &= ~(0 if cfgword["bmodedis"] else self.CFGWORD_BMODEDIS_MSK)
        res_str = (
            "FLASHRE=[%01d] NVRRE=[%01d] JTAGEN=[%01d] DEBUGEN=[%01d] NVRWE=[%01d] FLASHWE=[%01d] BMODEDIS=[%01d]"
            % (
                cfgword["flashre"],
                cfgword["nvrre"],
                cfgword["jtagen"],
                cfgword["debugen"],
                cfgword["nvrwe"],
                cfgword["flashwe"],
                cfgword["bmodedis"],
            )
        )
        return (data, res_str)

    def apply_cfgword(self, cfgword):
        self.cfgword = cfgword
        for p in range(self.flash[0]["region_main"].pages):
            self.flash[0]["region_main"].rd_lock[p] = (
                False if cfgword["flashre"] else True
            )
        for p in range(self.flash[0]["region_nvr"].pages):
            self.flash[0]["region_nvr"].rd_lock[p] = False if cfgword["nvrre"] else True
        for p in range(self.flash[0]["region_main"].pages):
            self.flash[0]["region_main"].wr_lock[p] = (
                False if cfgword["flashwe"] else True
            )
        for p in range(self.flash[0]["region_nvr"].pages):
            self.flash[0]["region_nvr"].wr_lock[p] = False if cfgword["nvrwe"] else True
        # bootloader pages
        self.flash[0]["region_nvr"].wr_lock[0:3] = [True] * 3
        self.flash[0]["region_nvr"].rd_lock[0:3] = [True] * 3


class K1921VK028(MCU):
    CFGWORD0_RDC_POS = 0
    CFGWORD0_WRC_POS = 4
    CFGWORD0_MASK_POS = 8
    CFGWORD0_RDC_MSK = 0xF << CFGWORD0_RDC_POS
    CFGWORD0_WRC_MSK = 0xF << CFGWORD0_WRC_POS
    CFGWORD0_MASK_MSK = 0xFFF << CFGWORD0_MASK_POS
    CFGWORD1_TAC_POS = 0
    CFGWORD1_MODE_POS = 4
    CFGWORD1_AF_POS = 5
    CFGWORD1_MFLASHWE_POS = 6
    CFGWORD1_MNVRWE_POS = 7
    CFGWORD1_BFLASHWE_POS = 8
    CFGWORD1_BNVRWE_POS = 9
    CFGWORD1_JTAGEN_POS = 10
    CFGWORD1_DEBUGEN_POS = 11
    CFGWORD1_MFLASHRE_POS = 12
    CFGWORD1_MNVRRE_POS = 13
    CFGWORD1_BFLASHRE_POS = 14
    CFGWORD1_BNVRRE_POS = 15
    CFGWORD1_TAC_MSK = 0xF << CFGWORD1_TAC_POS
    CFGWORD1_MODE_MSK = 1 << CFGWORD1_MODE_POS
    CFGWORD1_AF_MSK = 1 << CFGWORD1_AF_POS
    CFGWORD1_MFLASHWE_MSK = 1 << CFGWORD1_MFLASHWE_POS
    CFGWORD1_MNVRWE_MSK = 1 << CFGWORD1_MNVRWE_POS
    CFGWORD1_BFLASHWE_MSK = 1 << CFGWORD1_BFLASHWE_POS
    CFGWORD1_BNVRWE_MSK = 1 << CFGWORD1_BNVRWE_POS
    CFGWORD1_JTAGEN_MSK = 1 << CFGWORD1_JTAGEN_POS
    CFGWORD1_DEBUGEN_MSK = 1 << CFGWORD1_DEBUGEN_POS
    CFGWORD1_MFLASHRE_MSK = 1 << CFGWORD1_MFLASHRE_POS
    CFGWORD1_MNVRRE_MSK = 1 << CFGWORD1_MNVRRE_POS
    CFGWORD1_BFLASHRE_MSK = 1 << CFGWORD1_BFLASHRE_POS
    CFGWORD1_BNVRRE_MSK = 1 << CFGWORD1_BNVRRE_POS

    def __init__(self):
        super().__init__()
        self.chipid = "0x3ABF2FD1"
        self.name = "k1921vk028"
        self.name_ru = "К1921ВК028"
        self.flash_base_address = 0x10000000
        self.flash = [
            {
                "name": "mflash",
                "region_main": Flash(size=(2 * M), pages=128),
                "region_nvr": Flash(size=(64 * K), pages=4),
                "bootflash_end_address": 0x0,
                "lockable": True,
            },
            {
                "name": "bflash",
                "region_main": Flash(size=(512 * K), pages=128),
                "region_nvr": Flash(size=(16 * K), pages=4),
                "bootflash_end_address": 0x0,
                "lockable": True,
            },
        ]
        self.cfgword = {}
        self.flash[1]["region_main"].wr_lock[0] = True
        self.flash[1]["region_main"].rd_lock[0] = True
        self.flash[1]["region_main"].wr_lock[1] = True
        self.flash[1]["region_main"].rd_lock[1] = True
        self.booten_active = False

    def parse_cfgword(self, data):
        cfgword = {}
        temp0 = (data[3] << 24) | (data[2] << 16) | (data[1] << 8) | (data[0] << 0)
        temp1 = (data[7] << 24) | (data[6] << 16) | (data[5] << 8) | (data[4] << 0)
        cfgword["rdc"] = (temp0 & self.CFGWORD0_RDC_MSK) >> self.CFGWORD0_RDC_POS
        cfgword["wrc"] = (temp0 & self.CFGWORD0_WRC_MSK) >> self.CFGWORD0_WRC_POS
        cfgword["mask"] = (temp0 & self.CFGWORD0_MASK_MSK) >> self.CFGWORD0_MASK_POS

        cfgword["debugen"] = (
            temp1 & self.CFGWORD1_DEBUGEN_MSK
        ) >> self.CFGWORD1_DEBUGEN_POS
        cfgword["jtagen"] = (
            temp1 & self.CFGWORD1_JTAGEN_MSK
        ) >> self.CFGWORD1_JTAGEN_POS
        cfgword["tac"] = (temp1 & self.CFGWORD1_TAC_MSK) >> self.CFGWORD1_TAC_POS
        cfgword["mode"] = (temp1 & self.CFGWORD1_MODE_MSK) >> self.CFGWORD1_MODE_POS
        cfgword["af"] = (temp1 & self.CFGWORD1_AF_MSK) >> self.CFGWORD1_AF_POS
        cfgword["mflashwe"] = (
            temp1 & self.CFGWORD1_MFLASHWE_MSK
        ) >> self.CFGWORD1_MFLASHWE_POS
        cfgword["mnvrwe"] = (
            temp1 & self.CFGWORD1_MNVRWE_MSK
        ) >> self.CFGWORD1_MNVRWE_POS
        cfgword["bflashwe"] = (
            temp1 & self.CFGWORD1_BFLASHWE_MSK
        ) >> self.CFGWORD1_BFLASHWE_POS
        cfgword["bnvrwe"] = (
            temp1 & self.CFGWORD1_BNVRWE_MSK
        ) >> self.CFGWORD1_BNVRWE_POS
        cfgword["mflashre"] = (
            temp1 & self.CFGWORD1_MFLASHRE_MSK
        ) >> self.CFGWORD1_MFLASHRE_POS
        cfgword["mnvrre"] = (
            temp1 & self.CFGWORD1_MNVRRE_MSK
        ) >> self.CFGWORD1_MNVRRE_POS
        cfgword["bflashre"] = (
            temp1 & self.CFGWORD1_BFLASHRE_MSK
        ) >> self.CFGWORD1_BFLASHRE_POS
        cfgword["bnvrre"] = (
            temp1 & self.CFGWORD1_BNVRRE_MSK
        ) >> self.CFGWORD1_BNVRRE_POS
        cfgword["res_str"] = (
            "RDC=[0x%01x] WRC=[0x%01x] MASK=[0x%03x] TAC=[0x%01x] MODE=[%01d] AF=[%01d] MFLASHWE=[%01d] MNVRWE=[%01d] BFLASHWE=[%01d] BNVRWE=[%01d] MFLASHRE=[%01d] MNVRRE=[%01d] BFLASHRE=[%01d] BNVRRE=[%01d]"
            % (
                cfgword["rdc"],
                cfgword["wrc"],
                cfgword["mask"],
                cfgword["tac"],
                cfgword["mode"],
                cfgword["af"],
                cfgword["mflashwe"],
                cfgword["mnvrwe"],
                cfgword["bflashwe"],
                cfgword["bnvrwe"],
                cfgword["mflashre"],
                cfgword["mnvrre"],
                cfgword["bflashre"],
                cfgword["bnvrre"],
            )
        )
        return cfgword

    def pack_cfgword(self, cfgword):
        data = [0xFF] * 8
        temp = 0xFFFFFFFF
        temp = (temp & (~self.CFGWORD0_RDC_MSK)) | (
            cfgword["rdc"] << self.CFGWORD0_RDC_POS
        )
        temp = (temp & (~self.CFGWORD0_WRC_MSK)) | (
            cfgword["wrc"] << self.CFGWORD0_WRC_POS
        )
        temp = (temp & (~self.CFGWORD0_MASK_MSK)) | (
            cfgword["mask"] << self.CFGWORD0_MASK_POS
        )
        data[0] = (temp >> 0) & 0xFF
        data[1] = (temp >> 8) & 0xFF
        data[2] = (temp >> 16) & 0xFF
        data[3] = (temp >> 24) & 0xFF
        temp = 0xFFFFFFFF
        temp = (temp & (~self.CFGWORD1_TAC_MSK)) | (
            cfgword["tac"] << self.CFGWORD1_TAC_POS
        )
        temp = (temp & (~self.CFGWORD1_MODE_MSK)) | (
            cfgword["mode"] << self.CFGWORD1_MODE_POS
        )
        temp = (temp & (~self.CFGWORD1_AF_MSK)) | (
            cfgword["af"] << self.CFGWORD1_AF_POS
        )
        temp &= ~(0 if cfgword["debugen"] else self.CFGWORD1_DEBUGEN_MSK)
        temp &= ~(0 if cfgword["jtagen"] else self.CFGWORD1_JTAGEN_MSK)
        temp &= ~(0 if cfgword["mflashwe"] else self.CFGWORD1_MFLASHWE_MSK)
        temp &= ~(0 if cfgword["mnvrwe"] else self.CFGWORD1_MNVRWE_MSK)
        temp &= ~(0 if cfgword["bflashwe"] else self.CFGWORD1_BFLASHWE_MSK)
        temp &= ~(0 if cfgword["bnvrwe"] else self.CFGWORD1_BNVRWE_MSK)
        temp &= ~(0 if cfgword["mflashre"] else self.CFGWORD1_MFLASHRE_MSK)
        temp &= ~(0 if cfgword["mnvrre"] else self.CFGWORD1_MNVRRE_MSK)
        temp &= ~(0 if cfgword["bflashre"] else self.CFGWORD1_BFLASHRE_MSK)
        temp &= ~(0 if cfgword["bnvrre"] else self.CFGWORD1_BNVRRE_MSK)
        data[4] = (temp >> 0) & 0xFF
        data[5] = (temp >> 8) & 0xFF
        data[6] = (temp >> 16) & 0xFF
        data[7] = (temp >> 24) & 0xFF

        res_str = (
            "RDC=[0x%01x] WRC=[0x%01x] MASK=[0x%03x] TAC=[0x%01x] DEBUGEN=[%01d] JTAGEN=[%01d] MODE=[%01d] AF=[%01d] MFLASHWE=[%01d] MNVRWE=[%01d] BFLASHWE=[%01d] BNVRWE=[%01d] MFLASHRE=[%01d] MNVRRE=[%01d] BFLASHRE=[%01d] BNVRRE=[%01d]"
            % (
                cfgword["rdc"],
                cfgword["wrc"],
                cfgword["mask"],
                cfgword["tac"],
                cfgword["debugen"],
                cfgword["jtagen"],
                cfgword["mode"],
                cfgword["af"],
                cfgword["mflashwe"],
                cfgword["mnvrwe"],
                cfgword["bflashwe"],
                cfgword["bnvrwe"],
                cfgword["mflashre"],
                cfgword["mnvrre"],
                cfgword["bflashre"],
                cfgword["bnvrre"],
            )
        )
        return (data, res_str)

    def apply_cfgword(self, cfgword):
        self.cfgword = cfgword
        for p in range(self.flash[0]["region_main"].pages):
            self.flash[0]["region_main"].rd_lock[p] = (
                False if cfgword["mflashre"] else True
            )
        for p in range(self.flash[0]["region_nvr"].pages):
            self.flash[0]["region_nvr"].rd_lock[p] = (
                False if cfgword["mnvrre"] else True
            )
        for p in range(self.flash[0]["region_main"].pages):
            self.flash[0]["region_main"].wr_lock[p] = (
                False if cfgword["mflashwe"] else True
            )
        for p in range(self.flash[0]["region_nvr"].pages):
            self.flash[0]["region_nvr"].wr_lock[p] = (
                False if cfgword["mnvrwe"] else True
            )
        for p in range(self.flash[1]["region_main"].pages):
            self.flash[1]["region_main"].rd_lock[p] = (
                False if cfgword["bflashre"] else True
            )
        for p in range(self.flash[1]["region_nvr"].pages):
            self.flash[1]["region_nvr"].rd_lock[p] = (
                False if cfgword["bnvrre"] else True
            )
        for p in range(self.flash[1]["region_main"].pages):
            self.flash[1]["region_main"].wr_lock[p] = (
                False if cfgword["bflashwe"] else True
            )
        for p in range(self.flash[1]["region_nvr"].pages):
            self.flash[1]["region_nvr"].wr_lock[p] = (
                False if cfgword["bnvrwe"] else True
            )
        # bootloader pages
        self.flash[1]["region_main"].wr_lock[0] = True
        self.flash[1]["region_main"].rd_lock[0] = True
        self.flash[1]["region_main"].wr_lock[1] = True
        self.flash[1]["region_main"].rd_lock[1] = True


class K1921VK01T(MCU):
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
    CFGWORD_UFIFBRE_MSK = 1 << CFGWORD_UFIFBRE_POS
    CFGWORD_UFRE_MSK = 1 << CFGWORD_UFRE_POS
    CFGWORD_LOCKIFBUF_MSK = 1 << CFGWORD_LOCKIFBUF_POS
    CFGWORD_BFIFBRE_MSK = 1 << CFGWORD_BFIFBRE_POS
    CFGWORD_BFRE_MSK = 1 << CFGWORD_BFRE_POS
    CFGWORD_LOCKIFBLF_MSK = 1 << CFGWORD_LOCKIFBLF_POS
    CFGWORD_PORTNUM_MSK = 0xF << CFGWORD_PORTNUM_POS
    CFGWORD_PINNUM_MSK = 0xF << CFGWORD_PINNUM_POS
    CFGWORD_EXTMEMSEL_MSK = 3 << CFGWORD_EXTMEMSEL_POS
    CFGWORD_ENGPIO_MSK = 1 << CFGWORD_ENGPIO_POS
    CFGWORD_BOOTFROMIFB_MSK = 1 << CFGWORD_BOOTFROMIFB_POS

    def __init__(self):
        super().__init__()
        self.chipid = "0x00000000"
        self.name = "k1921vk01t"
        self.name_ru = "К1921ВК01Т"
        self.flash_base_address = 0x00002000
        self.flash = [
            {
                "name": "bootflash",
                "region_main": Flash(size=(1 * M), pages=128),
                "region_nvr": Flash(size=(8 * K), pages=1),
                "bootflash_end_address": 0x0,
                "lockable": True,
            },
            {
                "name": "userflash",
                "region_main": Flash(size=(64 * K), pages=256),
                "region_nvr": Flash(size=512, pages=2),
                "bootflash_end_address": 0x0,
                "lockable": True,
            },
        ]
        self.cfgword = {}
        self.flash[0]["region_nvr"].wr_lock[0] = True
        self.flash[0]["region_nvr"].rd_lock[0] = True
        self.flash[0]["region_main"].rd_lock[0] = True
        self.booten_active = False

    def parse_cfgword(self, data):
        cfgword = {}
        temp = (data[3] << 24) | (data[2] << 16) | (data[1] << 8) | (data[0] << 0)
        cfgword["boot_from_ifb"] = (
            temp & self.CFGWORD_BOOTFROMIFB_MSK
        ) >> self.CFGWORD_BOOTFROMIFB_POS
        cfgword["en_gpio"] = (temp & self.CFGWORD_ENGPIO_MSK) >> self.CFGWORD_ENGPIO_POS
        cfgword["extmem_sel"] = (
            temp & self.CFGWORD_EXTMEMSEL_MSK
        ) >> self.CFGWORD_EXTMEMSEL_POS
        cfgword["pinnum"] = (temp & self.CFGWORD_PINNUM_MSK) >> self.CFGWORD_PINNUM_POS
        cfgword["portnum"] = (
            temp & self.CFGWORD_PORTNUM_MSK
        ) >> self.CFGWORD_PORTNUM_POS
        cfgword["lock_ifb_lf"] = (
            temp & self.CFGWORD_LOCKIFBLF_MSK
        ) >> self.CFGWORD_LOCKIFBLF_POS
        cfgword["bfre"] = (temp & self.CFGWORD_BFRE_MSK) >> self.CFGWORD_BFRE_POS
        cfgword["bfifbre"] = (
            temp & self.CFGWORD_BFIFBRE_MSK
        ) >> self.CFGWORD_BFIFBRE_POS
        cfgword["lock_ifb_uf"] = (
            temp & self.CFGWORD_LOCKIFBUF_MSK
        ) >> self.CFGWORD_LOCKIFBUF_POS
        cfgword["ufre"] = (temp & self.CFGWORD_UFRE_MSK) >> self.CFGWORD_UFRE_POS
        cfgword["ufifbre"] = (
            temp & self.CFGWORD_UFIFBRE_MSK
        ) >> self.CFGWORD_UFIFBRE_POS
        cfgword["res_str"] = (
            "BOOTFROMIFB=[%01d] ENGPIO=[%01d] EXTMEMSEL=[%01d] PINNUM=[%02d] PORTNUM=[%02d] LOCKIFBLF=[%01d] BFRE=[%01d] BFIFBRE=[%01d] LOCKIFBUF=[%01d] UFRE=[%01d] UFIFBRE=[%01d]"
            % (
                cfgword["boot_from_ifb"],
                cfgword["en_gpio"],
                cfgword["extmem_sel"],
                cfgword["pinnum"],
                cfgword["portnum"],
                cfgword["lock_ifb_lf"],
                cfgword["bfre"],
                cfgword["bfifbre"],
                cfgword["lock_ifb_uf"],
                cfgword["ufre"],
                cfgword["ufifbre"],
            )
        )
        _bflock = ""
        for b in range(16):
            _bflock = bin(data[4 + b])[2:].zfill(8) + _bflock
        bflock = _bflock[::-1]
        _uflock = ""
        for b in range(32):
            _uflock = bin(data[20 + b])[2:].zfill(8) + _uflock
        uflock = _uflock[::-1]
        cfgword["bflock"] = [1] * self.flash[0]["region_main"].pages
        cfgword["uflock"] = [1] * self.flash[1]["region_main"].pages
        for p in range(len(bflock)):
            cfgword["bflock"][p] = int(bflock[p])
        for p in range(len(uflock)):
            cfgword["uflock"][p] = int(uflock[p])
        return cfgword

    def pack_cfgword(self, cfgword):
        data = [0xFF] * (4 + 16 + 32)
        temp = 0xFFFFFFFF
        temp &= ~(0 if cfgword["boot_from_ifb"] else self.CFGWORD_BOOTFROMIFB_MSK)
        temp &= ~(0 if cfgword["en_gpio"] else self.CFGWORD_ENGPIO_MSK)
        temp = (temp & (~self.CFGWORD_EXTMEMSEL_MSK)) | (
            cfgword["extmem_sel"] << self.CFGWORD_EXTMEMSEL_POS
        )
        temp = (temp & (~self.CFGWORD_PINNUM_MSK)) | (
            cfgword["pinnum"] << self.CFGWORD_PINNUM_POS
        )
        temp = (temp & (~self.CFGWORD_PORTNUM_MSK)) | (
            cfgword["portnum"] << self.CFGWORD_PORTNUM_POS
        )
        temp &= ~(0 if cfgword["lock_ifb_lf"] else self.CFGWORD_LOCKIFBLF_MSK)
        temp &= ~(0 if cfgword["bfre"] else self.CFGWORD_BFRE_MSK)
        temp &= ~(0 if cfgword["bfifbre"] else self.CFGWORD_BFIFBRE_MSK)
        temp &= ~(0 if cfgword["lock_ifb_uf"] else self.CFGWORD_LOCKIFBUF_MSK)
        temp &= ~(0 if cfgword["ufre"] else self.CFGWORD_UFRE_MSK)
        temp &= ~(0 if cfgword["ufifbre"] else self.CFGWORD_UFIFBRE_MSK)
        data[0] = (temp >> 0) & 0xFF
        data[1] = (temp >> 8) & 0xFF
        data[2] = (temp >> 16) & 0xFF
        data[3] = (temp >> 24) & 0xFF
        for p in range(0, len(cfgword["bflock"])):
            data[4 + (p // 8)] &= ~(0 if cfgword["bflock"][p] else (1 << (p % 8)))
        for p in range(0, len(cfgword["uflock"])):
            data[20 + (p // 8)] &= ~(0 if cfgword["uflock"][p] else (1 << (p % 8)))
        res_str = (
            "BOOTFROMIFB=[%01d] ENGPIO=[%01d] EXTMEMSEL=[%01d] PINNUM=[%02d] PORTNUM=[%02d] LOCKIFBLF=[%01d] BFRE=[%01d] BFIFBRE=[%01d] LOCKIFBUF=[%01d] UFRE=[%01d] UFIFBRE=[%01d]"
            % (
                cfgword["boot_from_ifb"],
                cfgword["en_gpio"],
                cfgword["extmem_sel"],
                cfgword["pinnum"],
                cfgword["portnum"],
                cfgword["lock_ifb_lf"],
                cfgword["bfre"],
                cfgword["bfifbre"],
                cfgword["lock_ifb_uf"],
                cfgword["ufre"],
                cfgword["ufifbre"],
            )
        )
        return (data, res_str)

    def apply_cfgword(self, cfgword):
        self.cfgword = cfgword
        for p in range(self.flash[0]["region_main"].pages):
            self.flash[0]["region_main"].rd_lock[p] = False if cfgword["bfre"] else True
        for p in range(self.flash[0]["region_nvr"].pages):
            self.flash[0]["region_nvr"].rd_lock[p] = (
                False if cfgword["bfifbre"] else True
            )
        for p in range(self.flash[0]["region_main"].pages):
            self.flash[0]["region_main"].wr_lock[p] = (
                False if cfgword["bflock"][p] else True
            )
        for p in range(self.flash[0]["region_nvr"].pages):
            self.flash[0]["region_nvr"].wr_lock[p] = (
                False if cfgword["lock_ifb_lf"] else True
            )
        for p in range(self.flash[1]["region_main"].pages):
            self.flash[1]["region_main"].rd_lock[p] = False if cfgword["ufre"] else True
        for p in range(self.flash[1]["region_nvr"].pages):
            self.flash[1]["region_nvr"].rd_lock[p] = (
                False if cfgword["ufifbre"] else True
            )
        for p in range(self.flash[1]["region_main"].pages):
            self.flash[1]["region_main"].wr_lock[p] = (
                False if cfgword["uflock"][p] else True
            )
        for p in range(self.flash[1]["region_nvr"].pages):
            self.flash[1]["region_nvr"].wr_lock[p] = (
                False if cfgword["lock_ifb_uf"] else True
            )
        # bootloader pages
        self.flash[0]["region_nvr"].wr_lock[0] = True
        self.flash[0]["region_nvr"].rd_lock[0] = True
        self.flash[0]["region_main"].rd_lock[0] = True


db = [
    K1921Vx(),
    K1921VG015(),
    K1921VK035(),
    K1921VK028(),
    K1921VK01T(),
    K1921VG5T(),
    K1921VG7T(),
    K1921VG3T(),
    K1921VG1T(),
]


def get_by_chipid(chipid):
    for mcu in db:
        if mcu.chipid == chipid:
            return mcu
    return None


def get_by_name(name):
    for mcu in db:
        if mcu.name == name:
            return mcu
    return None
