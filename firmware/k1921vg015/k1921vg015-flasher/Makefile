#==============================================================================
# Makefile NIIET K1921VG015
# Created by NIIET
# free to use
#==============================================================================
TARGET_NAME = k1921vg015_flasher
	
COMPILER_PATH ?= C:/Users/user/.niiet_aspect/riscv_gcc_windows/bin
ADDITIONAL_FLAGS ?= 
DEFINES ?= -DHSECLK_VAL=16000000 -DRETARGET -DSYSCLK_PLL -DCKO_PLL0
PREFIX ?= riscv64-unknown-elf-
	
LINKER_PATH  		= F:/bootloader/git/k1921vkx_flasher/firmware/k1921vg015/k1921vg015-flasher/platform/ldscripts
LD_SRC 				= F:/bootloader/git/k1921vkx_flasher/firmware/k1921vg015/k1921vg015-flasher/platform/ldscripts/k1921vg015_boot_flash.ld
MARCH				= rv32imfc
MABI				= ilp32f
BUILD_NAME			= build
BUILD_PATH  		?= ./$(BUILD_NAME)
	
OPTIMISATION ?= -Os

rwildcard = $(foreach d,$(wildcard $(1:=/*)),$(call rwildcard,$d,$2) $(filter $(subst *,%,$2),$d))
	
SRCS := $(call rwildcard,.,*.c)
ASMS := $(call rwildcard,.,*.S)
HEADERS := $(call rwildcard,.,*.h)
	
OBJS := $(SRCS:.c=.o)
OBJS += $(ASMS:.S=.o)
	
INCLUDE_FOLDERS = $(foreach inc, $(sort $(dir $(HEADERS))), -I"$(inc)")
OBJ_DIRS = $(sort $(dir $(OBJS)))
	
LIBS ?= -L$(LINKER_PATH)
LIBS_ACR ?= -lc_nano -lg_nano -lgcc
	
LD_FLAGS ?= -static $(LIBS)  $(LIBS_ACR)

export CROSS_PREFIX = $(COMPILER_PATH)$(if $(COMPILER_PATH),/,)$(PREFIX)

ifeq ($(OS), Windows_NT)
export RISCV-GCC	 ?= $(CROSS_PREFIX)gcc.exe -c -Wall $(OPTIMISATION) -march=$(MARCH) -mabi=$(MABI) -g -ggdb3 $(DEFINES) $(INCLUDE_FOLDERS) -static -std=gnu99 $(LIBS) $(LIBS_ACR) $(ADDITIONAL_FLAGS)
export RISCV-AS 	 ?= $(CROSS_PREFIX)as.exe -mno-arch-attr $(OPTIMISATION) -march=$(MARCH) -mabi=$(MABI) $(ADDITIONAL_FLAGS)
export RISCV-LD 	 ?= $(CROSS_PREFIX)ld.exe 
export RISCV-OBJDUMP ?= $(CROSS_PREFIX)objdump.exe -S
export RISCV-OBJCOPY ?= $(CROSS_PREFIX)objcopy.exe
export RISCV-SIZE 	 ?= $(CROSS_PREFIX)size.exe
export RISCV-GDB	 ?= $(CROSS_PREFIX)gdb.exe
else 
export RISCV-GCC	 ?= $(CROSS_PREFIX)gcc -c -Wall $(OPTIMISATION) -g -ggdb3 -march=$(MARCH) -mabi=$(MABI) $(DEFINES) $(INCLUDE_FOLDERS) -static -std=gnu99 $(LIBS) $(LIBS_ACR) $(ADDITIONAL_FLAGS)
export RISCV-AS 	 ?= $(CROSS_PREFIX)as -mno-arch-attr $(OPTIMISATION) -march=$(MARCH) -mabi=$(MABI) $(ADDITIONAL_FLAGS)
export RISCV-LD 	 ?= $(CROSS_PREFIX)ld 
export RISCV-OBJDUMP ?= $(CROSS_PREFIX)objdump -S
export RISCV-OBJCOPY ?= $(CROSS_PREFIX)objcopy
export RISCV-SIZE 	 ?= $(CROSS_PREFIX)size
export RISCV-GDB	 ?= $(CROSS_PREFIX)gdb
endif

make_build:
	@ -$(foreach dir, $(OBJ_DIRS), mkdir -p $(BUILD_PATH)/$(dir) && ):

help:
	@ echo "help: make [all, clean, load]"
	
header:
	@ echo "NIIET MAKEFILE v.1.0 "$^""
	
%.o: %.S
	@ echo "ASSEMBLY "$^"" 
	$(RISCV-GCC) $^ -o $(BUILD_PATH)/$@
	@ echo "...DONE"
	
%.o: %.c
	@ echo "COMPILE "$^""
	$(RISCV-GCC) $^ -o $(BUILD_PATH)/$@ 
	@ echo "...DONE"
	
%.elf: $(OBJS)
	@ echo "LINK "$^"" 
	$(CROSS_PREFIX)g++ -o $@ $(foreach obj, $(OBJS), $(BUILD_PATH)/$(obj)) -static -march=$(MARCH) -mabi=$(MABI) -g -ggdb3 -std=gnu99 $(LD_FLAGS) -nostartfiles -T $(LD_SRC)
	@ echo "...DONE" 
	
%.dump: %.elf
	@ echo "DUMP "$^"" 
	$(RISCV-OBJDUMP) $^ > $@
	@ echo "...DONE"
	
size: $(BUILD_PATH)/$(TARGET_NAME).elf
	@ echo "~~SIZE~~ """ 
	$(RISCV-SIZE) $^

ifeq ($(OS), Windows_NT)
clean:
	@ echo "CLEANING "$^""
	rm -rf $(BUILD_PATH)
	@ echo "...DONE"
else
clean:
	@ echo "CLEANING "$^""
	rm -rf $(BUILD_PATH)
	@ echo "...DONE"
endif

hex:
	@ echo "HEX "
	$(RISCV-OBJCOPY) -O ihex $(BUILD_PATH)/$(TARGET_NAME).elf $(BUILD_PATH)/$(TARGET_NAME).hex
	@ echo "...DONE"
	

all: header clean make_build $(BUILD_PATH)/$(TARGET_NAME).elf $(BUILD_PATH)/$(TARGET_NAME).dump hex size
	
debug: all
	@ echo "LOAD "$(TARGET_NAME).elf"" 
	$(RISCV-GDB) $(BUILD_PATH)/$(TARGET_NAME).elf -iex="target extended-remote localhost:3333" -ex="monitor reset halt" -ex="load"
