from crownstone_core.util.DataStepper import DataStepper


class UartCrownstoneStatusPacket:
    """
    UART crownstone status packet:
    1B flags
    """

    def __init__(self, buffer):
        if isinstance(buffer, DataStepper):
            streamBuf = buffer
        else:
            streamBuf = DataStepper(buffer)

        self.flags = streamBuf.getUInt8()

        # Parse flags
        self.encryptionRequired = self.flags & (1 << 0) != 0
        self.hasBeenSetUp       = self.flags & (1 << 1) != 0
        self.hubMode            = self.flags & (1 << 2) != 0
        self.hasError           = self.flags & (1 << 3) != 0
