import logging

from crownstone_core.Exceptions import CrownstoneError
from crownstone_core.util.DataStepper import DataStepper

from crownstone_uart.core.uart.uartPackets.UartLogHeaderPacket import UartLogHeaderPacket

_LOGGER = logging.getLogger(__name__)

class UartLogPacket:
	"""
	UART log packet
	"""

	def __init__(self, buffer: list = None):
		self.header = UartLogHeaderPacket()
		self.numArgs = 0

		# List of buffers, one for each argument.
		self.argBufs = []

		if buffer != None:
			self.parse(buffer)

	def parse(self, buffer: list):
		"""
		Parses data.

		:returns True on success.
		"""
		try:
			streamBuf = DataStepper(buffer)
			self.header.parse([], streamBuf)
			self.numArgs = streamBuf.getUInt8()
			self.argBufs = []
			for i in range(0, self.numArgs):
				argSize = streamBuf.getUInt8()
				self.argBufs.append(streamBuf.getAmountOfBytes(argSize))
			return True
		except CrownstoneError as e:
			_LOGGER.warning(F"Parse error: {e}")
			return False
