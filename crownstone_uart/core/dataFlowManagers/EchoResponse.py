import asyncio

from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.topics.UartTopics import UartTopics

class EchoResponse:
    
    def __init__(self, timeout, interval = 0.05):
        self.response = None
        self.timeout = timeout
        self.interval = interval
        self.handshakeId = UartEventBus.subscribe(UartTopics.uartMessage, self.handleReply)

    def __del__(self):
        UartEventBus.unsubscribe(self.handshakeId)

    async def collect(self):
        counter = 0
        while counter < self.timeout:
            if self.response is not None:
                UartEventBus.unsubscribe(self.handshakeId)
                return self.response
            await asyncio.sleep(self.interval)
            counter += self.interval
        UartEventBus.unsubscribe(self.handshakeId)
        return None

    def handleReply(self, reply):
        self.response = reply

