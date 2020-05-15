from typing import List

from crownstone_core import Conversion
from crownstone_core.protocol.BlePackets import ControlPacket, ControlStateSetPacket
from crownstone_core.protocol.BluenetTypes import ControlType, StateType
from crownstone_core.protocol.MeshPackets import MeshMultiSwitchPacket, StoneMultiSwitchPacket
from crownstone_uart.core.UartEventBus import UartEventBus

from crownstone_uart.core.uart.UartTypes import UartTxType
from crownstone_uart.core.uart.UartWrapper import UartWrapper
from crownstone_uart.topics.SystemTopics import SystemTopics


class MeshHandler:

    def __init__(self):
        pass

    def turnCrownstoneOn(self, crownstoneId):
        self._switchCrownstone(crownstoneId, 255)

    def turnCrownstoneOff(self, crownstoneId):
        self._switchCrownstone(crownstoneId, 255)

    def setCrownstoneSwitchState(self, crownstoneId, switchState):
        """
        :param crownstoneId:
        :param switchState: 0 .. 1
        :return:
        """

        # forcibly map the input from [any .. any] to [0 .. 1]
        correctedValue = min(1, max(0, switchState))

        self._switchCrownstone(crownstoneId, correctedValue)

    def _switchCrownstone(self,crownstoneId, switchState):
        """
        :param crownstoneId:
        :param switchState: 0 .. 255
        :return:
        """

        # create a stone switch state packet to go into the multi switch
        stoneSwitchPacket = StoneMultiSwitchPacket(crownstoneId, switchState)

        # wrap it in a mesh multi switch packet
        meshMultiSwitchPacket = MeshMultiSwitchPacket([stoneSwitchPacket]).getPacket()

        # wrap that in a control packet
        controlPacket = ControlPacket(ControlType.MULTISWITCH).loadByteArray(meshMultiSwitchPacket).getPacket()

        # finally wrap it in an Uart packet
        uartPacket = UartWrapper(UartTxType.CONTROL, controlPacket).getPacket()

        # send over uart
        UartEventBus.emit(SystemTopics.uartWriteData, uartPacket)

    def set_time(self, time):
        pass

    def send_no_op(self):
        pass

    async def set_ibeacon_uuid(self, crownstoneId: int, uuid: str, index: int = 0):
        """
        :param crownstoneId: int crownstoneUid, 1-255
        :param uuid:  string: "d8b094e7-569c-4bc6-8637-e11ce4221c18"
        :param index: for the normal uuid, index = 0, when alternating you also need to define 1 in a
                      followup command. Usually 0 has already been set by the setup procedure.
        :return:
        """
        statePacket = ControlStateSetPacket(StateType.IBEACON_UUID, index)
        statePacket.loadByteArray(Conversion.ibeaconUUIDString_to_reversed_uint8_array(uuid))
        await self._set_state_via_mesh_acked(crownstoneId, statePacket.getPacket())

    async def set_ibeacon_major(self, crownstoneId: int, major: int, index: int = 0):
        """
        :param crownstoneId: int crownstoneUid, 1-255
        :param major:  int: uint16 0-65535
        :param index: for the normal uuid, index = 0, when alternating you also need to define 1 in a
                      followup command. Usually 0 has already been set by the setup procedure.
        :return:
        """
        statePacket = ControlStateSetPacket(StateType.IBEACON_MAJOR, index)
        statePacket.loadUInt16(major)
        await self._set_state_via_mesh_acked(crownstoneId, statePacket.getPacket())

    async def set_ibeacon_minor(self, crownstoneId: int, minor: int, index: int = 0):
        """
        :param crownstoneId: int crownstoneUid, 1-255
        :param minor:  int: uint16 0-65535
        :param index: for the normal uuid, index = 0, when alternating you also need to define 1 in a
                      followup command. Usually 0 has already been set by the setup procedure.
        :return:
        """
        statePacket = ControlStateSetPacket(StateType.IBEACON_MINOR, index)
        statePacket.loadUInt16(minor)
        await self._set_state_via_mesh_acked(crownstoneId, statePacket.getPacket())


    async def periodically_activate_ibeacon_index(self, crownstone_uid_array: List[int], index, interval_seconds, offset_seconds):
        """
        You need to have 2 stored ibeacon payloads (state index 0 and 1) in order for this to work. This can be done by the set_ibeacon methods
        available in this class.

        Once the interval starts, it will set this ibeacon ID to be active. In order to have 2 ibeacon payloads interleaving, you have to call this method twice.
        To interleave every minute
        First,    periodically_activate_ibeacon_index, index 0, interval = 120 (2 minutes), offset = 0
        Secondly, periodically_activate_ibeacon_index, index 1, interval = 120 (2 minutes), offset = 60

        This will change the active ibeacon payload every minute:
        T        = 0.............60.............120.............180.............240
        activeId = 0.............1...............0...............1...............0
        period_0 = |------------120s-------------|--------------120s-------------|
        :param crownstone_uid_array:
        :param index:
        :param interval_seconds:
        :param offset_seconds:
        :return:
        """

        pass

    async def stop_ibeacon_interval_and_set_index(self, crownstone_uid_array: List[int], index):
        """
        This method stops the interleaving for the specified ibeacon payload at that index.
        :param crownstone_uid_array:
        :param index:
        :return:
        """
        pass

    async def _set_state_via_mesh_acked(self, crownstoneId: int, packet: bytearray):
        # 1:1 message to N crownstones with acks (only N = 1 supported for now)
        # flag value: 2
        pass

    def _command_via_mesh_broadcast(self, packet: bytearray):
        # this is only for time and noop
        # broadcast to all:
        # value: 1
        pass

    def _command_via_mesh_broadcast_acked(self, crownstone_uid_array: List[int], packet: bytearray):
        # this is only for the set_iBeacon_config_id
        # broadcast to all, but retry until ID's in list have acked or timeout
        # value: 3
        pass


