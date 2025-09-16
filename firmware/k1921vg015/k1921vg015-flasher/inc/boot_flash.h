/*==============================================================================
 * UART загрузчик для К1921ВГ015
 *
 * Прототипы функций работы с флеш-памятью
 *------------------------------------------------------------------------------
 * НИИЭТ, Александр Дыхно <dykhno@niiet.ru>
 * НИИЭТ, Штоколов Филипп
 *==============================================================================
 * ДАННОЕ ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ ПРЕДОСТАВЛЯЕТСЯ «КАК ЕСТЬ», БЕЗ КАКИХ-ЛИБО
 * ГАРАНТИЙ, ЯВНО ВЫРАЖЕННЫХ ИЛИ ПОДРАЗУМЕВАЕМЫХ, ВКЛЮЧАЯ ГАРАНТИИ ТОВАРНОЙ
 * ПРИГОДНОСТИ, СООТВЕТСТВИЯ ПО ЕГО КОНКРЕТНОМУ НАЗНАЧЕНИЮ И ОТСУТСТВИЯ
 * НАРУШЕНИЙ, НО НЕ ОГРАНИЧИВАЯСЬ ИМИ. ДАННОЕ ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ
 * ПРЕДНАЗНАЧЕНО ДЛЯ ОЗНАКОМИТЕЛЬНЫХ ЦЕЛЕЙ И НАПРАВЛЕНО ТОЛЬКО НА
 * ПРЕДОСТАВЛЕНИЕ ДОПОЛНИТЕЛЬНОЙ ИНФОРМАЦИИ О ПРОДУКТЕ, С ЦЕЛЬЮ СОХРАНИТЬ ВРЕМЯ
 * ПОТРЕБИТЕЛЮ. НИ В КАКОМ СЛУЧАЕ АВТОРЫ ИЛИ ПРАВООБЛАДАТЕЛИ НЕ НЕСУТ
 * ОТВЕТСТВЕННОСТИ ПО КАКИМ-ЛИБО ИСКАМ, ЗА ПРЯМОЙ ИЛИ КОСВЕННЫЙ УЩЕРБ, ИЛИ
 * ПО ИНЫМ ТРЕБОВАНИЯМ, ВОЗНИКШИМ ИЗ-ЗА ИСПОЛЬЗОВАНИЯ ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
 * ИЛИ ИНЫХ ДЕЙСТВИЙ С ПРОГРАММНЫМ ОБЕСПЕЧЕНИЕМ.
 *
 *                              2025 АО "НИИЭТ"
 *==============================================================================
 */


#ifndef BOOT_FLASH_H
#define BOOT_FLASH_H

#include "boot_conf.h"

#define FLASH_CELL_WORD_WIDTH            4
#define FLASH_MAGICKEY_CONST        0xC0DEUL
#define FLASH_PAGE_SIZE_BYTES       4096UL
#define FLASH_PAGE_SIZE_BYTES_LOG2  12UL
#define FLASH_PAGE_SIZE_CELLS       (FLASH_PAGE_SIZE_BYTES/(FLASH_CELL_WORD_WIDTH*4))
#define FLASH_PAGE_TOTAL            256UL
#define FLASH_TOTAL_BYTES           (FLASH_PAGE_SIZE_BYTES*FLASH_PAGE_TOTAL)
#define FLASH_NVR_PAGE_SIZE_BYTES   FLASH_PAGE_SIZE_BYTES
#define FLASH_NVR_PAGE_TOTAL        2UL
#define FLASH_NVR_TOTAL_BYTES       (FLASH_NVR_PAGE_SIZE_BYTES*FLASH_NVR_PAGE_TOTAL)
#define FLASH_NVR_CFGWORD_OFFSET    (1*FLASH_NVR_PAGE_SIZE_BYTES+0xFF0)

#define BOOT_FLASH_SIZE_TOTAL_PAGES 2
#define BOOT_FLASH_SIZE_TOTAL_BYTES (BOOT_FLASH_SIZE_TOTAL_PAGES*FLASH_PAGE_SIZE_BYTES)

#define CFGWORD_FLASHWE_POS         0
#define CFGWORD_CFGWE_POS           1
#define CFGWORD_JTAGEN_POS          2
#define CFGWORD_FLASHWE_MSK         (1<<CFGWORD_FLASHWE_POS)
#define CFGWORD_CFGWE_MSK           (1<<CFGWORD_CFGWE_POS)
#define CFGWORD_JTAGEN_MSK          (1<<CFGWORD_JTAGEN_POS)

#define FLASH_START_ADDRESS 		0x80000000
#define USER_JUMP_ADDRESS 			(FLASH_START_ADDRESS + BOOT_FLASH_SIZE_TOTAL_BYTES)

typedef enum {
    FLASH_MAIN = 0,
    FLASH_NVR = 1
} FlashType_TypeDef;

typedef enum {
    FLASH_RD = FLASH_CMD_RD_Msk,
    FLASH_WR = FLASH_CMD_WR_Msk,
    FLASH_ERSEC = FLASH_CMD_ERSEC_Msk,
    FLASH_ALLSEC = FLASH_CMD_ERSEC_Msk | FLASH_CMD_ALLSEC_Msk
} FlashCmd_TypeDef;

/**
 * \brief           Read 4x32-bit data (16 byte) from flash memory
 * \param[in]       addr: flash memory address 
 * \param[in]       ftype: Type of flash memory
 * \param[out]      data: array with size 4
 */ 
 void flash_read(uint32_t addr, FlashType_TypeDef ftype, uint32_t* data);

/**
 * \brief           Write 4x32-bit data (16 byte) to flash memory
 * \param[in]       addr: flash memory address 
 * \param[in]       ftype: Type of flash memory
 * \param[in]      data: array with size 4
 */ 
 void flash_write(uint32_t addr, FlashType_TypeDef ftype, const uint32_t* data);

/**
 * \brief           Erase page of flash memory
 * \param[in]       addr: flash memory address 
 * \param[in]       ftype: Type of flash memory
 */
 void flash_erase_page(uint32_t addr, FlashType_TypeDef ftype);

/**
 * \brief           Full erase of flash memory
 */
 void flash_erase_full();

/**
 * \brief           Disabling startup from boot memory after the next software reset
 */
 void flash_disable_boot();

#endif //BOOT_FLASH_H
