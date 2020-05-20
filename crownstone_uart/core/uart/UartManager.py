import asyncio

from crownstone_uart.core.uart.UartBridge import UartBridge
from serial.tools import list_ports

class UartManager:

    def __init__(self, port = None, baudRate = 230400):
        self.port = port
        self.baudRate = baudRate
        self.running = True
        self._trackingLoop = None
        self._availablePorts = list(list_ports.comports())
        self._attemptingIndex = 0
        self._uartBridge = None

    async def reset(self):
        self._attemptingIndex = 0
        self._availablePorts = list(list_ports.comports())
        self._uartBridge = None
        self.port = None
        await self.initialize()

    def stop(self):
        self.running = False
        if self._uartBridge is not None:
            self._uartBridge.stop_sync()


    async def initialize(self, port = None, baudrate = 230400):
        self.baudRate = baudrate

        if port is not None:
            found_port = False
            index = 0
            for testPort in self._availablePorts:
                if port == testPort.device:
                    found_port = True
                    self._attemptingIndex = index
                    break
                index += 1
            if not found_port:
                return await self.setupConnection(port)


        if self._trackingLoop is None:
            self._trackingLoop = asyncio.get_running_loop()

        if self.port is None:
            if self._attemptingIndex >= len(self._availablePorts): # this also catches len(self._availablePorts) == 0
                print("No Crownstone USB connected? Retrying...")
                await asyncio.sleep(1)
                await self.reset()
            else:
                await self._attemptConnection(self._attemptingIndex)


    async def _attemptConnection(self, index):
        attemptingPort = self._availablePorts[index]
        await self.setupConnection(attemptingPort.device)


    async def setupConnection(self, port):
        self._uartBridge = UartBridge(port, self.baudRate)
        self._uartBridge.start()
        await self._uartBridge.starting()

        success = await self._uartBridge.handshake()

        if not success:
            print("Crownstone handshake failed. Moving on to next device...")
            self._attemptingIndex += 1
            await self._uartBridge.stop()
            await self.initialize()
        else:
            print("Connection established to", port)
            self.port = port
            asyncio.create_task(self.trackConnection())
        

    async def trackConnection(self):
        await self._uartBridge.isAlive()
        if self.running:
            asyncio.create_task(self.reset())

