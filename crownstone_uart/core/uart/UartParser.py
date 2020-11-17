import sys
import logging
import time

from crownstone_core.packets.ResultPacket import ResultPacket
from crownstone_core.packets.ServiceData import ServiceData
from crownstone_core.util.Conversion import Conversion

from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.core.uart.UartLogParser import UartLogParser
from crownstone_uart.core.uart.UartTypes import UartRxType, UartMessageType
from crownstone_uart.core.uart.uartPackets.UartMessagePacket import UartMessagePacket
from crownstone_uart.core.uart.uartPackets.UartWrapperPacket import UartWrapperPacket, PROTOCOL_MAJOR
from crownstone_uart.core.uart.uartPackets.AdcConfigPacket import AdcConfigPacket
from crownstone_uart.core.uart.uartPackets.CurrentSamplesPacket import CurrentSamplesPacket
from crownstone_uart.core.uart.uartPackets.PowerCalculationPacket import PowerCalculationPacket
from crownstone_uart.core.uart.uartPackets.StoneStatePacket import StoneStatePacket
from crownstone_uart.core.uart.uartPackets.VoltageSamplesPacket import VoltageSamplesPacket
from crownstone_uart.topics.DevTopics import DevTopics
from crownstone_uart.topics.SystemTopics import SystemTopics
from crownstone_uart.topics.UartTopics import UartTopics

_LOGGER = logging.getLogger(__name__)

