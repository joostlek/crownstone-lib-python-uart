#!/usr/bin/env python3

"""An example that prints all Crownstone IDs seen on the mesh."""
import time

# Create new instance of Bluenet
from crownstone_uart import CrownstoneUart

uart = CrownstoneUart()

# Start up the USB bridge.
uart.initialize_usb_sync()
# you can alternatively do this async by
# await uart.initialize_usb()

# List the ids that have been seen
print("Listening for Crownstones on the mesh, this might take a while.")

# the try except part is just to catch a control+c, time.sleep does not appreciate being killed.
initial_time = time.time()
try:
	while uart.running:
		time.sleep(2)
		ids = uart.get_crownstone_ids()
		print("Crownstone IDs seen so far:", ids, "after", round(time.time() - initial_time), "seconds")
except KeyboardInterrupt:
	print("\nClosing example.... Thank you for your time!")
except:
	print("\nClosing example.... Thank you for your time!")

uart.stop()
