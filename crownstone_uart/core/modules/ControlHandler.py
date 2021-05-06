import asyncio

from crownstone_core.packets.assetFilters.FilterMetaDataPackets import FilterMetaData
from crownstone_core.packets.assetFilters.FilterPackets import FilterSummaries
from crownstone_core.protocol.ControlPackets import ControlPacketsGenerator
from crownstone_core.util.FilterUtil import FilterChunker

from crownstone_core.Exceptions import CrownstoneException
from crownstone_core.protocol.BluenetTypes import ResultValue

from crownstone_uart.core.dataFlowManagers.Collector import Collector
from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.topics.SystemTopics import SystemTopics


class ControlHandler:

    async def uploadFilter(self, filterId: int, metaData: FilterMetaData, filterData: [int]):
        fullData = metaData.getPacket() + filterData
        chunker = FilterChunker(filterId, fullData)
        for i in range(0,chunker.getAmountOfChunks()):
            chunk = chunker.getChunk()
            await self._write(ControlPacketsGenerator.getUploadFilterPacket(chunk))


    async def removeFilter(self, filterId):
        return self._write(ControlPacketsGenerator.getRemoveFilterPacket(filterId))


    async def getFilterSummaries(self) -> FilterSummaries:
        result = await self._write(ControlPacketsGenerator.getGetFilterSummariesPacket())
        if result is None:
            raise CrownstoneException(401, "No summaries received")
        summaries = FilterSummaries()
        summaries.fromData(result)
        return summaries


    async def commitFilterChanges(self, masterVersion: int, masterCrc: int):
        return self._write(ControlPacketsGenerator.getCommitFilterChangesPacket(masterVersion, masterCrc))


    async def _write(self, uartPacket: [int]) -> [int] or None:
        resultCollector = Collector(timeout=1, topic=SystemTopics.resultPacket)
        # send the message to the Crownstone
        UartEventBus.emit(SystemTopics.uartWriteData, uartPacket)

        # wait for the collectors to fill
        commandResultData = await resultCollector.receive()

        if commandResultData is not None:
            if commandResultData.resultCode is not ResultValue.SUCCESS:
                raise CrownstoneException(commandResultData.resultCode, "Command has failed.")
            return commandResultData.payload
        return None