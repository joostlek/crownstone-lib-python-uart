from crownstone_core.util.BasePackets import *


class NearestCrownstoneTrackingUpdate(PacketBase):

    def __init__(self):
        self.assetId      = Uint8Array([],3)
        self.crownstoneId = Uint8()
        self.rssi         = Int8()
        self.channel      = Uint8()

class NearestCrownstoneTrackingTimeout(PacketBase):

    def __init__(self):
        self.assetId      = Uint8Array([],3)