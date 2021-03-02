import logging

from crownstone_core.packets.BasePacket import BasePacket
from crownstone_core.util.DataStepper import DataStepper

from crownstone_uart.core.uart.uartPackets.UartLogHeaderPacket import UartLogHeaderPacket

_LOGGER = logging.getLogger(__name__)

class UartLogPacket(BasePacket):
	"""
	UART log packet
	"""

	def __init__(self, data = None):
		self.header = UartLogHeaderPacket()
		self.numArgs = 0

		# List of buffers, one for each argument.
		self.argBufs = []

		if data != None:
			self.parse(data)

	def _parse(self, dataStepper: DataStepper):
		self.header.parse(dataStepper)
		self.numArgs = dataStepper.getUInt8()
		self.argBufs = []
		for i in range(0, self.numArgs):
			argSize = dataStepper.getUInt8()
			self.argBufs.append(dataStepper.getAmountOfBytes(argSize))

	def __str__(self):
		return f"UartLogPacket(" \
		       f"header={self.header}, " \
		       f"numArgs={self.numArgs}, " \
		       f"argBufs={self.argBufs})"
