from crownstone_core.util.Conversion import Conversion

from crownstone_uart.core.uart.uartPackets.StoneStatePacket import STONE_STATE_PACKET_SIZE, StoneStatePacket

MESH_STATE_PACKET_SIZE = 92
MAX_STATE_ITEMS = 6

class MeshStatePacket:

	def __init__(self, payload):
		self.stoneStates = []
		
		if len(payload) != MESH_STATE_PACKET_SIZE:
			print("ERROR: INVALID PAYLOAD LENGTH", len(payload), payload)
			return
		self.stoneStates = []
		self.head = payload[0]
		self.tail = payload[1]
		self.size = payload[2]
		self.timestamp = Conversion.uint8_array_to_uint32(payload[4:8])

		expectedSizeOfStoneStates = self.size * STONE_STATE_PACKET_SIZE

		if expectedSizeOfStoneStates + 8 > MESH_STATE_PACKET_SIZE:
			print("ERROR: CANT FIT STONE STATE PACKETS IN MESSAGE", expectedSizeOfStoneStates)
			return

		for i in range(0,self.size):
			self.stoneStates.append(StoneStatePacket(payload[8+i*STONE_STATE_PACKET_SIZE:8+(i+1)*STONE_STATE_PACKET_SIZE]))

		# deprecation is when a stone id has multiple entrees in the data. Checking for this makes sure we only use the latest one.
		self._checkForDeprecation()


	def _checkForDeprecation(self):
		# point to the newest item in this meshStatePacket
		newestItem = (self.head + self.size - 1) % MAX_STATE_ITEMS

		# we start there
		itemIndex = newestItem

		seenStoneIds = set()

		for i in range(0,self.size):
			stoneId = self.stoneStates[itemIndex].serviceData.crownstoneId
			if stoneId in seenStoneIds:
				self.stoneStates[itemIndex].deprecated = True
			else:
				seenStoneIds.add(stoneId)

			# point to the next newest item in the list
			itemIndex = (itemIndex - 1 + MAX_STATE_ITEMS) % MAX_STATE_ITEMS



