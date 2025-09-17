/*==============================================================================
 * UART загрузчик для К1921ВГ015
 *
 * Ядро загрузчика.
 * Обработка полученных комманд и формирование исходящих пакетов.
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
#include "boot_flash.h"
#include "boot_packet.h"
#include <string.h>
#include <riscv-csr.h>


//-- Private variables ---------------------------------------------------------
static  uint8_t bootflash_program[BOOT_FLASH_SIZE_TOTAL_BYTES] __attribute__((section(".ramvars")));

//-- Private function prototypes -----------------------------------------------
static  void msg_cmd(Packet_TypeDef* packet);
static  void get_info_cmd(Packet_TypeDef* packet);
static  void get_cfgword_cmd(Packet_TypeDef* packet);
static  void set_cfgword_cmd(Packet_TypeDef* packet);
static  void read_page_cmd(Packet_TypeDef* packet);
static  void write_page_cmd(Packet_TypeDef* packet);
static  void jump_cmd(Packet_TypeDef* packet);
static  void erase_cmd(Packet_TypeDef* packet);
static  void exit_cmd(Packet_TypeDef* packet);
static  void memcpy_ramfunc(uint8_t* to, uint8_t* from, uint32_t size);
static  void memcpy_flash_ramfunc(uint32_t to_flash, uint32_t* from, uint32_t size);
static  void flash_write_128_ramfunc(uint32_t addr, uint32_t *data);
static  void flash_erase_full_ramfunc(void);
static  void save_and_erase_all_ramfunc(void);

int wait_uart_rx(uint32_t value){
//    uint32_t timeout_start;
//    TIMEOUT_TMR->CTRL_bit.MODE = 0;
//    TIMEOUT_TMR->CTRL_bit.CLR = 1;
//    timeout_start = TIMEOUT_TMR->COUNT;
//    TIMEOUT_TMR->CTRL_bit.MODE = 2;

    while (UART_PORT->MASKLB[1 << UART_PIN_RX_POS].MASKLB != value ) {
//        if((uint32_t)(TIMEOUT_TMR->COUNT - timeout_start) > (uint32_t)(SYSCLK / 1000 * UART_TIMEOUT_MS)) {
//            return -1;
//        }
    }
    return 0;
}
volatile uint32_t ticks_counted;
int boot_init()
{
    uint32_t ticks_counted;
    uint32_t baud_i;
    uint32_t baud_f;
    
    DEBUG_PRINT(0x01);

    //Waiting for the start bit - 0
    UART_TMR->CTRL_bit.CLR = 1;
    UART_TMR->COUNT = 0;
    wait_uart_rx(0);

//    if(wait_uart_rx(0) < 0){
//        return -1;
//    }

    //turn on timer
    //We are waiting for the start of a group of seven 1 (0x7F)
    UART_TMR->CTRL_bit.MODE = 2;
    wait_uart_rx(1);

//    if(wait_uart_rx(1) < 0){
//        return -1;
//    }

    ticks_counted = UART_TMR->COUNT;
    //Waiting for bit - 0
    wait_uart_rx(0);

//    if(wait_uart_rx(0) < 0){
//        return -1;
//    }

    ticks_counted = UART_TMR->COUNT - ticks_counted;
    UART_TMR->CTRL_bit.MODE = 0;
    //calculate baudrate
    baud_i = ticks_counted / (16 * 7);
    baud_f = (uint32_t)((ticks_counted / (16 * 7.0f) - baud_i) * 64 + 0.5f);

    //Waiting for stop bit - 1
    wait_uart_rx(1);

//    if(wait_uart_rx(1) < 0){
//        return -1;
//    }

    //turn on UART
    UART->IBRD = baud_i;
    UART->FBRD = baud_f;
    UART->LCRH = (1 << UART_LCRH_FEN_Pos) | (3 << UART_LCRH_WLEN_Pos);
    UART->CR = (1 << UART_CR_RXE_Pos) | (1 << UART_CR_TXE_Pos) | (1 << UART_CR_UARTEN_Pos);
    //transmit the device signature with bytes swapped
    UART->DR = (PACKET_DEVICE_SIGN & 0xFF00) >> 8;
    UART->DR = PACKET_DEVICE_SIGN & 0x00FF;

    return 0;
}

void boot_exit(uint32_t jumpaddr)
{
	/* Restore PLIC to known state: */
    //disable all interrupts
    csr_clr_bits_mstatus(MSTATUS_MIE_BIT_MASK);
    csr_clr_bits_mstatus(MSTATUS_MPIE_BIT_MASK);
    //PLIC_init(); //TODO
    /* Disable all interrupts: */
	csr_write_mie(0);

    // Disable periph
    RCU->CGCFGAHB = 0;
    RCU->CGCFGAPB = 0;
    RCU->RSTDISAHB = 0;
    RCU->RSTDISAPB = 0;
    RCU->UARTCLKCFG[0].UARTCLKCFG = 0;
    RCU->UARTCLKCFG[1].UARTCLKCFG = 0;
    RCU->UARTCLKCFG[2].UARTCLKCFG = 0;
    RCU->UARTCLKCFG[3].UARTCLKCFG = 0;
    RCU->UARTCLKCFG[4].UARTCLKCFG = 0;

    RCU->SYSCLKCFG_bit.SRC = RCU_SYSCLKCFG_SRC_HSECLK;
    while (RCU->CLKSTAT_bit.SRC != RCU_CLKSTAT_SRC_HSECLK) ;

    RCU->PLLSYSCFG0 = 0;


	/* Start executing from  after end of bootloader section: */
    __asm__ volatile("jr %0" : : "value" (jumpaddr));
    
    /*User application execution should now start and never return here.... */
}

