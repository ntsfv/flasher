/*==============================================================================
 * UART загрузчик для К1921ВК035
 *
 * Первичная настройка периферии и переход на исполнение ядра загрузчика из ОЗУ
 *------------------------------------------------------------------------------
 * НИИЭТ, Богдан Колбов <kolbov@niiet.ru>
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
 *                              2018 АО "НИИЭТ"
 *==============================================================================
 */

//-- Includes ------------------------------------------------------------------
#include "boot_core.h"

//-- Init functions ------------------------------------------------------------
void some_stuck() {
  for( volatile int i = 0; i < 10000; ++i ) {}
}


void ClockInit()
{
    // Переводим системную частоту на HSI
    RCU->SYSCLKCFG = RCU_SYSCLKCFG_SYSSEL_OSICLK;
    //
    some_stuck();
    //Настраиваем PLL на 100 МГц (от внешних 8 МГц)
    RCU->PLLCFG = (RCU_PLLCFG_REFSRC_OSECLK << RCU_PLLCFG_REFSRC_Pos) 
                | (1 << RCU_PLLCFG_N_Pos)
                | (25 << RCU_PLLCFG_M_Pos)
                | (1 << RCU_PLLCFG_OD_Pos)
                | (1 << RCU_PLLCFG_OUTEN_Pos)
                ;
    //
    some_stuck();
    //Ждем пока PLL стабилизируется
    while (!RCU->PLLCFG_bit.LOCK) {}
    //
    RCU->PLLCFG |= (1 << RCU_PLLCFG_OUTEN_Pos);
    // Устанавливаем количество waitstate
    MFLASH->CTRL = 4 << MFLASH_CTRL_LAT_Pos;
    // Переводим системную частоту на PLL
    RCU->SYSCLKCFG = RCU_SYSCLKCFG_SYSSEL_PLLCLK;
}

static void UartInit()
{
    RCU->HCLKCFG |= UART_PORT_EN;
    RCU->HRSTCFG |= UART_PORT_EN;
    UART_PORT->ALTFUNCSET = UART_PINS_MSK;
    UART_PORT->DENSET = UART_PINS_MSK;

    RCU->UARTCFG[UART_NUM].UARTCFG = (RCU_UARTCFG_UARTCFG_CLKSEL_PLLCLK << RCU_UARTCFG_UARTCFG_CLKSEL_Pos) |
                                     (1 << RCU_UARTCFG_UARTCFG_CLKEN_Pos) |
                                     (1 << RCU_UARTCFG_UARTCFG_RSTDIS_Pos);
    UART->IFLS = UART_IFLS_RXIFLSEL_Lvl18 << UART_IFLS_RXIFLSEL_Pos |
                 UART_IFLS_TXIFLSEL_Lvl12 << UART_IFLS_TXIFLSEL_Pos;
    UART->IMSC = UART_MIS_RXMIS_Msk;
    NVIC_EnableIRQ(UART_RX_IRQn);
}

static void TimerInit()
{
  RCU->PRSTCFG_bit.TMR_EN = 1;
  RCU->PCLKCFG_bit.TMR_EN = 1;
  TMR->LOAD = TMR_LOAD;
}

void PeriphInit()
{
  ClockInit();
  UartInit();
  TimerInit();
}


//-- Main ----------------------------------------------------------------------
int main()
{
  //выходим из загрузчика, если NMI не был активен при сбросе
  for ( int i = 0; i < 1000000 && 0 == TMR->LOAD; ++i ) {}
  if ( 0 == TMR->LOAD ) {
    boot_exit();
  }
  boot_core();
  return 0;
}


//-- IRQ handlers --------------------------------------------------------------
// NMI используется как BOOT нога, которая разрешает работу загрузчика.
// При этом, NMI нужно установить обратно в 1, чтобы загручик продолжил работу после инициализации -
// это можно сделать либо вручную, либо использовать RTS пин USB-UART.
void ih_NMI()
{
  if (0 == TMR->LOAD) { // TODO: перенести это в main для новых ревизий чипа (где будет человеский BOOT пин, на месте NMI)
    PeriphInit();
    boot_init();
  }
}


extern uint32_t _sidata, _sdata, _edata, _sbss, _ebss;

void _start() {
  // copy initialized data
  uint32_t * v_ptr = (uint32_t *)&_sidata;
  for ( uint32_t * i = (uint32_t *)&_sdata; i < (uint32_t *)&_edata; ++i ) {
    *i = *v_ptr++;
  }
  // zero initialized data
  for ( uint32_t * i = (uint32_t *)&_sbss; i < (uint32_t *)&_ebss; ++i ) {
    *i = 0;
  }
  main();
}
