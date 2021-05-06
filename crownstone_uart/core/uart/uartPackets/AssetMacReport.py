from crownstone_core.util.BasePackets import *


class AssetMacReport(PacketBase):

    def __init__(self):
        self.macAddress   = Uint8Array([],6)
        self.crownstoneId = Uint8()
        self.rssi         = Int8()
        self.channel      = Uint8()