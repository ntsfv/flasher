/*==============================================================================
 * Инициализация K1921VG3T
 *------------------------------------------------------------------------------
 * НИИЭТ, Александр Дыхно <dykhno@niiet.ru>
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

//-- Includes ------------------------------------------------------------------
#include "system_k1921vg3t.h"
#include "plic.h"
#include "K1921VG3T.h"

//-- Variables -----------------------------------------------------------------
uint32_t SystemCoreClock; // System Clock Frequency (Core Clock)
uint32_t Pll0Clock; // PLL0Clock Frequency
uint32_t Pll1Clock; // PLL1Clock Frequency
uint32_t Pll2Clock; // PLL1Clock Frequency
//-- Functions -----------------------------------------------------------------
void SystemCoreClockUpdate(void)
{
    SystemCoreClock = 0;     // При ошибке вычислений значения переменных будут равны нулю
    Pll0Clock = 0;
    Pll1Clock = 0;
    Pll2Clock = 0;

    uint8_t rdiv = RCU->PLLDIV_bit.RDIV + 1;
    uint8_t ndiv = RCU->PLLDIV_bit.NDIV;
    uint8_t div1a = RCU->PLLDIV_bit.DIV1A + 1;
    uint8_t div1b = RCU->PLLDIV_bit.DIV1B + 1;

    if (RCU->PLLCFG_bit.FOUTEN)        // Если PLL0 включен
    {
        if (RCU->PLLCFG_bit.ST)    // Если дробный делитель включен
        {
        	uint32_t n = ndiv;
        	Pll0Clock = (HSECLK_VAL * n) / (rdiv * div1a * div1b);
        } else {
        	uint32_t n = ndiv;
        	Pll0Clock = (HSECLK_VAL * n) / (rdiv * div1a * div1b);
        }
    }
    switch (RCU->CLKSTAT_bit.SRC) {        // Определение источника тактирования ядра
        case RCU_CLKSTAT_SRC_HSICLK:
            SystemCoreClock = HSICLK_VAL;
            break;
        case RCU_CLKSTAT_SRC_HSECLK:
            SystemCoreClock = HSECLK_VAL;
            break;
        case RCU_CLKSTAT_SRC_PLL0CLK:
            SystemCoreClock = Pll0Clock;
            break;
        case RCU_CLKSTAT_SRC_EXTCLK:
            SystemCoreClock = EXTCLK_VAL;
            break;

    }

    if (RCU->PLL[1].CFG_bit.FOUTEN)        // Если PLL1 включен
    {
        rdiv = RCU->PLL[1].DIV_bit.RDIV;
        ndiv = RCU->PLL[1].DIV_bit.NDIV;
        div1a = RCU->PLL[1].DIV_bit.DIV1A + 1;
        div1b = RCU->PLL[1].DIV_bit.DIV1B + 1;
        if (RCU->PLL[1].CFG_bit.ST)    // Если дробный делитель включен
        {
        	uint32_t n = ndiv;
        	Pll1Clock = (HSECLK_VAL * n) / (rdiv * div1a * div1b);
        } else {
        	uint32_t n = ndiv;
        	Pll1Clock = (HSECLK_VAL * n) / (rdiv * div1a * div1b);
        }
    }

    if (RCU->PLL[2].CFG_bit.FOUTEN)        // Если PLL2 включен
    {
        rdiv = RCU->PLL[2].DIV_bit.RDIV;
        ndiv = RCU->PLL[2].DIV_bit.NDIV;
        div1a = RCU->PLL[2].DIV_bit.DIV1A + 1;
        div1b = RCU->PLL[2].DIV_bit.DIV1B + 1;
        if (RCU->PLL[2].CFG_bit.ST)    // Если дробный делитель включен
        {
        	uint32_t n = ndiv;
        	Pll2Clock = (HSECLK_VAL * n) / (rdiv * div1a * div1b);
        } else {
        	uint32_t n = ndiv;
        	Pll2Clock = (HSECLK_VAL * n) / (rdiv * div1a * div1b);
        }
    }
}

void ClkInit()
{
    uint32_t timeout_counter = 0;
    uint32_t sysclk_source;

    //clockout control
    #ifndef CKO_NONE
        //D11 clockout
        RCU->CGCFGAHB_bit.GPIODEN = 1;
        RCU->RSTDISAHB_bit.GPIODEN = 1;
        GPIOD->ALTFUNCNUM_bit.PIN11 = 3;
        GPIOD->ALTFUNCSET_bit.PIN11 = 1;
    #endif

    #if defined CKO_HSI
        RCU->CLKOUTCFG = (RCU_CLKOUTCFG_CLKSEL_HSI << RCU_CLKOUTCFG_CLKSEL_Pos) |
        				  (1 << RCU_CLKOUTCFG_DIVN_Pos) |
						  (0 << RCU_CLKOUTCFG_DIVEN_Pos) |
        				  RCU_CLKOUTCFG_RSTDIS_Msk | RCU_CLKOUTCFG_CLKEN_Msk; //CKO = HSICLK
    #elif defined CKO_HSE
        RCU->CLKOUTCFG = (RCU_CLKOUTCFG_CLKSEL_HSE << RCU_CLKOUTCFG_CLKSEL_Pos) |
				  	  	  (1 << RCU_CLKOUTCFG_DIVN_Pos) |
						  (0 << RCU_CLKOUTCFG_DIVEN_Pos) |
						  RCU_CLKOUTCFG_RSTDIS_Msk | RCU_CLKOUTCFG_CLKEN_Msk; //CKO = HSECLK
    #elif defined CKO_PLL0
        RCU->CLKOUTCFG = (RCU_CLKOUTCFG_CLKSEL_PLL0 << RCU_CLKOUTCFG_CLKSEL_Pos) |
				  	  	  (1 << RCU_CLKOUTCFG_DIVN_Pos) |
						  (1 << RCU_CLKOUTCFG_DIVEN_Pos) |
						  RCU_CLKOUTCFG_RSTDIS_Msk | RCU_CLKOUTCFG_CLKEN_Msk; //CKO = PLL0CLK
    #elif defined CKO_RTC
        RCU->CLKOUTCFG = (RCU_CLKOUTCFG_CLKSEL_RTC << RCU_CLKOUTCFG_CLKSEL_Pos) |
				  	  	  (1 << RCU_CLKOUTCFG_DIVN_Pos) |
						  (0 << RCU_CLKOUTCFG_DIVEN_Pos) |
						  RCU_CLKOUTCFG_RSTDIS_Msk | RCU_CLKOUTCFG_CLKEN_Msk; //CKO = LSICLK
    #endif

//select system clock
#ifdef SYSCLK_PLL
	//PLLCLK = REFCLK * (FBDIV+FRAC/2^24) / (REFDIV*(1+PD0A)*(1+PD0B))
	
	//select HSE as source system clock while config PLL
	RCU->SYSCLKCFG = (RCU_SYSCLKCFG_SRC_HSECLK << RCU_SYSCLKCFG_SRC_Pos);
    // Wait switching done
    timeout_counter = 0;
    while ((RCU->CLKSTAT_bit.SRC != RCU->SYSCLKCFG_bit.SRC) && (timeout_counter < 100)){ //SYSCLK_SWITCH_TIMEOUT))
        timeout_counter++;
    }  						  
#if (HSECLK_VAL == 10000000)
    //FOUT = 120 000 000 Hz  from 10 MHz HSE
    // RCU->PLLDIV is equivalent for RCU->PLL[0].DIV
    RCU->PLLDIV = ( 1 << RCU_PLLDIV_DIV1A_Pos ) |
                  ( 1 << RCU_PLLDIV_DIV1B_Pos ) |
                  ( 1 << RCU_PLLDIV_PREDIV_Pos) |
                  ( 1 << RCU_PLLDIV_NNCLR_Pos ) |             // N-divider enable
                  ( 1 << RCU_PLLDIV_RNCLR_Pos ) |             // R-divider enable
                  ( 1 << RCU_PLLDIV_RDIV_Pos  ) |
                  (96 << RCU_PLLDIV_NDIV_Pos );
	RCU->PLLMOD  = (1 << RCU_PLLFRAC_FRAC_Pos );
	RCU->PLLFRAC = (1 << RCU_PLLMOD_MOD_Pos   );
	RCU->PLLCFG  = (1 << RCU_PLLCFG_FOUTEN_Pos ) |			// Fout enable
			       (3 << RCU_PLLCFG_PFD_Pos    ) |
			       (0 << RCU_PLLCFG_CLKSEL_Pos ) |
			       (1 << RCU_PLLCFG_VCOMODE_Pos) |
			       (0 << RCU_PLLCFG_ST_Pos) ;				  // ST = 0 for integer divider
#elif (HSECLK_VAL == 12000000)
    //FOUT = 120 000 000 Hz  from 12 MHz HSE
    // RCU->PLLDIV is equivalent for RCU->PLL[0].DIV
    RCU->PLLDIV = ( 1 << RCU_PLLDIV_DIV1A_Pos ) |
                  ( 1 << RCU_PLLDIV_DIV1B_Pos ) |             // DIV1B + 1
                  ( 1 << RCU_PLLDIV_PREDIV_Pos) |
                  ( 1 << RCU_PLLDIV_NNCLR_Pos ) |             // N-divider enable
                  ( 1 << RCU_PLLDIV_RNCLR_Pos ) |             // R-divider enable
                  ( 2 << RCU_PLLDIV_RDIV_Pos  ) |
                  (120 << RCU_PLLDIV_NDIV_Pos );
	RCU->PLLMOD  = (1 << RCU_PLLFRAC_FRAC_Pos );
	RCU->PLLFRAC = (1 << RCU_PLLMOD_MOD_Pos   );
	RCU->PLLCFG  = (1 << RCU_PLLCFG_FOUTEN_Pos ) |			// Fout enable
			       (3 << RCU_PLLCFG_PFD_Pos    ) |
			       (0 << RCU_PLLCFG_CLKSEL_Pos ) |
			       (1 << RCU_PLLCFG_VCOMODE_Pos) |
			       (0 << RCU_PLLCFG_ST_Pos) ;				  // ST = 0 for integer divider
#elif (HSECLK_VAL == 16000000)
    //FOUT = 120 000 000 Hz  from 16 MHz HSE
    // RCU->PLLDIV is equivalent for RCU->PLL[0].DIV
    RCU->PLLDIV = ( 1 << RCU_PLLDIV_DIV1A_Pos ) |
                  ( 1 << RCU_PLLDIV_DIV1B_Pos ) |
                  ( 1 << RCU_PLLDIV_PREDIV_Pos) |
                  ( 1 << RCU_PLLDIV_NNCLR_Pos ) |             // N-divider enable
                  ( 1 << RCU_PLLDIV_RNCLR_Pos ) |             // R-divider enable
                  ( 3 << RCU_PLLDIV_RDIV_Pos  ) |
                  (100 << RCU_PLLDIV_NDIV_Pos );
	RCU->PLLMOD  = (1 << RCU_PLLFRAC_FRAC_Pos );
	RCU->PLLFRAC = (1 << RCU_PLLMOD_MOD_Pos   );
	RCU->PLLCFG  = (1 << RCU_PLLCFG_FOUTEN_Pos ) |			// Fout enable
			       (3 << RCU_PLLCFG_PFD_Pos    ) |
			       (0 << RCU_PLLCFG_CLKSEL_Pos ) |
			       (1 << RCU_PLLCFG_VCOMODE_Pos) |
			       (0 << RCU_PLLCFG_ST_Pos) ;				  // ST = 0 for integer divider

#elif (HSECLK_VAL == 20000000)
    //FOUT = 120 000 000 Hz  from 20 MHz HSE
    // RCU->PLLDIV is equivalent for RCU->PLL[0].DIV
    RCU->PLLDIV = ( 1 << RCU_PLLDIV_DIV1A_Pos ) |
                  ( 1 << RCU_PLLDIV_DIV1B_Pos ) |
                  ( 1 << RCU_PLLDIV_PREDIV_Pos) |
                  ( 1 << RCU_PLLDIV_NNCLR_Pos ) |             // N-divider enable
                  ( 1 << RCU_PLLDIV_RNCLR_Pos ) |             // R-divider enable
                  ( 4 << RCU_PLLDIV_RDIV_Pos  ) |
                  (120 << RCU_PLLDIV_NDIV_Pos );
	RCU->PLLMOD  = (1 << RCU_PLLFRAC_FRAC_Pos );
	RCU->PLLFRAC = (1 << RCU_PLLMOD_MOD_Pos   );
	RCU->PLLCFG  = (1 << RCU_PLLCFG_FOUTEN_Pos ) |			// Fout enable
			       (3 << RCU_PLLCFG_PFD_Pos    ) |
			       (0 << RCU_PLLCFG_CLKSEL_Pos ) |
			       (1 << RCU_PLLCFG_VCOMODE_Pos) |
			       (0 << RCU_PLLCFG_ST_Pos) ;				  // ST = 0 for integer divider
#elif (HSECLK_VAL == 24000000)
    //FOUT = 120 000 000 Hz  from 24 MHz HSE
    // RCU->PLLDIV is equivalent for RCU->PLL[0].DIV
    RCU->PLLDIV = ( 1 << RCU_PLLDIV_DIV1A_Pos ) |
                  ( 1 << RCU_PLLDIV_DIV1B_Pos ) |
                  ( 1 << RCU_PLLDIV_PREDIV_Pos) |
                  ( 1 << RCU_PLLDIV_NNCLR_Pos ) |             // N-divider enable
                  ( 1 << RCU_PLLDIV_RNCLR_Pos ) |             // R-divider enable
                  ( 5 << RCU_PLLDIV_RDIV_Pos  ) |
                  (120 << RCU_PLLDIV_NDIV_Pos );
	RCU->PLLMOD  = (1 << RCU_PLLFRAC_FRAC_Pos );
	RCU->PLLFRAC = (1 << RCU_PLLMOD_MOD_Pos   );
	RCU->PLLCFG  = (1 << RCU_PLLCFG_FOUTEN_Pos ) |			// Fout enable
			       (3 << RCU_PLLCFG_PFD_Pos    ) |
			       (0 << RCU_PLLCFG_CLKSEL_Pos ) |
			       (1 << RCU_PLLCFG_VCOMODE_Pos) |
			       (0 << RCU_PLLCFG_ST_Pos) ;				  // ST = 0 for integer divider
#else
#error "Please define HSECLK_VAL with correct values!"
#endif
	//select PLL as source system clock
	sysclk_source = RCU_SYSCLKCFG_SRC_PLL0CLK;
    // FLASH control settings
    FLASH->CTRL_bit.LAT = 2;
    // enable/init caches
    //cache_enable(1,0); // Cash enable for Flash

#elif defined SYSCLK_HSI
    sysclk_source = RCU_SYSCLKCFG_SRC_HSICLK;
#elif defined SYSCLK_HSE
    sysclk_source = RCU_SYSCLKCFG_SRC_HSECLK;
#elif defined SYSCLK_LSI
    sysclk_source = RCU_SYSCLKCFG_SRC_LSICLK;
#else
#error "Please define SYSCLK source (SYSCLK_PLL | SYSCLK_HSE | SYSCLK_HSI | SYSCLK_EXT)!"
#endif

    //switch sysclk
    RCU->SYSCLKCFG = (sysclk_source << RCU_SYSCLKCFG_SRC_Pos);
    // Wait switching done
    timeout_counter = 0;
    while ((RCU->CLKSTAT_bit.SRC != RCU->SYSCLKCFG_bit.SRC) && (timeout_counter < 100)) //SYSCLK_SWITCH_TIMEOUT))
        timeout_counter++;
/*    if (timeout_counter == SYSCLK_SWITCH_TIMEOUT) //SYSCLK failed to switch
        while (1) {
        };*/

}

void InterruptEnable()
{
	//allow all interrupts in machine mode
	PLIC_SetThreshold (Plic_Mach_Target, 0); //allow all interrupts in machine mode
    // disable timer interrupt
    clear_csr(mie, MIE_MTIMER);
    // enable machine external interrupt
    set_csr(mie, MIE_MEXTERNAL);
    // enable global interrupts
    set_csr(mstatus, MSTATUS_MIE);
}

void InterruptDisable()
{
	//disable all interrupts in machine mode
	PLIC_SetThreshold (Plic_Mach_Target, 7); //Disable all interrupts in machine mode
    // disable machine external interrupt
    clear_csr(mie, MIE_MEXTERNAL);
    // disable global interrupts
    clear_csr(mstatus, MSTATUS_MIE);
}

void SystemInit(void)
{
	// PLIC configuration
	// disable timer interrupt
//	clear_csr(mie, MIE_MTIMER);
	// enable machine external interrupt
//	set_csr(mie, MIE_MEXTERNAL);
	// enable global interrupts
//	set_csr(mstatus, MSTATUS_MIE);
	ClkInit();
}

