#!/usr/bin/env python3

"""An example that sets the current time in the Crownstone mesh."""
import asyncio
import time

from crownstone_core.util.Timestamp import getCorrectedLocalTimestamp

from crownstone_uart import CrownstoneUart

uart = CrownstoneUart()

# Start up the USB bridge.
async def run_example():
	# create a connection with the crownstone usb dongle.
	await uart.initialize_usb()

	# In the Crownstone app, we usually set the local time, which is the timestamp with correction for the timezone
	# The only important thing is that you use the same timezone when you set certain time-related things as you use here.
	timestamp = time.time()

	local_timestamp = getCorrectedLocalTimestamp(timestamp)
	await uart.mesh.set_time(int(local_timestamp))

	# stop the connection to the dongle
	uart.stop()

asyncio.run(run_example())