__attribute__((noreturn)) void boot_core()
{
    Packet_TypeDef packet;

    DEBUG_PRINT(0x02);
    packet_fifo_init();
    //send a message about readiness to accept commands
    packet.cmd_code = CMD_NONE;
    packet.tmp_data8[0] = MSG_READY;
    msg_cmd(&packet);

    while (1) {
        packet_receive(&packet);
        DEBUG_PRINT(0x03);
        DEBUG_PRINT(packet.cmd_code);
        switch (packet.cmd_code) {
        // Get commands
        case CMD_GET_INFO:
            get_info_cmd(&packet);
            break;
        case CMD_GET_CFGWORD:
            get_cfgword_cmd(&packet);
            break;
        // Set commands
        case CMD_SET_CFGWORD:
           set_cfgword_cmd(&packet);
           break;
        // Jump commands
        case CMD_JUMP:
        	jump_cmd(&packet);
        	break;
        // Write commands
        case CMD_WRITE_PAGE:
            write_page_cmd(&packet);
            break;
        // Read commands
        case CMD_READ_PAGE:
            read_page_cmd(&packet);
            break;
        // Erase commands
        case CMD_ERASE_FULL:
            erase_cmd(&packet);
            break;
        case CMD_ERASE_PAGE:
            erase_cmd(&packet);
            break;
        // Exit
        case CMD_EXIT:
            exit_cmd(&packet);
            break;
        case CMD_NONE:
            msg_cmd(&packet);
            break;
        default:
            break;
        }
    }
}

void msg_cmd(Packet_TypeDef* packet)
{
    if (packet->cmd_code == CMD_NONE)
        packet->data_n = 4;
    packet->tmp_data8[1] = packet->cmd_code;
    packet->tmp_data8[2] = PACKET_EMPTY_DATA;
    packet->tmp_data8[3] = PACKET_EMPTY_DATA;
    packet->cmd_code = CMD_MSG;

    packet_transmit(packet);
}

void get_info_cmd(Packet_TypeDef* packet)
{
    uint16_t rx_crc;

    rx_crc = packet_fifo_read_u16();

    if (packet->crc != rx_crc) {
        packet->tmp_data8[0] = MSG_ERR_CRC;
        packet->data_n = 4;
    } else {
        packet->tmp_data8[0] = MSG_OK;
        packet->tmp_data32[1] = PMUSYS->CHIPID & 0xFFFFFFF0;//  		PMUSYS_CHIPID;
        packet->tmp_data32[2] = PMUSYS->UID[0];// TO Do UID
        packet->tmp_data32[3] = BOOT_VER;
        size_t boot_name_len = sizeof(BOOT_NAME);
        memcpy(&(packet->tmp_data32[4]), BOOT_NAME, boot_name_len);
        packet->data_n = 16 + boot_name_len;
    }

    msg_cmd(packet);
}

