/*==============================================================================
 * UART загрузчик для К1921ВГ015
 *
 * Функции работы с флеш-памятью.
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

#include "boot_flash.h"

//-- Private functions ---------------------------------------------------------
static  void flash_cmd(uint32_t addr, FlashType_TypeDef ftype, uint32_t* data, FlashCmd_TypeDef cmd)
{
  __asm__ volatile("nop");
  __asm__ volatile("nop");
  while (FLASH->STAT_bit.BUSY) {
    };
    FLASH->ADDR = addr;
    if (cmd == FLASH_WR) {
        FLASH->DATA[0].DATA = (uint32_t) data[0];
        FLASH->DATA[1].DATA = (uint32_t) data[1];
        FLASH->DATA[2].DATA = (uint32_t) data[2];
        FLASH->DATA[3].DATA = (uint32_t) data[3];
    }
    FLASH->CMD = FLASH_MAGICKEY_CONST << FLASH_CMD_KEY_Pos |
                  cmd | ftype << FLASH_CMD_NVRON_Pos;
    if (cmd == FLASH_RD) {
        while (FLASH->STAT_bit.BUSY) {
        };
        data[0] = FLASH->DATA[0].DATA;
        data[1] = FLASH->DATA[1].DATA;
        data[2] = FLASH->DATA[2].DATA;
        data[3] = FLASH->DATA[3].DATA;
    }
}

void flash_read(uint32_t addr, FlashType_TypeDef ftype, uint32_t* data)
{
    flash_cmd(addr, ftype, data, FLASH_RD);
}

 void flash_write(uint32_t addr, FlashType_TypeDef ftype, const uint32_t* data)
{
    flash_cmd(addr, ftype, (uint32_t*)data, FLASH_WR);
    //~42.5us
}

void flash_erase_page(uint32_t addr, FlashType_TypeDef ftype)
{
    flash_cmd(addr, ftype, NULL, FLASH_ERSEC);
    //~160ms
}

void flash_erase_full()
{
    flash_cmd(0, FLASH_MAIN, NULL, FLASH_ALLSEC);
    //~160ms
}


