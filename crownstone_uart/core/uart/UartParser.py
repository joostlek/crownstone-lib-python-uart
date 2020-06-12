import sys
import logging
import time

from crownstone_core.packets.ResultPacket import ResultPacket
from crownstone_core.packets.ServiceData import ServiceData
from crownstone_core.util.Conversion import Conversion

from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.core.uart.UartTypes import UartRxType
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
        self.uartSubscription = UartEventBus.subscribe(SystemTopics.uartNewPackage, self.parse)

    def stop(self):
        UartEventBus.unsubscribe(self.uartSubscription)

    def parse(self, dataPacket):
        opCode = dataPacket.opCode
        parsedData = None
        # print("UART - opCode:", opCode, "payload:", dataPacket.payload)
        if opCode == UartRxType.OWN_SERVICE_DATA:
            # service data type + device type + data type + service data (15b)
            serviceData = ServiceData(dataPacket.payload)
            if serviceData.validData:
                UartEventBus.emit(DevTopics.newServiceData, serviceData.getDictionary())

        elif opCode == UartRxType.RESULT_PACKET:
            packet = ResultPacket(dataPacket.payload)
            UartEventBus.emit(SystemTopics.resultPacket, packet)

        elif opCode == UartRxType.MESH_SERVICE_DATA:
            # data type + service data (15b)
            serviceData = ServiceData(dataPacket.payload, unencrypted=True)
            statePacket = StoneStatePacket(serviceData)
            statePacket.broadcastState()
            # if serviceData.validData:
            #     UartEventBus.emit(DevTopics.newServiceData, serviceData.getDictionary())

        elif opCode == UartRxType.OWN_SERVICE_DATA:
            # service data type + device type + data type + service data (15b)
            serviceData = ServiceData(dataPacket.payload)
            if serviceData.validData:
                UartEventBus.emit(DevTopics.newServiceData, serviceData.getDictionary())

        elif opCode == UartRxType.CROWNSTONE_ID:
            id = Conversion.int8_to_uint8(dataPacket.payload)
            UartEventBus.emit(DevTopics.ownCrownstoneId, id)

        elif opCode == UartRxType.MAC_ADDRESS:
            if len(dataPacket.payload) == 7:
                # Bug in old firmware (2.1.4 and lower) sends an extra byte.
                addr = Conversion.uint8_array_to_address(dataPacket.payload[0:-1])
            else:
                addr = Conversion.uint8_array_to_address(dataPacket.payload)
            if addr is not "":
                UartEventBus.emit(DevTopics.ownMacAddress, addr)
            else:
                print("invalid address:", dataPacket.payload)

        elif opCode == UartRxType.POWER_LOG_CURRENT:
            # type is CurrentSamples
            parsedData = CurrentSamplesPacket(dataPacket.payload)
            UartEventBus.emit(DevTopics.newCurrentData, parsedData.getDict())
            
        elif opCode == UartRxType.POWER_LOG_VOLTAGE:
            # type is VoltageSamplesPacket
            parsedData = VoltageSamplesPacket(dataPacket.payload)
            UartEventBus.emit(DevTopics.newVoltageData, parsedData.getDict())
            
        elif opCode == UartRxType.POWER_LOG_FILTERED_CURRENT:
            # type is CurrentSamples
            parsedData = CurrentSamplesPacket(dataPacket.payload)
            UartEventBus.emit(DevTopics.newFilteredCurrentData, parsedData.getDict())
            
        elif opCode == UartRxType.POWER_LOG_FILTERED_VOLTAGE:
            # type is VoltageSamplesPacket
            parsedData = VoltageSamplesPacket(dataPacket.payload)
            UartEventBus.emit(DevTopics.newFilteredVoltageData, parsedData.getDict())
            
        elif opCode == UartRxType.POWER_LOG_POWER:
            # type is PowerCalculationsPacket
            parsedData = PowerCalculationPacket(dataPacket.payload)
            UartEventBus.emit(DevTopics.newCalculatedPowerData, parsedData.getDict())
            
        elif opCode == UartRxType.ADC_CONFIG:
            # type is PowerCalculationsPacket
            parsedData = AdcConfigPacket(dataPacket.payload)
            UartEventBus.emit(DevTopics.newAdcConfigPacket, parsedData.getDict())

        elif opCode == UartRxType.ADC_RESTART:
            UartEventBus.emit(DevTopics.adcRestarted, None)

        elif opCode == UartRxType.ASCII_LOG:
            stringResult = ""
            for byte in dataPacket.payload:
                if byte < 128:
                    stringResult += chr(byte)
            logStr = "LOG: %15.3f - %s" % (time.time(), stringResult)
            sys.stdout.write(logStr)
        elif opCode == UartRxType.UART_MESSAGE:
            stringResult = ""
            for byte in dataPacket.payload:
                stringResult += chr(byte)
            # logStr = "LOG: %15.3f - %s" % (time.time(), stringResult)
            UartEventBus.emit(UartTopics.uartMessage, {"string":stringResult, "data": dataPacket.payload})
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
            if len(dataPacket.payload) > 1:
                crownstoneId = dataPacket.payload[0]
                packet = ResultPacket(dataPacket.payload[1:])
                UartEventBus.emit(SystemTopics.meshResultPacket, [crownstoneId, packet])
        elif opCode == UartRxType.MESH_ACK_ALL_RESULT:
            packet = ResultPacket(dataPacket.payload)
            UartEventBus.emit(SystemTopics.meshResultFinalPacket, packet)
        else:
            _LOGGER.warning("Unknown OpCode {}".format(opCode))

        
        parsedData = None
        