void get_cfgword_cmd(Packet_TypeDef* packet)
{
    uint16_t rx_crc;
    uint32_t data[4];

    rx_crc = packet_fifo_read_u16();

    if (packet->crc != rx_crc) {
        packet->tmp_data8[0] = MSG_ERR_CRC;
        packet->data_n = 4;
    } else {
        packet->tmp_data8[0] = MSG_OK;
        flash_read(FLASH_NVR_CFGWORD_OFFSET, FLASH_NVR, data);
        packet->tmp_data32[1] = data[0];
        packet->data_n = 8;
    }

    msg_cmd(packet);
}

void set_cfgword_cmd(Packet_TypeDef* packet)
{
    uint32_t cfgword;
    uint16_t rx_crc;
    uint16_t calc_crc;
    uint32_t page_arr[FLASH_PAGE_SIZE_CELLS][FLASH_CELL_WORD_WIDTH];
    uint32_t data[FLASH_CELL_WORD_WIDTH];
    uint32_t modify_en;
    uint32_t cfgword_page_addr =FLASH_NVR_CFGWORD_OFFSET & ~(FLASH_PAGE_SIZE_BYTES - 1);

    flash_read(FLASH_NVR_CFGWORD_OFFSET, FLASH_NVR, data);
    modify_en = (data[0] & CFGWORD_CFGWE_MSK) >> CFGWORD_CFGWE_POS;

    cfgword = packet_fifo_read_u32();
    calc_crc = crc_upd_u32(packet->crc, cfgword);

    rx_crc = packet_fifo_read_u16();

    packet->data_n = 8;
    if (calc_crc != rx_crc)
        packet->tmp_data8[0] = MSG_ERR_CRC;
    else if (!modify_en)
        packet->tmp_data8[0] = MSG_FAIL;
    else {
        //read the whole page
        for (uint32_t i = 0; i < FLASH_PAGE_SIZE_CELLS; i++) {
            flash_read(cfgword_page_addr + i * FLASH_CELL_WORD_WIDTH*4, FLASH_NVR, (uint32_t*)page_arr[i]);
        }
        //modify the CFGWORD, erase and write back
        page_arr[0][0] = cfgword;
        flash_erase_page(cfgword_page_addr, FLASH_NVR);
        for (uint32_t i = 0; i < FLASH_PAGE_SIZE_CELLS; i++) {
            if ((page_arr[i][0] != 0xFFFFFFFF) || (page_arr[i][1] != 0xFFFFFFFF))
                flash_write(cfgword_page_addr + i * 8, FLASH_NVR, (uint32_t*)page_arr[i]);
        }
    }

    packet->tmp_data32[1] = cfgword;

    msg_cmd(packet);
}

void write_page_cmd(Packet_TypeDef* packet)
{
    uint32_t rx_data;
    uint8_t cfg;
    uint32_t addr;
    uint32_t addr_i;
    uint32_t flash_type;
    uint32_t erase_option;
    uint32_t data[FLASH_CELL_WORD_WIDTH];
    uint16_t rx_crc;
    uint16_t calc_crc;
    uint32_t modify_en;

    //read the address, determine the required flash type and page number, then erase it if necessary
    rx_data = packet_fifo_read_u32();

    cfg = (uint8_t)(rx_data >> 24);

    //determine the type of flash and whether it can be written
    flash_type = (FlashType_TypeDef)((cfg & CMD_WRITE_PAGE_OPT_NVR_MSK) >> CMD_WRITE_PAGE_OPT_NVR_POS);
    flash_read(FLASH_NVR_CFGWORD_OFFSET, FLASH_NVR, data);
    if (flash_type == FLASH_MAIN)
        modify_en = (data[0] & CFGWORD_FLASHWE_MSK) >> CFGWORD_FLASHWE_POS;
    else
        modify_en = (data[0] & CFGWORD_CFGWE_MSK) >> CFGWORD_CFGWE_POS;

    //should erase before writing
    erase_option = (cfg & CMD_WRITE_PAGE_OPT_ERASE_MSK) >> CMD_WRITE_PAGE_OPT_ERASE_POS;

    addr = rx_data & ~(FLASH_PAGE_SIZE_BYTES - 1)& 0x00FFFFFF;

    //bootloader modification protection
    modify_en &= !((addr < (BOOT_FLASH_SIZE_TOTAL_BYTES)));

    if (erase_option && modify_en)
        flash_erase_page(addr, flash_type);
    calc_crc = crc_upd_u32(packet->crc, rx_data);

    //read 8 bytes of data and write the whole page
    addr_i = addr;
    for (uint32_t i = 0; i < FLASH_PAGE_SIZE_BYTES / 16; i++) {
      for (int j = 0; j < FLASH_CELL_WORD_WIDTH; j++){
        data[j] = packet_fifo_read_u32();
        calc_crc = crc_upd_u32(calc_crc, data[j]);
      }
        if (modify_en)
            flash_write(addr_i, flash_type, data);
    
        addr_i += (FLASH_CELL_WORD_WIDTH*4);
    }

    rx_crc = packet_fifo_read_u16();

    packet->data_n = 8;
    if (calc_crc != rx_crc)
        packet->tmp_data8[0] = MSG_ERR_CRC;
    else if (!modify_en)
        packet->tmp_data8[0] = MSG_FAIL;
    else
        packet->tmp_data8[0] = MSG_OK;

    packet->tmp_data32[1] = rx_data;

    msg_cmd(packet);
}

