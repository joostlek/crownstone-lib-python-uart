import threading
import time
import asyncio

"""
An example that switches a Crownstone, and prints the power usage of the selected Crownstone.

But now it runs it its own thread.
"""

from crownstone_uart import CrownstoneUart

# This is the id of the Crownstone we will be switching
# change it to match the Crownstone Id you want to switch!
targetCrownstoneId = 38


class UartThreadExample(threading.Thread):

    def __init__(self):
        self.loop = None
        self.uart = None
        threading.Thread.__init__(self)

    def run(self):
        self.loop = asyncio.new_event_loop()
        self.uart = CrownstoneUart()
        # choose either sync, or async operation
        self.loop.run_until_complete(self.runIt())
        # self.runIt_sync()


    async def runIt(self):
        await self.uart.initialize_usb()
        self.switch_crownstone()

    def runIt_sync(self):
        self.uart.initialize_usb_sync()
        self.switch_crownstone()

    def switch_crownstone(self):
        turnOn = True
        for i in range(0, 10):
            if not self.uart.running:
                break

            if turnOn:
                print("Switching Crownstone on  (iteration: ", i,")")
            else:
                print("Switching Crownstone off (iteration: ", i,")")
            self.uart.switch_crownstone(targetCrownstoneId, on = turnOn)
            turnOn = not turnOn
            time.sleep(2)

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