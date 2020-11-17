from crownstone_core.util.Conversion import Conversion
import logging

from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.core.uart.uartPackets.UartWrapperPacket import SIZE_HEADER_SIZE, CRC_SIZE, WRAPPER_HEADER_SIZE, START_TOKEN, \
    ESCAPE_TOKEN, BIT_FLIP_MASK, UartWrapperPacket
from crownstone_uart.topics.DevTopics import DevTopics
from crownstone_uart.topics.SystemTopics import SystemTopics
from crownstone_uart.util.UartUtil import UartUtil

_LOGGER = logging.getLogger(__name__)


class UartReadBuffer:

    def __init__(self):
        self.buffer = []
        self.escapingNextByte = False
        self.active = False
        self.sizeToRead = 0

    def addByteArray(self, rawByteArray):
        for byte in rawByteArray:
            self.add(byte)

    def add(self, byte):
        # An escape shouldn't be followed by a special byte.
        if self.escapingNextByte and (byte is START_TOKEN or byte is ESCAPE_TOKEN):
            _LOGGER.warning("Special byte after escape token")
            UartEventBus.emit(DevTopics.uartNoise, "special byte after escape token")
            self.reset()
            return

        # Activate on start token.
        if byte is START_TOKEN:
            if self.active:
                _LOGGER.warning("MULTIPLE START TOKENS")
                _LOGGER.debug(f"Multiple start tokens: sizeToRead={self.sizeToRead} bufLen={len(self.buffer)} buffer={self.buffer}")
                UartEventBus.emit(DevTopics.uartNoise, "multiple start token")
            self.reset()
            self.active = True
            return

        if not self.active:
            return

        # Escape next byte on escape token.
        if byte is ESCAPE_TOKEN:
            self.escapingNextByte = True
            return

        if self.escapingNextByte:
            byte ^= BIT_FLIP_MASK
            self.escapingNextByte = False

        self.buffer.append(byte)
        bufferSize = len(self.buffer)

        if self.sizeToRead == 0:
            # We didn't parse the size yet.
            if bufferSize == SIZE_HEADER_SIZE:
                # Now we know the remaining size to read
                self.sizeToRead = Conversion.uint8_array_to_uint16(self.buffer)

                # Size to read shouldn't be 0.
                if self.sizeToRead == 0:
                    self.reset()
                    return

                self.buffer = []
                return

        elif bufferSize >= self.sizeToRead:
            self.process()
            self.reset()
            return

    def process(self):
        """
        Process a buffer.

        Check CRC, and emit a uart packet.

        Buffer starts after size header, and includes wrapper header and tail (CRC).
        """

        # Check size
        bufferSize = len(self.buffer)
        wrapperSize = WRAPPER_HEADER_SIZE + CRC_SIZE
        if bufferSize < wrapperSize:
            _LOGGER.warning("Buffer too small")
            UartEventBus.emit(DevTopics.uartNoise, "buffer too small")
            return

        # Get the buffer between size field and CRC:
        baseBuffer = self.buffer[0 : bufferSize - CRC_SIZE]

        # Check CRC
        calculatedCrc = UartUtil.crc16_ccitt(baseBuffer)
        sourceCrc = Conversion.uint8_array_to_uint16(self.buffer[bufferSize - CRC_SIZE : ])

        if calculatedCrc != sourceCrc:
            _LOGGER.warning("Failed CRC")
            _LOGGER.debug(f"Failed CRC: sourceCrc={sourceCrc} calculatedCrc={calculatedCrc} bufSize={len(self.buffer)} buffer={self.buffer}")
            UartEventBus.emit(DevTopics.uartNoise, "crc mismatch")
            return

        wrapperPacket = UartWrapperPacket()
        if wrapperPacket.parse(baseBuffer):
            UartEventBus.emit(SystemTopics.uartNewPackage, wrapperPacket)

    def reset(self):
        self.buffer = []
        self.escapingNextByte = False
        self.active = False
        self.sizeToRead = 0

