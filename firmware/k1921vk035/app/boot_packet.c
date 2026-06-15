/*==============================================================================
 * UART загрузчик для К1921ВК035
 *
 * Функции работы с пакетами
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
#include "boot_packet.h"

//-- Variables -----------------------------------------------------------------
struct
{
    uint8_t mem[PACKET_FIFO_BYTES];
    int wr_ptr;
    int rd_ptr;
    volatile int count;
} packet_fifo;

int packet_fifo_full() {
  return PACKET_FIFO_BYTES == packet_fifo.count;
}

int packet_fifo_empty() {
  return 0 == packet_fifo.count;
}

//-- Functions -----------------------------------------------------------------
//Инициализация fifo
void packet_fifo_init()
{
    packet_fifo.wr_ptr = 0;
    packet_fifo.rd_ptr = 0;
    packet_fifo.count = 0;
}

//Чтение байта из пакетного fifo
uint8_t packet_fifo_read()
{
    uint8_t data = 0;

    while ( packet_fifo_empty() ) {};
    

    data = packet_fifo.mem[packet_fifo.rd_ptr];
    
    __disable_irq();
    
    --packet_fifo.count;
    
    __enable_irq();
    
    if ( ++packet_fifo.rd_ptr >= PACKET_FIFO_BYTES ) {
        packet_fifo.rd_ptr = 0;
    }
    

    return data;
}

//Побайтовый расчет CRC16
uint16_t crc_upd(uint16_t crc_in, uint8_t data)
{
    uint32_t crc = crc_in;
    uint32_t in = data | 0x100;

    do {
        crc <<= 1;
        in <<= 1;
        if (in & 0x100) {
          ++crc;
        }
        if (crc & 0x10000) {
          crc ^= 0x1021;
        }
    } while (!(in & 0x10000));

    return crc & 0xffffu;
}

//Поиск и прием пакетов
void packet_recieve(Packet_TypeDef* rx_packet)
{
    uint16_t rx_signature;
    uint8_t rx_cmd;
    uint8_t rx_cmd_inv;
    uint16_t rx_data_n;
    uint16_t pre_crc;

    //поиск сигнатуры
    rx_signature = 0x0000;
    while (rx_signature != PACKET_HOST_SIGN) {
        rx_signature = (rx_signature >> 8) | (uint16_t)(packet_fifo_read() << 8);
    }
    //считываем служебную инфмацию
    rx_cmd = packet_fifo_read();
    rx_cmd_inv = packet_fifo_read();
    rx_data_n = packet_fifo_read_u16();

    //проверяем корректность команды
    if ((rx_cmd ^ rx_cmd_inv) != 0xFF) {
        rx_packet->cmd_code = CMD_NONE;
        rx_packet->tmp_data8[0] = MSG_ERR_CMD;
    }
    //если все верно, то начинаем считать crc
    else {
        pre_crc = 0;
        pre_crc = crc_upd(pre_crc, rx_cmd);
        pre_crc = crc_upd(pre_crc, rx_cmd_inv);
        pre_crc = crc_upd_u16(pre_crc, rx_data_n);
        //передаем то что распарсили в ядро, crc досчитается и проверится уже там в обработчике конкретной команды
        rx_packet->cmd_code = rx_cmd;
        rx_packet->data_n = rx_data_n;
        rx_packet->crc = pre_crc;
    }
}

//Проверка статуса отправки текущего пакета
uint32_t packet_transmit_status_busy()
{
    return !UART->FR_bit.TXFE;
}

//Отправка исходящего пакета
void packet_transmit(Packet_TypeDef* tx_packet)
{
  uint16_t crc = 0;

  send_byte( PACKET_DEVICE_SIGN & 0x00FF );
  send_byte( (PACKET_DEVICE_SIGN & 0xFF00) >> 8 );

  send_byte( tx_packet->cmd_code );
  crc = crc_upd(crc, tx_packet->cmd_code);

  send_byte( ~tx_packet->cmd_code );
  crc = crc_upd(crc, ~tx_packet->cmd_code);

  send_byte( tx_packet->data_n & 0x00FF );
  send_byte( (tx_packet->data_n & 0xFF00) >> 8 );
  crc = crc_upd_u16(crc, tx_packet->data_n);

  for ( uint16_t i = 0; i < tx_packet->data_n; ++i ) {
    send_byte( tx_packet->tmp_data8[i] );
    //UART->ICR = UART_ICR_TXIC_Msk;
    crc = crc_upd(crc, tx_packet->tmp_data8[i]);
  }

  send_byte( crc & 0x00FF );
  send_byte( (crc & 0xFF00) >> 8 );
}

//Обертка для чтения 32-битных значений из пакетного fifo
uint32_t packet_fifo_read_u32()
{
    uint32_t data = packet_fifo_read() << 0;
    data |= packet_fifo_read() << 8;
    data |= packet_fifo_read() << 16;
    data |= packet_fifo_read() << 24;

    return data;
}

//Обертка для чтения 16-битных значений из пакетного fifo
uint16_t packet_fifo_read_u16()
{
    uint16_t data = 0;

    data = (uint16_t)(packet_fifo_read() << 0);
    data |= (uint16_t)(packet_fifo_read() << 8);

    return data;
}

//Обертка для расчета CRC16 для 32-битных данных
uint16_t crc_upd_u32(uint16_t crc_in, uint32_t data)
{
    crc_in = crc_upd( crc_in, data );
    crc_in = crc_upd( crc_in, data >> 8 );
    crc_in = crc_upd( crc_in, data >> 16 );
    crc_in = crc_upd( crc_in, data >> 24 );

    return crc_in;
}

//Обертка для расчета CRC16 для 16-битных данных
uint16_t crc_upd_u16(uint16_t crc_in, uint16_t data)
{
    crc_in = crc_upd( crc_in, data );
    crc_in = crc_upd( crc_in, data >> 8 );

    return crc_in;
}


void send_byte( uint8_t a_byte ) {
  while ( 0 != (UART->FR & UART_FR_TXFF_Msk) ) {};
  UART->DR = a_byte;
}


//-- Interrupt handlers --------------------------------------------------------
__attribute__ ((section(".data.text"),used))
void ih_UART1_RX_IRQ()
{
  while ( !UART->FR_bit.RXFE ) {
    if ( !packet_fifo_full() ) {
      packet_fifo.mem[packet_fifo.wr_ptr] = UART->DR;
      ++packet_fifo.count;
      if ( ++packet_fifo.wr_ptr >= PACKET_FIFO_BYTES ) {
        packet_fifo.wr_ptr = 0;
      }
    }
  }
  UART->ICR = UART_ICR_RXIC_Msk;
}
