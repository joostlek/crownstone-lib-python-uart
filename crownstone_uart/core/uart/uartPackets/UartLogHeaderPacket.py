import logging

from crownstone_core.Exceptions import CrownstoneError
from crownstone_core.util.DataStepper import DataStepper

_LOGGER = logging.getLogger(__name__)

class UartLogHeaderPacket:
	"""
	UART log header packet:
	4B filename hash
	2B line number
	1B log level
	1B flags:
	- bit 0 = newLine
	"""

	def __init__(self):
		self.fileNameHash = None
		self.lineNr = None
		self.logLevel = None
		# Flags:
		self.newLine = False

	def parse(self, buffer: list, streamBuf: DataStepper = None):
		"""
		Parses given data.

		:returns True on success.
		"""
		try:
			if streamBuf == None:
				streamBuf = DataStepper(buffer)
			self.fileNameHash = streamBuf.getUInt32()
			self.lineNr = streamBuf.getUInt16()
			self.logLevel = streamBuf.getUInt8()

			flags = streamBuf.getUInt8()
			self.newLine = (flags & (1 << 0)) != 0
			return True
		except CrownstoneError as e:
			_LOGGER.warning(F"Parse error: {e}")
			return False
