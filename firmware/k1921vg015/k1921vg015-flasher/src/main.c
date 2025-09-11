/*==============================================================================
 * UART загрузчик для К1921ВГ015
 *
 * Первичная настройка периферии и переход на исполнение ядра загрузчика из ОЗУ
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

#include "boot_core.h"
#include "plic.h"
#include "boot_flash.h"
#include "csr.h"
#include "arch.h"
#include "boot_packet.h"


static void DebugInit(void)
{
#ifdef DEBUG
    // configure service outputs for output
    RCU->CGCFGAHB |= DEBUG_PORT_EN;
    RCU->RSTDISAHB |= DEBUG_PORT_EN;
    DEBUG_PORT->OUTENSET = DEBUG_INFO_MSK << 8;
#endif
}

static void ClockInit(void){
    //HSECLK = 16 MHz
    //Set up PLL at 50 MHz 
    RCU->PLLSYSCFG0_bit.REFDIV = 1;
    RCU->PLLSYSCFG0_bit.BYP = 0;
    RCU->PLLSYSCFG2_bit.FBDIV = 25;
    RCU->PLLSYSCFG1_bit.FRAC = 0;

    RCU->PLLSYSCFG0_bit.PLLEN = 1;
    RCU->PLLSYSCFG0_bit.DSMEN = 0;
    RCU->PLLSYSCFG0_bit.PD0A = 3;
    RCU->PLLSYSCFG0_bit.PD0B = 1;
    RCU->PLLSYSCFG0_bit.PD1A = 3;
    RCU->PLLSYSCFG0_bit.PD1B = 1;
    RCU->PLLSYSCFG0_bit.FOUTEN = 1;

    //Waiting for PLL to stabilize
    while (!RCU->PLLSYSSTAT_bit.LOCK);
    // Change system frequency to PLL
    RCU->SYSCLKCFG_bit.SRC = RCU_SYSCLKCFG_SRC_SYSPLL0CLK; //enable SYSPLL0CLK
}

static void UartInit(void){
	RCU->CGCFGAHB |= UART_PORT_EN;
	RCU->RSTDISAHB |= UART_PORT_EN;
	UART_PORT->ALTFUNCSET = UART_PINS_MSK;
	UART_PORT->ALTFUNCNUM =
         (1 << UART_PIN_TX_POS * 2) | (1 << UART_PIN_RX_POS * 2);

	RCU->CGCFGAPB |= (1 << (RCU_CGCFGAPB_UART0EN_Pos + UART_NUMBER));
	RCU->RSTDISAPB |= (1 << (RCU_RSTDISAPB_UART0EN_Pos + UART_NUMBER));
	RCU->UARTCLKCFG[UART_NUMBER].UARTCLKCFG_bit.CLKSEL = 2;
	RCU->UARTCLKCFG[UART_NUMBER].UARTCLKCFG_bit.CLKEN = 1;
	RCU->UARTCLKCFG[UART_NUMBER].UARTCLKCFG_bit.RSTDIS = 1;
	UART->IFLS  = UART_IFLS_TXIFLSEL_Lvl18 << UART_IFLS_RXIFLSEL_Pos |
    		 	   UART_IFLS_TXIFLSEL_Lvl18 << UART_IFLS_TXIFLSEL_Pos;
	UART->IMSC = UART_IMSC_RXIM_Msk;
	PLIC_SetIrqHandler (Plic_Mach_Target, UART_RX_IRQn, UART_IRQHandler);
    PLIC_SetPriority   (UART_RX_IRQn, 0x1);
    PLIC_IntEnable     (Plic_Mach_Target, UART_RX_IRQn);
}


void GpioInit(void){
    #ifdef BOOTEN
    RCU->CGCFGAHB  |= BOOTEN_PORT_EN;
    RCU->RSTDISAHB |= BOOTEN_PORT_EN;
    
    BOOTEN_PORT->PULLMODE |= 1 << (BOOTEN_PIN_POS * 2); // enable Pull Up
    #endif
}
void TimersInit(void){

    //tbd015

    RCU->CGCFGAPB |= UART_TMR_EN_Msk | TIMEOUT_TMR_EN_Msk;
    RCU->RSTDISAPB |= UART_TMR_EN_Msk | TIMEOUT_TMR_EN_Msk;
    UART_TMR->CTRL_bit.MODE = 0;
    UART_TMR->CTRL_bit.DIV = 0; //turn off divider
    UART_TMR->CTRL_bit.CLR = 1;

    TIMEOUT_TMR->CTRL_bit.MODE = 0;
    TIMEOUT_TMR->CTRL_bit.DIV = 0; //turn off divider
    TIMEOUT_TMR->CTRL_bit.CLR = 1;
}

void PeriphInit(void){
  //riscv_irq_init();
  //PLIC_Init();
    //allow all interrupts in machine mode
    PLIC_SetThreshold (Plic_Mach_Target, 0); //allow all interrupts in machine mode
    // disable timer interrupt
    clear_csr(mie, MIE_MTIMER);
    // enable machine external interrupt
    set_csr(mie, MIE_MEXTERNAL);
    // enable global interrupts
    set_csr(mstatus, MSTATUS_MIE);
  GpioInit();
  DebugInit();
  ClockInit();
  UartInit();
  TimersInit();
}

void enter_boot_mode() {
#ifdef BOOTEN
    RCU->CGCFGAHB  = BOOTEN_PORT_EN;
    RCU->RSTDISAHB = BOOTEN_PORT_EN;

    BOOTEN_PORT->PULLMODE = BOOTEN_PIN_MSK;

    if ((BOOTEN_PORT->DATA & BOOTEN_PIN_MSK) != 0) {
        __asm__ volatile("jr %0" : : "value" (USER_JUMP_ADDRESS));
    }
#endif
}

int main(void) {
    PeriphInit();

    if(boot_init() < 0) {
        boot_exit();
    }

    boot_core();

    return 0;

}
