from crownstone_core.util.BasePackets import *


class AssetMacReport(PacketBase):

    def __init__(self):
        self.macAddress   = PacketBaseList(cls=Uint8,len=6)
        self.crownstoneId = Uint8()
        self.rssi         = Int8()
        self.channel      = Uint8()