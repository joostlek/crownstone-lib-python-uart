import asyncio, logging, time
from typing import List

from crownstone_core.Exceptions import CrownstoneException
from crownstone_core.packets.ResultPacket import ResultPacket
from crownstone_core.protocol.BluenetTypes import ResultValue

from crownstone_uart.Constants import UART_WRITE_TIMEOUT
from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.topics.SystemTopics import SystemTopics

_LOGGER = logging.getLogger(__name__)

class UartWriter:

    def __init__(self, dataToSend: List[int], interval = 0.001):
        self.dataToSend : List[int] = dataToSend
        self.interval = interval

        self.error   = None
        self.success = False
        self.result  = None

        self.cleanupIds = []
        self.cleanupIds.append(UartEventBus.subscribe(SystemTopics.resultPacket,     self.handleResult))
        self.cleanupIds.append(UartEventBus.subscribe(SystemTopics.uartWriteSuccess, self.handleSuccess))
        self.cleanupIds.append(UartEventBus.subscribe(SystemTopics.uartWriteError,   self.handleError))

        self.t = time.time_ns()

    def __del__(self):
        for cleanupId in self.cleanupIds:
            UartEventBus.unsubscribe(cleanupId)

    def handleError(self, errorData):
        _LOGGER.error("Error during uart write", errorData)
        self.error = errorData
        raise errorData["error"]

    def handleResult(self, data: ResultPacket):
        self.result = data

    def handleSuccess(self, data: List[int]):
        if data == self.dataToSend:
            self.success = True

    async def send_with_result(self, success_codes=None, wait_until_result=1) -> ResultPacket:
        UartEventBus.emit(SystemTopics.uartWriteData, self.dataToSend)
        counter = 0
        while counter < wait_until_result:
            if self.result:
                if success_codes is None or success_codes == [] or self.result.resultCode in success_codes:
                    self.__del__()
                    return self.result
                else:
                    raise CrownstoneException(
                        "WRITE_EXCEPTION",
                        "Incorrect result type. Got " + str(self.result.resultCode) + ", expected one of " + str(
                            success_codes),
                        400
                    )

            await asyncio.sleep(self.interval)
            counter += self.interval

        self.__del__()
        raise CrownstoneException("WRITE_EXCEPTION", "No result received after writing to UART. Waited for " + str(wait_until_result) + " seconds", 404)

    def send_with_result_sync(self, success_codes=None, wait_until_result=1) -> ResultPacket:
        UartEventBus.emit(SystemTopics.uartWriteData, self.dataToSend)
        counter = 0
        while counter < wait_until_result:
            if self.result:
                if success_codes is None or success_codes == [] or self.result.resultCode in success_codes:
                    self.__del__()
                    return self.result
                else:
                    raise CrownstoneException(
                        "WRITE_EXCEPTION",
                        "Incorrect result type. Got " + str(self.result.resultCode) + ", expected one of " + str(success_codes),
                        400
                    )

            time.sleep(self.interval)
            counter += self.interval

        self.__del__()
        raise CrownstoneException("WRITE_EXCEPTION", "No result received after writing to UART. Waited for " + str(wait_until_result) + " seconds", 404)


    async def send(self) -> None or ResultPacket:
        UartEventBus.emit(SystemTopics.uartWriteData, self.dataToSend)
        counter = 0
        while counter < 2*UART_WRITE_TIMEOUT:
            if self.success:
                # cleanup the listener(s)
                self.__del__()
                return True

            await asyncio.sleep(self.interval)
            counter += self.interval

        # we should never arrive here. If the write went wrong, an error should have been thrown by the write method before we get here.
        self.__del__()
        raise CrownstoneException("WRITE_EXCEPTION", "Write not completed, but no error was thrown.", 500)
    
    def send_sync(self):
        UartEventBus.emit(SystemTopics.uartWriteData, self.dataToSend)
        counter = 0
        while counter < 2 * UART_WRITE_TIMEOUT:
            if self.success:
                # cleanup the listener(s)
                self.__del__()
                return True

            time.sleep(self.interval)
            counter += self.interval
        self.__del__()
        raise CrownstoneException("WRITE_EXCEPTION", "Write not completed, but no error was thrown.", 500)
