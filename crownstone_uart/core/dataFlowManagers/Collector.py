import asyncio

class Collector:
    
    def __init__(self, timeout = 2, interval = 0.05):
        self.response = None
        self.timeout = timeout
        self.interval = interval

    async def receive(self):
        counter = 0
        while counter < self.timeout:
            if self.response is not None:
                return self.response
            await asyncio.sleep(self.interval)
            counter += self.interval
        return None

    def collect(self, data):
        self.response = data

