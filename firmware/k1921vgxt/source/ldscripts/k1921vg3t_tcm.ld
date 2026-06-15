/** @file
*  @brief linker script for K1921VG3T
*/

OUTPUT_FORMAT("elf32-littleriscv", "elf32-littleriscv", "elf32-littleriscv")
OUTPUT_ARCH( "riscv" )
ENTRY(_start)

MEMORY {
  TCM (rwx) : ORIGIN = 0xf0000000, LENGTH = 64K
}

REGION_ALIAS("REGION_TEXT",   TCM);
REGION_ALIAS("REGION_RODATA", TCM);
REGION_ALIAS("REGION_DATA",   TCM);
REGION_ALIAS("REGION_BSS",    TCM);
REGION_ALIAS("REGION_STACK",  TCM);
REGION_ALIAS("REGION_TCM",    TCM );

STACK_SIZE = 2048;

INCLUDE "k1921vg3t_common.lds"
