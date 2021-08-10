from crownstone_core.packets.BasePacket import BasePacket
from crownstone_core.util.BufferReader import BufferReader


class NearestCrownstoneTrackingUpdate(BasePacket):
    def __init__(self, data=None):
        self.assetId      = 0
        self.crownstoneId = 0
        self.rssi         = 0
        self.channel      = 0

        if data is not None:
            self.deserialize(data)

    def _deserialize(self, reader: BufferReader):
        self.assetId      = reader.getUInt8() + (reader.getUInt8() << 8) + (reader.getUInt8() << 16)
        self.crownstoneId = reader.getUInt8()
        self.rssi         = reader.getInt8()
        self.channel      = reader.getUInt8()

    def __str__(self):
        return f"NearestCrownstoneTrackingUpdate(" \
               f"assetId={self.assetId} " \
               f"crownstoneId={self.crownstoneId} " \
               f"rssi={self.rssi} " \
               f"channel={self.channel})"


class NearestCrownstoneTrackingTimeout(BasePacket):
    def __init__(self, data=None):
        self.assetId      = 0

        if data is not None:
            self.deserialize(data)

    def _deserialize(self, reader: BufferReader):
        self.assetId      = reader.getUInt8() + (reader.getUInt8() << 8) + (reader.getUInt8() << 16)

    def __str__(self):
        return f"NearestCrownstoneTrackingTimeout(" \
               f"assetId={self.assetId})"