class UartParser:
    
    def __init__(self):
        self.uartPackageSubscription = UartEventBus.subscribe(SystemTopics.uartNewPackage, self.parse)
        self.uartMessageSubscription = UartEventBus.subscribe(SystemTopics.uartNewMessage, self.handleUartMessage)
        self.uartLogParser = UartLogParser()

    def stop(self):
        UartEventBus.unsubscribe(self.uartPackageSubscription)
        UartEventBus.unsubscribe(self.uartMessageSubscription)

    def parse(self, wrapperPacket: UartWrapperPacket):
        if type(wrapperPacket) is not UartWrapperPacket:
            raise TypeError

        if wrapperPacket.protocolMajor != PROTOCOL_MAJOR:
            _LOGGER.warning(F"Unknown protocol: {wrapperPacket.protocolMajor}.{wrapperPacket.protocolMinor}")
            return

        msgType = wrapperPacket.messageType
        if msgType == UartMessageType.UART_MESSAGE:
            uartMsg = UartMessagePacket()
            if uartMsg.parse(wrapperPacket.payload):
                UartEventBus.emit(SystemTopics.uartNewMessage, uartMsg)
        else:
            _LOGGER.warning(F"Unknown message type: {msgType}")
            return

    def handleUartMessage(self, messagePacket: UartMessagePacket):
        opCode = messagePacket.opCode
        parsedData = None
        # print("UART - opCode:", opCode, "payload:", dataPacket.payload)
        if opCode == UartRxType.OWN_SERVICE_DATA:
            # service data type + device type + data type + service data (15b)
            serviceData = ServiceData(messagePacket.payload)
            if serviceData.validData:
                UartEventBus.emit(DevTopics.newServiceData, serviceData.getDictionary())

        elif opCode == UartRxType.RESULT_PACKET:
            packet = ResultPacket(messagePacket.payload)
            UartEventBus.emit(SystemTopics.resultPacket, packet)

        elif opCode == UartRxType.MESH_SERVICE_DATA:
            # data type + service data (15b)
            serviceData = ServiceData(messagePacket.payload, unencrypted=True)
            statePacket = StoneStatePacket(serviceData)
            statePacket.broadcastState()
            # if serviceData.validData:
            #     UartEventBus.emit(DevTopics.newServiceData, serviceData.getDictionary())

        elif opCode == UartRxType.OWN_SERVICE_DATA:
            # service data type + device type + data type + service data (15b)
            serviceData = ServiceData(messagePacket.payload)
            if serviceData.validData:
                UartEventBus.emit(DevTopics.newServiceData, serviceData.getDictionary())

        elif opCode == UartRxType.CROWNSTONE_ID:
            id = Conversion.int8_to_uint8(messagePacket.payload)
            UartEventBus.emit(DevTopics.ownCrownstoneId, id)

        elif opCode == UartRxType.MAC_ADDRESS:
            if len(messagePacket.payload) == 7:
                # Bug in old firmware (2.1.4 and lower) sends an extra byte.
                addr = Conversion.uint8_array_to_address(messagePacket.payload[0:-1])
            else:
                addr = Conversion.uint8_array_to_address(messagePacket.payload)
            if addr is not "":
                UartEventBus.emit(DevTopics.ownMacAddress, addr)
            else:
                print("invalid address:", messagePacket.payload)

        elif opCode == UartRxType.POWER_LOG_CURRENT:
            # type is CurrentSamples
            parsedData = CurrentSamplesPacket(messagePacket.payload)
            UartEventBus.emit(DevTopics.newCurrentData, parsedData.getDict())
            
        elif opCode == UartRxType.POWER_LOG_VOLTAGE:
            # type is VoltageSamplesPacket
            parsedData = VoltageSamplesPacket(messagePacket.payload)
            UartEventBus.emit(DevTopics.newVoltageData, parsedData.getDict())
            
        elif opCode == UartRxType.POWER_LOG_FILTERED_CURRENT:
            # type is CurrentSamples
            parsedData = CurrentSamplesPacket(messagePacket.payload)
            UartEventBus.emit(DevTopics.newFilteredCurrentData, parsedData.getDict())
            
        elif opCode == UartRxType.POWER_LOG_FILTERED_VOLTAGE:
            # type is VoltageSamplesPacket
            parsedData = VoltageSamplesPacket(messagePacket.payload)
            UartEventBus.emit(DevTopics.newFilteredVoltageData, parsedData.getDict())
            
        elif opCode == UartRxType.POWER_LOG_POWER:
            # type is PowerCalculationsPacket
            parsedData = PowerCalculationPacket(messagePacket.payload)
            UartEventBus.emit(DevTopics.newCalculatedPowerData, parsedData.getDict())
            
        elif opCode == UartRxType.ADC_CONFIG:
            # type is PowerCalculationsPacket
            parsedData = AdcConfigPacket(messagePacket.payload)
            UartEventBus.emit(DevTopics.newAdcConfigPacket, parsedData.getDict())

        elif opCode == UartRxType.ADC_RESTART:
            UartEventBus.emit(DevTopics.adcRestarted, None)

        elif opCode == UartRxType.ASCII_LOG:
            stringResult = ""
            for byte in messagePacket.payload:
                if byte < 128:
                    stringResult += chr(byte)
            logStr = "LOG: %15.3f - %s" % (time.time(), stringResult)
            sys.stdout.write(logStr)

        elif opCode == UartRxType.UART_MESSAGE:
            stringResult = ""
            for byte in messagePacket.payload:
                stringResult += chr(byte)
            # logStr = "LOG: %15.3f - %s" % (time.time(), stringResult)
            UartEventBus.emit(UartTopics.uartMessage, {"string":stringResult, "data": messagePacket.payload})

        elif opCode == UartRxType.FIRMWARESTATE:
            # no need to process this, that's in the test suite.
            pass

        elif opCode == UartRxType.EXTERNAL_STATE_PART_0:
            # no need to process this, that's in the test suite.
            pass

        elif opCode == UartRxType.EXTERNAL_STATE_PART_1:
            # no need to process this, that's in the test suite.
            pass

        elif opCode == UartRxType.MESH_RESULT:
            if len(messagePacket.payload) > 1:
                crownstoneId = messagePacket.payload[0]
                packet = ResultPacket(messagePacket.payload[1:])
                UartEventBus.emit(SystemTopics.meshResultPacket, [crownstoneId, packet])

        elif opCode == UartRxType.MESH_ACK_ALL_RESULT:
            packet = ResultPacket(messagePacket.payload)
            UartEventBus.emit(SystemTopics.meshResultFinalPacket, packet)

        elif opCode == UartRxType.LOG:
            _LOGGER.debug("received binary log:", messagePacket.payload)
            self.uartLogParser.parse(messagePacket.payload)
        else:
            _LOGGER.warning("Unknown OpCode {}".format(opCode))

        
        parsedData = None
        
