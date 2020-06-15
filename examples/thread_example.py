import threading
import time
import asyncio, logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

from crownstone_uart import CrownstoneUart

class UartThreadExample(threading.Thread):

    def __init__(self):
        self.loop = None
        self.uart = None
        threading.Thread.__init__(self)

    def run(self):
        self.loop = asyncio.new_event_loop()
        self.uart = CrownstoneUart(self.loop)
        # choose either sync, or async operation
        self.loop.run_until_complete(self.runIt())
        # self.runIt_sync()


    async def runIt(self):
        await self.uart.initialize_usb()

    def runIt_sync(self):
        self.uart.initialize_usb_sync()

    def stop(self):
        self.uart.stop()


thread = UartThreadExample()
thread.start()

try:
    while 1:
        print("tick")
        time.sleep(1)
except KeyboardInterrupt:
    print("\nClosing example.... Thanks for your time!")

thread.stop()