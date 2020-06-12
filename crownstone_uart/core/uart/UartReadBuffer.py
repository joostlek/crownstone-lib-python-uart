from crownstone_core.util.Conversion import Conversion
import logging

from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.core.uart.UartWrapper import START_TOKEN, ESCAPE_TOKEN, BIT_FLIP_MASK
from crownstone_uart.core.uart.uartPackets.UartPacket import PREFIX_SIZE, OPCODE_SIZE, WRAPPER_SIZE, CRC_SIZE, \
    UartPacket
from crownstone_uart.topics.DevTopics import DevTopics
from crownstone_uart.topics.SystemTopics import SystemTopics
from crownstone_uart.util.UartUtil import UartUtil

_LOGGER = logging.getLogger(__name__)


class UartReadBuffer:

    def __init__(self):
        self.buffer = []
        self.escapingNextToken = False
        self.active = False
        self.opCode = 0
        
        self.length = 0

    def addByteArray(self, rawByteArray):
        for byte in rawByteArray:
            self.add(byte)

    def add(self, byte):
        # if we have a start token and we are not active
        if byte is START_TOKEN:
            if self.active:
                _LOGGER.warning("MULTIPLE START TOKENS")
                UartEventBus.emit(DevTopics.uartNoise, "multiple start token")
#                print("buf:", self.buffer)
                self.reset()
                return
            else:
                self.active = True
                return

        if not self.active:
            return

        if byte is ESCAPE_TOKEN:
            if self.escapingNextToken:
                _LOGGER.warning("DOUBLE ESCAPE")
                UartEventBus.emit(DevTopics.uartNoise, "double escape token")
                self.reset()
                return

            self.escapingNextToken = True
            return

        # first get the escaping out of the way to avoid any double checks later on
        if self.escapingNextToken:
            byte ^= BIT_FLIP_MASK
            self.escapingNextToken = False

        self.buffer.append(byte)
        bufferSize = len(self.buffer)

        if bufferSize == PREFIX_SIZE:
            self.length = Conversion.uint8_array_to_uint16(self.buffer[OPCODE_SIZE:PREFIX_SIZE])

        if bufferSize > PREFIX_SIZE:
            if bufferSize == (self.length + WRAPPER_SIZE):
                self.process()
                return
            elif bufferSize > self.length + WRAPPER_SIZE:
                _LOGGER.warning("OVERFLOW")
                UartEventBus.emit(DevTopics.uartNoise, "overflow")
                self.reset()

    def process(self):
        payload = self.buffer[0:len(self.buffer)-CRC_SIZE]
        calculatedCrc = UartUtil.crc16_ccitt(payload)
        sourceCrc = Conversion.uint8_array_to_uint16(self.buffer[len(self.buffer) - CRC_SIZE : len(self.buffer)])

        if calculatedCrc != sourceCrc:
            _LOGGER.warning("Failed CRC")
            UartEventBus.emit(DevTopics.uartNoise, "crc mismatch")
            self.reset()
            return

        packet = UartPacket(self.buffer)
        UartEventBus.emit(SystemTopics.uartNewPackage, packet)
        self.reset()

    def reset(self):
        self.buffer = []
        self.escapingNextToken = False
        self.active = False
        self.opCode = 0
        self.length = 0

