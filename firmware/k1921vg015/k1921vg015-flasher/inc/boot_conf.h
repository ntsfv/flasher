/*==============================================================================
 * UART загрузчик для К1921ВГ015
 *
 * Общий файл конфигурации загрузчика: глобальные константы, общие макросы, типы
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

#ifndef BOOT_CONF_H
#define BOOT_CONF_H

#include <stdio.h>
#include "K1921VG015.h"
#include "plic.h"
#include "stringify.h"

#define CONCAT(x,y) _CONCAT(x,y)

//Global configuration
#define BOOT_VER_MAJOR  0x0001
#define BOOT_VER_MINOR  0x0001
#define BOOT_VER        ((BOOT_VER_MAJOR<<16)|BOOT_VER_MINOR)
#define BOOT_NAME       "K1921VG015_BOOTLOADER"
#define SYSCLK          50000000


/**
 * \note           BOOTEN pin used for activate bootloader 
 */
#ifndef BOOTEN_PORT_LETTER
	#define BOOTEN_PORT_LETTER A
#endif
#ifndef BOOTEN_PIN_NUMBER
	#define BOOTEN_PIN_NUMBER 6
#endif
#define BOOTEN_PORT CONCAT(GPIO, BOOTEN_PORT_LETTER)	/*!< Port of  BOOTEN pin */
#define BOOTEN_PORT_EN CONCAT(RCU_CGCFGAHB_GPIO, CONCAT(BOOTEN_PORT_LETTER, EN_Msk))
#define BOOTEN_PIN_POS BOOTEN_PIN_NUMBER /*!< Pin num of BOOTEN pin */
#define BOOTEN_PIN_MSK (1 << BOOTEN_PIN_POS) /*!< Pin num of BOOTEN pin */

/**
 * \note			BOOTLED pin used for information
 */
#ifndef BOOTLED_PORT_LETTER
	#define BOOTLED_PORT_LETTER A
#endif
#ifndef BOOTLED_PIN_NUMBER
	#define BOOTLED_PIN_NUMBER 12
#endif
#ifndef BOOTLED_ALTFUNC_NUMBER
#define BOOTLED_ALTFUNC_NUMBER 2
#endif
#define BOOTLED_PORT CONCAT(GPIO, BOOTLED_PORT_LETTER)	/*!< Port of  BOOTLED pin */
#define BOOTLED_PORT_EN CONCAT(RCU_CGCFGAHB_GPIO, CONCAT(BOOTLED_PORT_LETTER, EN_Msk))
#define BOOTLED_PIN_POS BOOTLED_PIN_NUMBER /*!< Pin num of BOOTLED pin */
#define BOOTLED_PIN_MSK (1 << BOOTLED_PIN_POS) /*!< Pin num of BOOTLED pin */
#define BOOTLED_ALTFUNC CONCAT(CONCAT(GPIO_ALTFUNCNUM_PIN, BOOTLED_PIN_NUMBER), CONCAT(_AF, BOOTLED_ALTFUNC_NUMBER))
/**
 * \note			BOOTLED timer
 */
#ifndef BOOTLED_TMR_NUMBER
	#define  BOOTLED_TMR_NUMBER 2
#endif
#define BOOTLED_TMR CONCAT(TMR, BOOTLED_TMR_NUMBER)
#define BOOTLED_TMR_EN_Msk CONCAT(RCU_CGCFGAPB_TMR, CONCAT(BOOTLED_TMR_NUMBER, EN_Msk))
#define BOOTLED_IRQn CONCAT(IsrVect_IRQ_TMR, BOOTLED_TMR_NUMBER)

//Debug
#ifndef DEBUG_PORT_LETTER
	#define DEBUG_PORT_LETTER A
#endif
#ifndef DEBUG_PORT_PIN_NUMBER
	#define DEBUG_PORT_PIN_NUMBER 7
#endif
#define DEBUG_PORT        CONCAT(GPIO, DEBUG_PORT_LETTER)
#define DEBUG_PORT_EN     CONCAT(RCU_CGCFGAHB_GPIO, CONCAT(DEBUG_PORT_LETTER, EN_Msk))
#define DEBUG_INFO_POS    DEBUG_PORT_PIN_NUMBER
#define DEBUG_INFO_MSK    (0xFF)
#define DEBUG_INFO        DEBUG_PORT->DATAOUT
#if defined (DEBUG)
    #define DEBUG_PRINT(MSG)   DEBUG_INFO = MSG<<DEBUG_INFO_POS
#else
    #define DEBUG_PRINT(MSG)    ((void)0);
#endif

#define LED0_MSK    (1 << 12)
#define LED1_MSK    (1 << 13)
#define LED2_MSK    (1 << 14)
#define LED3_MSK    (1 << 15)

/**
 * \brief           UART for communicate with HOST
 */
#define UART_NUMBER			0
#define UART                UART0
#define UART_PORT           GPIOA
#define UART_PORT_EN        RCU_CGCFGAHB_GPIOAEN_Msk
#define UART_PIN_RX_POS     0
#define UART_PIN_TX_POS     1
#define UART_PINS_MSK       ((1<<UART_PIN_RX_POS) | (1<<UART_PIN_TX_POS))
#define UART_RX_IRQn        IsrVect_IRQ_UART0

#ifndef UART_TIMEOUT_MS
	#define UART_TIMEOUT_MS        100
#endif

/**
 * \brief           Timer for calculate uart speed
 */
#define UART_TMR TMR1
#define UART_TMR_EN_Msk RCU_CGCFGAPB_TMR1EN_Msk

/**
 * \brief           Timer for timeout 
 */
#define TIMEOUT_TMR TMR32
#define TIMEOUT_TMR_EN_Msk RCU_CGCFGAPB_TMR32EN_Msk

/**
 * \brief           Packet parser values
 */
#define PACKET_FIFO_BYTES       8192
#define PACKET_HOST_SIGN        0x5C81
#define PACKET_DEVICE_SIGN      0x7EA3
#define PACKET_EMPTY_DATA       0x55
#define PACKET_TMP_DATA_BYTES   (4096+8)

#endif //BOOT_CONF_H
