import asyncio
import logging
import threading
import time

from crownstone_core.protocol.BlePackets import ControlPacket
from crownstone_core.protocol.BluenetTypes import ControlType
from crownstone_uart.core.dataFlowManagers.Collector import Collector

from crownstone_uart.topics.SystemTopics import SystemTopics
from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.core.uart.UartWrapper import UartWrapper
from crownstone_uart.core.uart.UartTypes import UartTxType
from crownstone_uart.topics.UartTopics import UartTopics
from crownstone_uart.core.uart.UartBridge import UartBridge
from serial.tools import list_ports

_LOGGER = logging.getLogger(__name__)

class UartManager(threading.Thread):

    def __init__(self):
        self.port = None
        self.baudRate = 230400
        self.running = True
        self.loop = None
        self._availablePorts = list(list_ports.comports())
        self._attemptingIndex = 0
        self._uartBridge = None
        self.ready = False
        self.eventId = UartEventBus.subscribe(SystemTopics.connectionClosed, self.resetEvent)

        threading.Thread.__init__(self)

    def __del__(self):
        self.stop()

    def config(self, port, baudRate = 230400):
        self.port     = port
        self.baudRate = baudRate

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.initialize()

    def stop(self):
        self.running = False
        UartEventBus.unsubscribe(self.eventId)
        if self._uartBridge is not None:
            self._uartBridge.stop()

    def resetEvent(self, eventData=None):
        if self.ready:
            self._uartBridge.stop()
            while self._uartBridge.running:
                time.sleep(0.1)
            self.reset()

            self.ready = False
            self.initialize()

    def reset(self):
        if self.running:
            self._attemptingIndex = 0
            self._availablePorts = list(list_ports.comports())
            self._uartBridge = None
            self.port = None

    def echo(self, string):
        controlPacket = ControlPacket(ControlType.UART_MESSAGE).loadString(string).getPacket()
        uartPacket    = UartWrapper(UartTxType.CONTROL, controlPacket).getPacket()
        UartEventBus.emit(SystemTopics.uartWriteData, uartPacket)

    def initialize(self):
        while self.running and not self.ready:
            self.ready = False
            _LOGGER.debug(F"Initializing... {self.port} {self.baudRate}")

            # if the user provides his own port, we check if it is in the list of ports we have
            # if it exists, we start there and skip the handshake.
            # if it is not in the list, we attempt the connection regardless, this might change in the future.
            if self.port is not None:
                found_port = False
                index = 0
                # check if the provided port is among the listed ports.
                for testPort in self._availablePorts:
                    if self.port == testPort.device:
                        found_port = True
                        self._attemptingIndex = index
                        break
                    index += 1
                # if it is not in the list of available ports
                if not found_port:
                    # we will attempt it anyway
                    _LOGGER.debug(F"Could not find provided port, attempt connection to index...{self._attemptingIndex} {self.baudRate}")
                    self.setupConnection(self.port)
                else:
                    _LOGGER.debug(F"Setup connection to...{self.port} {self.baudRate}")
                    self._attemptConnection(self._attemptingIndex, False)
                continue


            if self.port is None:
                if self._attemptingIndex >= len(self._availablePorts): # this also catches len(self._availablePorts) == 0
                    _LOGGER.debug("No Crownstone USB connected? Retrying...")
                    time.sleep(1)
                    self.reset()
                else:
                    self._attemptConnection(self._attemptingIndex)


    def _attemptConnection(self, index, handshake=True):
        attemptingPort = self._availablePorts[index]
        self.setupConnection(attemptingPort.device, handshake)


    def setupConnection(self, port, handshake=True):
        _LOGGER.debug(F"Setting up connection...{port} {self.baudRate} {handshake}")
        self._uartBridge = UartBridge(port, self.baudRate)
        self._uartBridge.start()

        # wait for the bridge to initialize
        while not self._uartBridge.started and self.running:
            time.sleep(0.1)

        success = True

        if handshake:
            collector = Collector(timeout=0.25, topic=UartTopics.uartMessage)
            
            self.echo("HelloCrownstone")
            reply = collector.receive_sync()

            success = False
            if reply is not None:
                if "string" in reply:
                    success = reply["string"] == "HelloCrownstone"
                    _LOGGER.debug("Handshake successful")
                else:
                    _LOGGER.debug("Handshake failed")
            else:
                _LOGGER.debug("Handshake failed")


        if not success:
            _LOGGER.debug("Reinitialization required")
            self._attemptingIndex += 1
            self._uartBridge.stop()
            while self._uartBridge.started and self.running:
                time.sleep(0.1)
        else:
            _LOGGER.info("Connection established to {}".format(port))
            self.port = port
            self.ready = True
            UartEventBus.emit(SystemTopics.connectionEstablished)



    def is_ready(self) -> bool:
        return self.ready