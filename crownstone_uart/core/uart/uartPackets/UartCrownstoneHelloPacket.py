from crownstone_core.util.DataStepper import DataStepper

from crownstone_uart.core.uart.uartPackets.UartCrownstoneStatusPacket import UartCrownstoneStatusPacket

class UartCrownstoneHelloPacket:
    """
    UART crownstone hello packet:
    1B sphereId
    1B status
    """
    def __init__(self, buffer):
        if isinstance(buffer, DataStepper):
            streamBuf = buffer
        else:
            streamBuf = DataStepper(buffer)

        # Parse buffer
        self.sphereId = streamBuf.getUInt8()

        self.status = UartCrownstoneStatusPacket(streamBuf)
