# /*==============================================================================
# * Makefile для UART загрузчика для К1921ВГXT
# *
# *------------------------------------------------------------------------------
# * НИИЭТ, Долгополов Алексей <dolgopolov@niiet.ru>
# *==============================================================================
# * ДАННОЕ ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ ПРЕДОСТАВЛЯЕТСЯ «КАК ЕСТЬ», БЕЗ КАКИХ-ЛИБО
# * ГАРАНТИЙ, ЯВНО ВЫРАЖЕННЫХ ИЛИ ПОДРАЗУМЕВАЕМЫХ, ВКЛЮЧАЯ ГАРАНТИИ ТОВАРНОЙ
# * ПРИГОДНОСТИ, СООТВЕТСТВИЯ ПО ЕГО КОНКРЕТНОМУ НАЗНАЧЕНИЮ И ОТСУТСТВИЯ
# * НАРУШЕНИЙ, НО НЕ ОГРАНИЧИВАЯСЬ ИМИ. ДАННОЕ ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ
# * ПРЕДНАЗНАЧЕНО ДЛЯ ОЗНАКОМИТЕЛЬНЫХ ЦЕЛЕЙ И НАПРАВЛЕНО ТОЛЬКО НА
# * ПРЕДОСТАВЛЕНИЕ ДОПОЛНИТЕЛЬНОЙ ИНФОРМАЦИИ О ПРОДУКТЕ, С ЦЕЛЬЮ СОХРАНИТЬ ВРЕМЯ
# * ПОТРЕБИТЕЛЮ. НИ В КАКОМ СЛУЧАЕ АВТОРЫ ИЛИ ПРАВООБЛАДАТЕЛИ НЕ НЕСУТ
# * ОТВЕТСТВЕННОСТИ ПО КАКИМ-ЛИБО ИСКАМ, ЗА ПРЯМОЙ ИЛИ КОСВЕННЫЙ УЩЕРБ, ИЛИ
# * ПО ИНЫМ ТРЕБОВАНИЯМ, ВОЗНИКШИМ ИЗ-ЗА ИСПОЛЬЗОВАНИЯ ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# * ИЛИ ИНЫХ ДЕЙСТВИЙ С ПРОГРАММНЫМ ОБЕСПЕЧЕНИЕМ.
# *
# *                              2026 АО "НИИЭТ"
# *==============================================================================
# */

PRJ_ROOT_DIR := $(shell pwd)/../

TARGET_IDX  = 1
TARGET_NAME := vg$(TARGET_IDX)t


LIBS_PATH 	= $(PRJ_ROOT_DIR)/lib/
SRC_PATH 	= $(PRJ_ROOT_DIR)/src/
INC_PATH 	= $(PRJ_ROOT_DIR)/inc/
LD_SCR_PATH = $(PRJ_ROOT_DIR)/ldscripts/
STARTUP_FILE = startup_k1921$(TARGET_NAME)
SYSTEM_FILE =  system_k1921$(TARGET_NAME)
SYSINIT_FILE = sys_init_$(TARGET_NAME)

ELF_O_FILES :=  $(SRC_PATH)main.o \
				$(SRC_PATH)$(STARTUP_FILE).o \
				$(SRC_PATH)$(SYSTEM_FILE).o \
				$(SRC_PATH)$(SYSINIT_FILE).o \
				$(SRC_PATH)plic_$(TARGET_NAME).o \
				$(SRC_PATH)boot_core.o \
				$(SRC_PATH)boot_flash.o \
				$(SRC_PATH)boot_packet.o \


INCLUDE_FOLDER = -I$(INC_PATH)

LIBS += -L$(LIBS_PATH)
LIBS_ACR += -lc -lgcc
DEFS := -D SYSCLK_PLL -D HSECLK_VAL=16000000 -D __TARGET_IDX__=$(TARGET_IDX)


ARCH = rv32imafc_zicsr_zifencei
LD_SRC := $(LD_SCR_PATH)/k1921$(TARGET_NAME)_flash.ld
LD_FLAGS = -static -march=$(ARCH) -melf32lriscv $(LIBS) $(LIBS_ACR)
ifeq ($(TARGET_IDX), 1)
	OPT = -Os
else
	OPT = -O3
endif

export RISCV-GCC	 ?= $(CROSS_PREFIX)gcc -c -Wall $(OPT) -ggdb3 -ffunction-sections -fdata-sections -march=$(ARCH) -mabi=ilp32 $(INCLUDE_FOLDER) $(DEFS) -static -std=gnu99 $(LIBS) $(LIBS_ACR)
export CROSS_PREFIX  ?= ~/embedded/toolchains/riscv32-unknown-elf/bin/riscv32-unknown-elf-
export RISCV-AS 	 ?= $(CROSS_PREFIX)as -ggdb3 -march=$(ARCH) -mno-arch-attr
export RISCV-LD 	 ?= $(CROSS_PREFIX)ld --gc-sections -L$(LD_SCR_PATH)
export RISCV-OBJDUMP ?= $(CROSS_PREFIX)objdump -d -S
export RISCV-OBJCOPY ?= $(CROSS_PREFIX)objcopy

help:
	@ echo "help:\nmake all\nclean\nload"

header:
	@ echo "k1921vgxt makefile "$^""

%.o: %.c
	@ echo "COMPILE "$^""
	$(RISCV-GCC) $^ -o $@
	@ echo "...DONE"

%.o: %.S
	@ echo "ASSEMBLY "$^""
	$(RISCV-GCC) $^ -o $@
	@ echo "...DONE"

$(TARGET_NAME).elf: $(ELF_O_FILES)
	@ echo "LINK "$^""
	$(RISCV-LD) -o $@ -T $(LD_SRC) $^ $(LD_FLAGS)
	@ echo "...DONE"

%.dump: %.elf
	@ echo "DUMP "$^""
	$(RISCV-OBJDUMP) -dS $^ > $@
	@ echo "...DONE"

size: ./$(TARGET_NAME).elf
	@ echo "~~SIZE~~ """
	$(CROSS_PREFIX)size $^

$(TARGET_NAME).bin: $(TARGET_NAME).elf
	$(RISCV-OBJCOPY) -O binary $< $@

clean:
	@ echo "CLEANING "$^""
	find $(PRJ_ROOT_DIR)/. -name "*.o" -exec rm {} \;
	find $(PRJ_ROOT_DIR)/. -name "*.elf" -exec rm {} \;
	find $(PRJ_ROOT_DIR)/. -name "*.bin" -exec rm {} \;
	find $(PRJ_ROOT_DIR)/. -name "*.dump" -exec rm {} \;
	@ echo "...DONE"

all: header clean $(TARGET_NAME).elf $(TARGET_NAME).bin $(TARGET_NAME).dump size

load: all
	@ echo "LOAD "$(TARGET_NAME).elf""
	$(CROSS_PREFIX)gdb ./$(TARGET_NAME).elf -ex="tar rem :3333" -ex="monitor reset halt" -ex="load"
