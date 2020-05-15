from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.topics.SystemTopics import SystemTopics
from crownstone_uart.topics.UartTopics import UartTopics


class StoneStateManager:
    def __init__(self):
        self.stones = {}
        UartEventBus.subscribe(SystemTopics.stateUpdate, self.handleStateUpdate)

    def handleStateUpdate(self, data):
        stoneId = data[0]
        stoneStatePacket = data[1]

        if stoneId in self.stones:
            if self.stones[stoneId]["timestamp"] < stoneStatePacket.serviceData.timestamp:
                self.stones[stoneId] = stoneStatePacket.getSummary()
                self.emitNewData(stoneStatePacket)
        else:
            UartEventBus.emit(SystemTopics.newCrownstoneFound, stoneId)
            self.stones[stoneId] = stoneStatePacket.getSummary()
            self.emitNewData(stoneStatePacket)
    
    def emitNewData(self, stoneStatePacket):
        UartEventBus.emit(UartTopics.newDataAvailable, stoneStatePacket.getSummary())

    def getIds(self):
        ids = []
        for stoneId, stoneData in self.stones.items():
            ids.append(stoneId)

        return ids
