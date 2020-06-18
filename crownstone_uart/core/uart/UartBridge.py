import logging
import threading

import serial
import serial.tools.list_ports

from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.core.uart.UartParser import UartParser
from crownstone_uart.core.uart.UartReadBuffer import UartReadBuffer
from crownstone_uart.topics.SystemTopics import SystemTopics

_LOGGER = logging.getLogger(__name__)


class UartBridge(threading.Thread):

    def __init__(self, port, baudrate):
        self.baudrate = baudrate
        self.port = port

        self.serialController = None
        self.started = False

        self.running = True
        self.parser = UartParser()
        self.eventId = UartEventBus.subscribe(SystemTopics.uartWriteData, self.write_to_uart)
        threading.Thread.__init__(self)

    def __del__(self):
        self.stop()

    def run(self):
        self.start_serial()
        self.start_reading()


    def stop(self):
        self.running = False
        UartEventBus.unsubscribe(self.eventId)
        self.parser.stop()


    def start_serial(self):
        _LOGGER.debug(F"UartBridge: Initializing serial on port {self.port} with baudrate {self.baudrate}")
        try:
            self.serialController = serial.Serial()
            self.serialController.port = self.port
            self.serialController.baudrate = int(self.baudrate)
            self.serialController.timeout = 0.25
            self.serialController.open()
        except OSError or serial.SerialException or KeyboardInterrupt:
            self.stop()


    def start_reading(self):
        readBuffer = UartReadBuffer()
        self.started = True
        _LOGGER.debug(F"Read starting on serial port.{self.port} {self.running}")
        try:
            while self.running:
                bytesFromSerial = self.serialController.read()
                if bytesFromSerial:
                    # clear out the entire read buffer
                    if self.serialController.in_waiting > 0:
                        additionalBytes = self.serialController.read(self.serialController.in_waiting)
                        bytesFromSerial = bytesFromSerial + additionalBytes
                    readBuffer.addByteArray(bytesFromSerial)

            # print("Cleaning up UartBridge")
        except OSError or serial.SerialException:
            _LOGGER.info("Connection to USB Failed. Retrying...")
        except KeyboardInterrupt:
            self.running = False
            _LOGGER.debug("Closing serial connection.")

        # close the serial controller
        self.serialController.close()
        self.serialController = None
        # remove the event listener pointing to the old connection
        UartEventBus.unsubscribe(self.eventId)
        self.started = False
        UartEventBus.emit(SystemTopics.connectionClosed, True)

    def write_to_uart(self, data):
        if self.serialController is not None and self.started:
            self.serialController.write(data)
        else:
            self.stop()
