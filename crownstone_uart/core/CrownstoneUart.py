# import signal  # used to catch control C
from crownstone_core.protocol.BlePackets import ControlPacket
from crownstone_core.protocol.BluenetTypes import ControlType
from crownstone_core.protocol.MeshPackets import StoneMultiSwitchPacket, MeshMultiSwitchPacket

from crownstone_uart.core.dataFlowManagers.StoneManager import StoneManager
from crownstone_uart.core.modules.UsbDevHandler import UsbDevHandler
import asyncio

from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.core.uart.UartManager import UartManager
from crownstone_uart.core.uart.UartTypes import UartTxType
from crownstone_uart.core.uart.UartWrapper import UartWrapper
from crownstone_uart.topics.SystemTopics import SystemTopics


class CrownstoneUart:

    def __init__(self):
        self.uartManager = None
        self.running = True
        self.uartManager = UartManager()
        self.loop = asyncio.get_event_loop()
        self.stoneManager = StoneManager()
        self._usbDev = UsbDevHandler()

    def __del__(self):
        self.stop()


    async def initialize_usb(self, port = None, baudrate=230400):
        await self.uartManager.initialize()

    def initialize_usb_sync(self, port = None, baudrate=230400):
        try:
            self.loop.run_until_complete(self.uartManager.initialize())
        except:
            self.stop()


    def run_forever(self):
        try:
            self.loop.run_forever()
        except:
            self.stop()

    def stop(self):
        if self.uartManager is not None:
            self.uartManager.stop()
        self.running = False

    #
    def switchCrownstone(self, crownstoneId, on):
        """
        :param crownstoneId:
        :param on: Boolean
        :return:
        """
        state = 1
        if not on:
            state = 0

        self.__switchCrownstone(crownstoneId, state)


    def dimCrownstone(self, crownstoneId, value):
        # dimming is used when the value is [0 .. 99], 100 is turning on the relay. We map 0..1 to 0..0.99
        value = min(0.99, max(0,value) * 0.99)

        self.__switchCrownstone(crownstoneId, value)


    def getCrownstoneIds(self):
        return self.stoneManager.getIds()

    def getCrownstones(self):
        return self.stoneManager.getStones()

    def isRunning(self):
        return self.running

    def uartEcho(self, payloadString):
        # wrap that in a control packet
        controlPacket = ControlPacket(ControlType.UART_MESSAGE).loadString(payloadString).getPacket()

        # finally wrap it in an Uart packet
        uartPacket = UartWrapper(UartTxType.CONTROL, controlPacket).getPacket()

        # send over uart
        UartEventBus.emit(SystemTopics.uartWriteData, uartPacket)

    # MARK: Private

    def __switchCrownstone(self, crownstoneId, value):
        """
        :param crownstoneId:
        :param value: 0 .. 1
        :return:
        """

        # forcibly map the input from [any .. any] to [0 .. 1]
        correctedValue = min(1,max(0,value))

        # create a stone switch state packet to go into the multi switch
        stoneSwitchPacket     = StoneMultiSwitchPacket(crownstoneId, correctedValue)

        # wrap it in a mesh multi switch packet
        meshMultiSwitchPacket = MeshMultiSwitchPacket([stoneSwitchPacket]).getPacket()

        # wrap that in a control packet
        controlPacket         = ControlPacket(ControlType.MULTISWITCH).loadByteArray(meshMultiSwitchPacket).getPacket()

        # finally wrap it in an Uart packet
        uartPacket            = UartWrapper(UartTxType.CONTROL, controlPacket).getPacket()

        # send over uart
        UartEventBus.emit(SystemTopics.uartWriteData, uartPacket)