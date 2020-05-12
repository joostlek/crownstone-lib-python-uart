import asyncio, serial

from crownstone_core.Exceptions import CrownstoneException

from crownstone_uart.Exceptions import UartError
from crownstone_uart.core.uart.UartBridge import UartBridge




class UartManager:

    def __init__(self, port = None, baudRate = 230400):
        self.port = port
        self.baudRate = baudRate
        self._availablePorts = serial.tools.list_ports.comports()
        self._attemptingIndex = 0
        self._uartBridge = None

    async def initialize(self):
        if self.port is None:
            if self._attemptingIndex >= len(self._availablePorts): # this also catches len(self._availablePorts) == 0
                raise CrownstoneException(UartError.NO_CROWNSTONE_UART_DEVICE_AVAILABLE, "Is the Crownstone USB connected?")
            else:
                await self._attemptConnection(self._attemptingIndex)

    async def _attemptConnection(self, index):
        attemptingPort = self._availablePorts[index]
        self._uartBridge = UartBridge(attemptingPort.device, self.baudRate)
        self._uartBridge.start()

        await asyncio.sleep(0.5)
        
        success = await self._uartBridge.handshake()

        if not success:
            self._attemptingIndex += 1
            await self._uartBridge.stop()
            await self.initialize()
        else:
            self.port = attemptingPort.device
        