void jump_cmd(Packet_TypeDef* packet)
{
	uint32_t jumpaddr;
	uint32_t rx_data;
	uint16_t calc_crc;
	uint16_t rx_crc;

	jumpaddr = rx_data = packet_fifo_read_u32();
	calc_crc = crc_upd_u32(packet->crc, rx_data);

	rx_crc = packet_fifo_read_u16();
	if (calc_crc != rx_crc) {
		packet->tmp_data8[0] = MSG_ERR_CRC;
	}

	packet->tmp_data32[1] = rx_data;

	msg_cmd(packet);

	packet_fifo_read_u32();

	boot_exit(jumpaddr);
}

void read_page_cmd(Packet_TypeDef* packet)
{
    uint32_t rx_data;
    uint8_t cfg;
    uint32_t addr;
    uint32_t addr_i;
    uint32_t flash_type;
    uint32_t data[FLASH_CELL_WORD_WIDTH];
    uint16_t rx_crc;
    uint16_t calc_crc;
    uint32_t read_en;


    flash_read(FLASH_NVR_CFGWORD_OFFSET, FLASH_NVR, data);

    //read the address, determine the required flash type and page number, then erase it if necessary
    rx_data = packet_fifo_read_u32();

    cfg = (uint8_t)(rx_data >> 24);
    flash_type = (FlashType_TypeDef)((cfg & CMD_READ_PAGE_OPT_NVR_MSK) >> CMD_READ_PAGE_OPT_NVR_POS);
    //can HOST read flash

    addr = rx_data & ~(FLASH_PAGE_SIZE_BYTES - 1) & 0x00FFFFFF;
    //bootloader read protection
    //read_en &= !((addr < (BOOT_FLASH_SIZE_TOTAL_BYTES)));
    read_en = 1; // No protection

    calc_crc = crc_upd_u32(packet->crc, rx_data);
    rx_crc = packet_fifo_read_u16();

    packet->data_n = 8;
    if (calc_crc != rx_crc)
        packet->tmp_data8[0] = MSG_ERR_CRC;
    else if (!read_en)
        packet->tmp_data8[0] = MSG_FAIL;
    else {
        addr_i = addr;
        for (uint32_t i = 0; i < FLASH_PAGE_SIZE_CELLS; i++) {
            flash_read(addr_i, flash_type, data);
            for (int j = 0; j < FLASH_CELL_WORD_WIDTH; j++){
                packet->tmp_data32[2 + i*FLASH_CELL_WORD_WIDTH  + j] = data[j];
            }
            addr_i += FLASH_CELL_WORD_WIDTH*4;
        }
        packet->tmp_data8[0] = MSG_OK;
        packet->data_n += FLASH_PAGE_SIZE_BYTES;
    }

    packet->tmp_data32[1] = rx_data;

    msg_cmd(packet);
}

