#include "vectors.h"

__attribute__((weak)) void ih_NMI() {}
__attribute__((weak)) void ih_HardFault() {}
__attribute__((weak)) void ih_MemManage() {}
__attribute__((weak)) void ih_BusFault() {}
__attribute__((weak)) void ih_UsageFault() {}
__attribute__((weak)) void ih_SVC() {}
__attribute__((weak)) void ih_DebugMon() {}
__attribute__((weak)) void ih_PendSV() {}
__attribute__((weak)) void ih_SysTick() {}


__attribute__((weak)) void ih_WDT_IRQ() {}
__attribute__((weak)) void ih_RCU_IRQ() {}
__attribute__((weak)) void ih_MFLASH_IRQ() {}
__attribute__((weak)) void ih_GPIOA_IRQ() {}
__attribute__((weak)) void ih_GPIOB_IRQ() {}
__attribute__((weak)) void ih_DMA_CH0_IRQ() {}
__attribute__((weak)) void ih_DMA_CH1_IRQ() {}
__attribute__((weak)) void ih_DMA_CH2_IRQ() {}
__attribute__((weak)) void ih_DMA_CH3_IRQ() {}
__attribute__((weak)) void ih_DMA_CH4_IRQ() {}
__attribute__((weak)) void ih_DMA_CH5_IRQ() {}
__attribute__((weak)) void ih_DMA_CH6_IRQ() {}
__attribute__((weak)) void ih_DMA_CH7_IRQ() {}
__attribute__((weak)) void ih_DMA_CH8_IRQ() {}
__attribute__((weak)) void ih_DMA_CH9_IRQ() {}
__attribute__((weak)) void ih_DMA_CH10_IRQ() {}
__attribute__((weak)) void ih_DMA_CH11_IRQ() {}
__attribute__((weak)) void ih_DMA_CH12_IRQ() {}
__attribute__((weak)) void ih_DMA_CH13_IRQ() {}
__attribute__((weak)) void ih_DMA_CH14_IRQ() {}
__attribute__((weak)) void ih_DMA_CH15_IRQ() {}
__attribute__((weak)) void ih_TMR0_IRQ() {}
__attribute__((weak)) void ih_TMR1_IRQ() {}
__attribute__((weak)) void ih_TMR2_IRQ() {}
__attribute__((weak)) void ih_TMR3_IRQ() {}
__attribute__((weak)) void ih_UART0_TD_IRQ() {}
__attribute__((weak)) void ih_UART0_RX_IRQ() {}
__attribute__((weak)) void ih_UART0_TX_IRQ() {}
__attribute__((weak)) void ih_UART0_IRQ() {}
__attribute__((weak)) void ih_UART1_TD_IRQ() {}
__attribute__((weak)) void ih_UART1_RX_IRQ() {}
__attribute__((weak)) void ih_UART1_TX_IRQ() {}
/*
__attribute__((weak)) void ih_UART1_IRQ() {}
__attribute__((weak)) void ih_SPI_IRQ() {}
__attribute__((weak)) void ih_SPI_RX_IRQ() {}
__attribute__((weak)) void ih_SPI_TX_IRQ() {}
__attribute__((weak)) void ih_I2C_IRQ() {}
__attribute__((weak)) void ih_ECAP0_IRQ() {}
__attribute__((weak)) void ih_ECAP1_IRQ() {}
__attribute__((weak)) void ih_ECAP2_IRQ() {}
__attribute__((weak)) void ih_PWM0_IRQ() {}
__attribute__((weak)) void ih_PWM0_HD_IRQ() {}
__attribute__((weak)) void ih_PWM0_TZ_IRQ() {}
__attribute__((weak)) void ih_PWM1_IRQ() {}
__attribute__((weak)) void ih_PWM1_HD_IRQ() {}
__attribute__((weak)) void ih_PWM1_TZ_IRQ() {}
__attribute__((weak)) void ih_PWM2_IRQ() {}
__attribute__((weak)) void ih_PWM2_HD_IRQ() {}
__attribute__((weak)) void ih_PWM2_TZ_IRQ() {}
__attribute__((weak)) void ih_QEP_IRQ() {}
__attribute__((weak)) void ih_ADC_SEQ0_IRQ() {}
__attribute__((weak)) void ih_ADC_SEQ1_IRQ() {}
__attribute__((weak)) void ih_ADC_DC_IRQ() {}
__attribute__((weak)) void ih_CAN0_IRQ() {}
__attribute__((weak)) void ih_CAN1_IRQ() {}
__attribute__((weak)) void ih_CAN2_IRQ() {}
__attribute__((weak)) void ih_CAN3_IRQ() {}
__attribute__((weak)) void ih_CAN4_IRQ() {}
__attribute__((weak)) void ih_CAN5_IRQ() {}
__attribute__((weak)) void ih_CAN6_IRQ() {}
__attribute__((weak)) void ih_CAN7_IRQ() {}
__attribute__((weak)) void ih_CAN8_IRQ() {}
__attribute__((weak)) void ih_CAN9_IRQ() {}
__attribute__((weak)) void ih_CAN10_IRQ() {}
__attribute__((weak)) void ih_CAN11_IRQ() {}
__attribute__((weak)) void ih_CAN12_IRQ() {}
__attribute__((weak)) void ih_CAN13_IRQ() {}
__attribute__((weak)) void ih_CAN14_IRQ() {}
__attribute__((weak)) void ih_CAN15_IRQ() {}
__attribute__((weak)) void ih_FPU_IRQ() {}
*/

