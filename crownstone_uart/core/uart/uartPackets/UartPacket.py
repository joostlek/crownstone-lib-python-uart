from crownstone_core.util.Conversion import Conversion

OPCODE_SIZE = 2
LENGTH_SIZE = 2
CRC_SIZE    = 2

PREFIX_SIZE  = OPCODE_SIZE + LENGTH_SIZE
WRAPPER_SIZE = PREFIX_SIZE + CRC_SIZE

class UartPacket:
	def __init__(self, data):
		self.opCode	 = Conversion.uint8_array_to_uint16(data[0:OPCODE_SIZE])
		self.length  = Conversion.uint8_array_to_uint16(data[OPCODE_SIZE:PREFIX_SIZE])
		self.payload = data[PREFIX_SIZE:PREFIX_SIZE + self.length]
		self.crc 	 = Conversion.uint8_array_to_uint16(data[len(data) - CRC_SIZE : len(data)])