void erase_cmd(Packet_TypeDef* packet)
{
    uint32_t rx_data;
    uint8_t cfg;
    uint32_t addr;
    uint32_t flash_type;
    uint16_t rx_crc;
    uint16_t calc_crc;
    uint32_t data[2];
    uint32_t modify_en;

    rx_data = packet_fifo_read_u32();
    cfg = (uint8_t)(rx_data >> 24);

    //determine the type of flash and whether the host can erase it
    flash_type = (FlashType_TypeDef)((cfg & CMD_WRITE_PAGE_OPT_NVR_MSK) >> CMD_WRITE_PAGE_OPT_NVR_POS);
    flash_read(FLASH_NVR_CFGWORD_OFFSET, FLASH_NVR, data);
    if (flash_type == FLASH_MAIN)
        modify_en = (data[0] & CFGWORD_FLASHWE_MSK) >> CFGWORD_FLASHWE_POS;
    else
        modify_en = (data[0] & CFGWORD_CFGWE_MSK) >> CFGWORD_CFGWE_POS;

    addr = rx_data & ~(FLASH_PAGE_SIZE_BYTES - 1) & 0x00FFFFFF;

    //bootloader modification protection
    modify_en &= !((addr < (BOOT_FLASH_SIZE_TOTAL_BYTES)));

    calc_crc = crc_upd_u32(packet->crc, rx_data);
    rx_crc = packet_fifo_read_u16();

    packet->data_n = 8;
    if (calc_crc != rx_crc)
        packet->tmp_data8[0] = MSG_ERR_CRC;
    else if (!modify_en)
        packet->tmp_data8[0] = MSG_FAIL;
    else {
        if(packet->cmd_code == CMD_ERASE_FULL){
        	save_and_erase_all_ramfunc();
        }else{
            flash_erase_page(addr, flash_type);
        }
        
        packet->tmp_data8[0] = MSG_OK;
    }

    packet->tmp_data32[1] = rx_data;

    msg_cmd(packet);
}

void exit_cmd(Packet_TypeDef* packet)
{
    uint16_t rx_crc;
    uint16_t calc_crc;

    calc_crc = packet->crc;
    rx_crc = packet_fifo_read_u16();

    packet->data_n = 4;
    if (calc_crc != rx_crc)
        packet->tmp_data8[0] = MSG_ERR_CRC;
    else
        packet->tmp_data8[0] = MSG_OK;

    msg_cmd(packet);
    while (packet_transmit_status_busy()) {
    };

    boot_exit(USER_JUMP_ADDRESS);
}


__attribute__((section(".ramfunc")))
void flash_erase_full_ramfunc(void) {
	__asm__ volatile("nop");
	__asm__ volatile("nop");
	while (FLASH->STAT_bit.BUSY) {};
	FLASH->ADDR = 0;
	FLASH->CMD = FLASH_MAGICKEY_CONST << FLASH_CMD_KEY_Pos |
			FLASH_ALLSEC | FLASH_MAIN << FLASH_CMD_NVRON_Pos;
	while (FLASH->STAT_bit.BUSY) {};
}

__attribute__((section(".ramfunc")))
void flash_write_128_ramfunc(uint32_t addr, uint32_t *data) {
    FLASH->ADDR = addr;
    FLASH->DATA[0].DATA = data[0];
    FLASH->DATA[1].DATA = data[1];
    FLASH->DATA[2].DATA = data[2];
    FLASH->DATA[3].DATA = data[3];
    FLASH->CMD = (0xC0DE << 16) | FLASH_CMD_WR_Msk;
    while (FLASH->STAT & 0x01);
}

__attribute__((section(".ramfunc")))
void memcpy_flash_ramfunc(uint32_t to_flash, uint32_t* from, uint32_t size) {
	for(uint32_t i = 0; i < size; i += 4) {
		flash_write_128_ramfunc(to_flash + i * 4, from + i);
	}
}

__attribute__((section(".ramfunc")))
void memcpy_ramfunc(uint8_t* to, uint8_t* from, uint32_t size) {
	for (uint32_t i = 0; i < size; i++) {
		to[i] = from[i];
	}
}

__attribute__((section(".ramfunc")))
void save_and_erase_all_ramfunc(void) {
	memcpy_ramfunc((uint8_t*) bootflash_program, (uint8_t*) 0x80000000, BOOT_FLASH_SIZE_TOTAL_BYTES);
	flash_erase_full_ramfunc();
	memcpy_flash_ramfunc(0x80000000, (uint32_t*) bootflash_program, BOOT_FLASH_SIZE_TOTAL_BYTES / 4);
}