__attribute__ ((section(".isr_vector"),used))
IntFunc exception_table[VECTORS_COUNT] = {
  
// самый хвост ОЗУ
	(IntFunc)0x20004000
// специфичные для Cortex-M4 прерывания
, _start // Reset Handler
, ih_NMI
, ih_HardFault
, ih_MemManage
, ih_BusFault
, ih_UsageFault
, 0
, 0
, 0
, 0
, ih_SVC
, ih_DebugMon
, 0
, ih_PendSV
, ih_SysTick
// специфичные для контроллера прерывания
, ih_WDT_IRQ
, ih_RCU_IRQ
, ih_MFLASH_IRQ
, ih_GPIOA_IRQ
, ih_GPIOB_IRQ
, ih_DMA_CH0_IRQ
, ih_DMA_CH1_IRQ
, ih_DMA_CH2_IRQ
, ih_DMA_CH3_IRQ
, ih_DMA_CH4_IRQ
, ih_DMA_CH5_IRQ
, ih_DMA_CH6_IRQ
, ih_DMA_CH7_IRQ
, ih_DMA_CH8_IRQ
, ih_DMA_CH9_IRQ
, ih_DMA_CH10_IRQ
, ih_DMA_CH11_IRQ
, ih_DMA_CH12_IRQ
, ih_DMA_CH13_IRQ
, ih_DMA_CH14_IRQ
, ih_DMA_CH15_IRQ
, ih_TMR0_IRQ
, ih_TMR1_IRQ
, ih_TMR2_IRQ
, ih_TMR3_IRQ
, ih_UART0_TD_IRQ
, ih_UART0_RX_IRQ
, ih_UART0_TX_IRQ
, ih_UART0_IRQ
, ih_UART1_TD_IRQ
, ih_UART1_RX_IRQ
, ih_UART1_TX_IRQ
/*
, ih_UART1_IRQ
, ih_SPI_IRQ
, ih_SPI_RX_IRQ
, ih_SPI_TX_IRQ
, ih_I2C_IRQ
, ih_ECAP0_IRQ
, ih_ECAP1_IRQ
, ih_ECAP2_IRQ
, ih_PWM0_IRQ
, ih_PWM0_HD_IRQ
, ih_PWM0_TZ_IRQ
, ih_PWM1_IRQ
, ih_PWM1_HD_IRQ
, ih_PWM1_TZ_IRQ
, ih_PWM2_IRQ
, ih_PWM2_HD_IRQ
, ih_PWM2_TZ_IRQ
, ih_QEP_IRQ
, ih_ADC_SEQ0_IRQ
, ih_ADC_SEQ1_IRQ
, ih_ADC_DC_IRQ
, ih_CAN0_IRQ
, ih_CAN1_IRQ
, ih_CAN2_IRQ
, ih_CAN3_IRQ
, ih_CAN4_IRQ
, ih_CAN5_IRQ
, ih_CAN6_IRQ
, ih_CAN7_IRQ
, ih_CAN8_IRQ
, ih_CAN9_IRQ
, ih_CAN10_IRQ
, ih_CAN11_IRQ
, ih_CAN12_IRQ
, ih_CAN13_IRQ
, ih_CAN14_IRQ
, ih_CAN15_IRQ
, ih_FPU_IRQ
*/
};
