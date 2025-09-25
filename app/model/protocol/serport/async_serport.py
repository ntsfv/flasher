#!/user/bin/env python
# coding:utf-8
from asyncio import Queue
import serial_asyncio
import asyncio

from model.logger.loggable import Loggable
from model.protocol.serport.serport import SerPort


class AsyncSerPort(SerPort, asyncio.Protocol, Loggable):
    def __init__(self):
        Loggable.__init__(self)

        self.write_queue = Queue()
        self.read_queue = Queue()

        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.logger.info(list(map(hex, list(data))))
        for byte in bytes(data):
            asyncio.get_event_loop().create_task(self.read_queue.put(byte))

    @staticmethod
    def open(port='/dev/ttyUSB0', baudrate=115200):
        loop = asyncio.get_event_loop()
        coro = serial_asyncio.create_serial_connection(loop, AsyncSerPort, port, baudrate=baudrate, timeout=5, do_not_open=True)
        transport, protocol = loop.run_until_complete(coro)

        transport.serial.rts = False
        transport.serial.dtr = False

        transport.serial.open()
        return protocol

    def close(self):
        self.transport.close()

    def reset_input_buffer(self):
        pass

    def connection_lost(self, exc):
        self.logger.info('Порт закрыт')
        # self.transport.loop.stop()

    def write(self, blist):
        self.transport.write(bytes(blist))

    async def read(self, size=1):
        bytes_str = []

        if size < 1:
            return bytes_str

        for byte in range(size):
            bytes_str.append(await self.read_queue.get())
        
        return int.from_bytes(bytes_str, byteorder='little')


if __name__ == '__main__':
    l = asyncio.new_event_loop()
    asyncio.set_event_loop(l)
    proto = AsyncSerPort.open('COM7')

    l.run_until_complete(asyncio.sleep(0.01))

    l.run_until_complete(proto.write([0x7F]))

    data = l.run_until_complete(proto.read(2))

    print(data)

    l.run_forever()
    l.close()
