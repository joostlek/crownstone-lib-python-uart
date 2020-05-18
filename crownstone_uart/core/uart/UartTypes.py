from enum import IntEnum

class UartTxType(IntEnum):
	CONTROL =                          1

	ENABLE_ADVERTISEMENT =             10000
	ENABLE_MESH =                      10001
	
	GET_CROWNSTONE_ID =                10002
	GET_MAC_ADDRESS =                  10003

	ADC_CONFIG_INC_RANGE_CURRENT =     10103
	ADC_CONFIG_DEC_RANGE_CURRENT =     10104
	ADC_CONFIG_INC_RANGE_VOLTAGE =     10105
	ADC_CONFIG_DEC_RANGE_VOLTAGE =     10106
	ADC_CONFIG_DIFFERENTIAL_CURRENT =  10108
	ADC_CONFIG_DIFFERENTIAL_VOLTAGE =  10109
	ADC_CONFIG_VOLTAGE_PIN =           10110

	POWER_LOG_CURRENT =                10200
	POWER_LOG_VOLTAGE =                10201
	POWER_LOG_FILTERED_CURRENT =       10202
	POWER_LOG_FILTERED_VOLTAGE =       10203
	POWER_LOG_CALCULATED_POWER =       10204
	MOCK_INTERNAL_EVT =                10300 # Send events over crownstone-internal bus, this protocol may change

class UartRxType(IntEnum):
	ACK =                              0
	RESULT_PACKET =                    1
	OWN_SERVICE_DATA =                 2
	UART_MESSAGE =                     3
	MESH_SERVICE_DATA =                102
	EXTERNAL_STATE_PART_0 =			   103
	EXTERNAL_STATE_PART_1 =			   104
	MESH_RESULT = 					   105
	MESH_ACK_ALL_RESULT = 		       106

	ADVERTISING_ENABLED =              10000
	MESH_ENABLED =                     10001
	CROWNSTONE_ID =                    10002
	MAC_ADDRESS =                      10003

	ADC_CONFIG =                       10100
	ADC_RESTART =                      10101

	POWER_LOG_CURRENT =                10200
	POWER_LOG_VOLTAGE =                10201
	POWER_LOG_FILTERED_CURRENT =       10202
	POWER_LOG_FILTERED_VOLTAGE =       10203
	POWER_LOG_POWER =                  10204
	
	
	ASCII_LOG =               		   20000
	FIRMWARESTATE =                    20001