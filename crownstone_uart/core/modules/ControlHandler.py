import asyncio
import logging
from crownstone_core.Exceptions import CrownstoneException
from crownstone_core.packets.assetFilter.AssetFilterCommands import GetFilterSummariesReturnPacket
from crownstone_core.packets.assetFilter.FilterMetaDataPackets import AssetFilter
from crownstone_core.protocol.BluenetTypes import ResultValue
from crownstone_core.protocol.ControlPackets import ControlPacketsGenerator
from crownstone_core.util.AssetFilterUtil import FilterChunker
from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.core.dataFlowManagers.Collector import Collector
from crownstone_uart.core.uart.UartTypes import UartTxType, UartMessageType
from crownstone_uart.core.uart.uartPackets.UartMessagePacket import UartMessagePacket
from crownstone_uart.core.uart.uartPackets.UartWrapperPacket import UartWrapperPacket
from crownstone_uart.topics.SystemTopics import SystemTopics

_LOGGER = logging.getLogger(__name__)

class ControlHandler:

    async def uploadFilter(self, filterId: int, filter: AssetFilter):
        chunker = FilterChunker(filterId, filter.getPacket(), 128)
        result = None
        for i in range(0, chunker.getAmountOfChunks()):
            chunk = chunker.getChunk()
            result = await self._write(ControlPacketsGenerator.getUploadFilterPacket(chunk))
        return result


    async def removeFilter(self, filterId):
        return await self._write(ControlPacketsGenerator.getRemoveFilterPacket(filterId))


    async def getFilterSummaries(self) -> GetFilterSummariesReturnPacket:
        result = await self._write(ControlPacketsGenerator.getGetFilterSummariesPacket())
        if result is None:
            raise CrownstoneException(401, "No summaries received")
        summaries = GetFilterSummariesReturnPacket()
        summaries.fromData(result)
        return summaries


    async def commitFilterChanges(self, masterVersion: int, masterCrc: int):
        return await self._write(ControlPacketsGenerator.getCommitFilterChangesPacket(masterVersion, masterCrc))


    async def _write(self, controlPacket: [int]) -> [int] or None:
        """
        Returns the result payload.
        TODO: return result packet.
        TODO: use a ControlPacket as param, instead of int array.
        """
        _LOGGER.debug(f"Write control packet {controlPacket}")
        uartMessage = UartMessagePacket(UartTxType.CONTROL, controlPacket).getPacket()
        uartPacket = UartWrapperPacket(UartMessageType.UART_MESSAGE, uartMessage).getPacket()

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