import asyncio
import threading

import serial
import serial.tools.list_ports
from crownstone_core.protocol.BlePackets import ControlPacket
from crownstone_core.protocol.BluenetTypes import ControlType

from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.core.dataFlowManagers.EchoResponse import EchoResponse
from crownstone_uart.core.uart.UartParser import UartParser
from crownstone_uart.core.uart.UartReadBuffer import UartReadBuffer
from crownstone_uart.core.uart.UartTypes import UartTxType
from crownstone_uart.core.uart.UartWrapper import UartWrapper
from crownstone_uart.topics.SystemTopics import SystemTopics


class UartBridge (threading.Thread):

    def __init__(self, port, baudrate):
        self.baudrate = baudrate
        self.port = port

        self.serialController = None
        self.parser = None
        self.eventId = 0

        self.running = True

        self.start_serial()

        if self.running:
            threading.Thread.__init__(self)

    def __del__(self):
        self.stop_sync()

    async def handshake(self):
        collector = EchoResponse(0.2)
        handshake = "HelloCrownstone"
        self.echo(handshake)
        reply = await collector.collect()
        if reply is not None:
            if "string" in reply:
                return reply["string"] == handshake
        return False

    def echo(self, string):
        controlPacket = ControlPacket(ControlType.UART_MESSAGE).loadString(string).getPacket()
        uartPacket    = UartWrapper(UartTxType.CONTROL, controlPacket).getPacket()
        self.write_to_uart(uartPacket)


    def run(self):
        self.eventId = UartEventBus.subscribe(SystemTopics.uartWriteData, self.write_to_uart)

        UartEventBus.subscribe(SystemTopics.cleanUp, lambda x: self.stop())

        self.parser = UartParser()
        self.start_reading()
    #
    def stop_sync(self):
        # print("Stopping UartBridge")
        self.running = False
        UartEventBus.unsubscribe(self.eventId)

    async def stop(self):
        self.stop_sync()
        counter = 0
        while self.serialController is not None and counter < 2:
            counter += 0.1
            await asyncio.sleep(0.1)

    async def isAlive(self):
        while self.serialController is not None and self.running:
            await asyncio.sleep(0.1)
    #
    def start_serial(self):
        # print("Initializing serial on port ", self.port, ' with baudrate ', self.baudrate)
        try:
            self.serialController = serial.Serial()
            self.serialController.port = self.port
            self.serialController.baudrate = int(self.baudrate)
            self.serialController.timeout = 0.25
            self.serialController.open()
        except:
            self.stop_sync()


    def start_reading(self):
        readBuffer = UartReadBuffer()
        # print("Read starting on serial port.")
        try:
            while self.running:
                bytes = self.serialController.read()
                if bytes:
                    # clear out the entire read buffer
                    if self.serialController.in_waiting > 0:
                        additionalBytes = self.serialController.read(self.serialController.in_waiting)
                        bytes = bytes + additionalBytes
                    readBuffer.addByteArray(bytes)

            # print("Cleaning up UartBridge")
        except serial.SerialException as err:
            print("Connection Failed. Retrying...")
        self.serialController.close()
        self.serialController = None

    def write_to_uart(self, data):
        if self.serialController is not None:
            self.serialController.write(data)
        else:
            self.stop_sync()
