# import signal  # used to catch control C

# from crownstone_uart.core.dataFlowManagers.StoneManager import StoneManager
# from crownstone_uart.core.modules.UsbDevHandler import UsbDevHandler
import asyncio

from crownstone_uart.core.uart.UartBridge import UartBridge
from crownstone_uart.core.uart.UartManager import UartManager


class CrownstoneUart:

    def __init__(self):
        self.uartManager = None
        self.running = True
        self.uartManager = UartManager()
        self.loop = asyncio.get_event_loop()
        # self.stoneManager = StoneManager()
        # self._usbDev = UsbDevHandler()
        
        # listen for CTRL+C and handle the exit cleanly.
        # if catchSIGINT:
        #     signal.signal(signal.SIGINT, lambda source,frame: self.stop())


    def __del__(self):
        self.stop()


    async def initialize_usb(self, port = None, baudrate=230400):
        await self.uartManager.initialize()

        # init the uart bridge
        # self.uartBridge = UartBridge(port, baudrate)
        # self.uartBridge.start()

    def initialize_usb_sync(self, port = None, baudrate=230400):
        self.loop.run_until_complete(self.uartManager.initialize())

    def stop(self):
        print("Quitting BluenetLib...")
        # UartEventBus.emit(SystemTopics.cleanUp)
        self.running = False

    #
    # def switchCrownstone(self, crownstoneId, on):
    #     """
    #     :param crownstoneId:
    #     :param on: Boolean
    #     :return:
    #     """
    #     state = 1
    #     if not on:
    #         state = 0
    #
    #     self.__switchCrownstone(crownstoneId, state)
    #
    #
    # def dimCrownstone(self, crownstoneId, value):
    #     # dimming is used when the value is [0 .. 99], 100 is turning on the relay. We map 0..1 to 0..0.99
    #     value = min(0.99, max(0,value) * 0.99)
    #
    #     self.__switchCrownstone(crownstoneId, value)


    # def getCrownstoneIds(self):
    #     return self.stoneManager.getIds()
    #
    # def getCrownstones(self):
    #     return self.stoneManager.getStones()
    #
    # def isRunning(self):
    #     return self.running
    #
    # def uartEcho(self, payloadString):
    #     # wrap that in a control packet
    #     controlPacket = ControlPacket(ControlType.UART_MESSAGE).loadString(payloadString).getPacket()
    #
    #     # finally wrap it in an Uart packet
    #     uartPacket = UartWrapper(UartTxType.CONTROL, controlPacket).getPacket()
    #
    #     # send over uart
    #     UartEventBus.emit(SystemTopics.uartWriteData, uartPacket)
    #
    # # MARK: Private
    #
    # def __switchCrownstone(self, crownstoneId, value):
    #     """
    #     :param crownstoneId:
    #     :param value: 0 .. 1
    #     :return:
    #     """
    #
    #     # forcibly map the input from [any .. any] to [0 .. 1]
    #     correctedValue = min(1,max(0,value))
    #
    #     # create a stone switch state packet to go into the multi switch
    #     stoneSwitchPacket     = StoneMultiSwitchPacket(crownstoneId, correctedValue)
    #
    #     # wrap it in a mesh multi switch packet
    #     meshMultiSwitchPacket = MeshMultiSwitchPacket([stoneSwitchPacket]).getPacket()
    #
    #     # wrap that in a control packet
    #     controlPacket         = ControlPacket(ControlType.MULTISWITCH).loadByteArray(meshMultiSwitchPacket).getPacket()
    #
    #     # finally wrap it in an Uart packet
    #     uartPacket            = UartWrapper(UartTxType.CONTROL, controlPacket).getPacket()
    #
    #     print("sending this packet", uartPacket)
    #     # send over uart
    #     UartEventBus.emit(SystemTopics.uartWriteData, uartPacket)