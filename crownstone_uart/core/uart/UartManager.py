import asyncio
import serial

from crownstone_uart.core.uart.UartBridge import UartBridge


class UartManager:

    def __init__(self, port = None, baudRate = 230400):
        self.port = port
        self.baudRate = baudRate
        self.running = True
        self._trackingLoop = None
        self._availablePorts = serial.tools.list_ports.comports()
        self._attemptingIndex = 0
        self._uartBridge = None

    async def reset(self):
        self._attemptingIndex = 0
        self._availablePorts = serial.tools.list_ports.comports()
        self._uartBridge = None
        self.port = None
        await self.initialize()

    def stop(self):
        self.running = False
        if self._uartBridge is not None:
            self._uartBridge.stop_sync()


    async def initialize(self, port = None, baudrate = 230400):
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
        self._uartBridge = UartBridge(attemptingPort.device, self.baudRate)
        self._uartBridge.start()
        await asyncio.sleep(0.5)
        
        success = await self._uartBridge.handshake()

        if not success:
            print("Crownstone handshake failed. Moving on to next device...")
            self._attemptingIndex += 1
            await self._uartBridge.stop()
            await self.initialize()
        else:
            print("Connection established to", attemptingPort.device)
            self.port = attemptingPort.device
            asyncio.create_task(self.trackConnection())
        


    async def trackConnection(self):
        await self._uartBridge.isAlive()
        if self.running:
            asyncio.create_task(self.reset())

