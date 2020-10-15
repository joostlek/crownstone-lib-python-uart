# crownstone-lib-python-uart

Official Python lib for Crownstone: "Crownstone Unified System Bridge", or **Crownstone USB** implementation.

This works on all platforms and requires a **Crownstone USB** to work.

# Install guide

This module is written in Python 3 and needs Python 3.7 or higher. The reason for this is that most of the asynchronous processes use the embedded asyncio core library.

If you want to use python virtual environments, take a look at the [README_VENV](https://github.com/crownstone/CrownstoneUart-python-lib/blob/master/README_VENV.MD)

Pip is used for package management. You can install all dependencies by running:
```
python setup.py install

# or

python3 setup.py install
```

You can also install the package by pip
```python
pip3 install crownstone-uart
```

## Requirements for the Crownstone USB

### OS X
OS X requires installation of the SiliconLabs driver: [https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers](https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers)

### Ubuntu
In order to use serial without root access, you should be in the `dialout` group.

You can check if you're in the group:
```
$ groups
```

To add yourself:
```
$ sudo adduser $USER dialout
```

### Raspbian
Similar to Ubuntu.

### Arch Linux
To use serial in Arch Linux, add yourself to the `uucp` group.

To add yourself to the group:
```console
$ sudo gpasswd -a $USER uucp
```
Make sure to logout and login again to register the group change.

# Example

An example is provided in the root of this repository.

## Prerequisites

- First use the [phone app](https://crownstone.rocks/app) to setup your Crownstones and the Crownstone USB.
- Make sure you update the Crownstones' firmware to at least 2.1.0.
- Find out what port to use (e.g. `COM1`, `/dev/ttyUSB0`, or `/dev/tty.SLAB_USBtoUART`) and fill this in at `discoveryExample.py` and `example.py` at the `initializeUSB` method.
- install the CrownstoneUartLib library using the setup.py:

```python
python3 setup.py install

# or:

python setup.py install
```

## Find the IDs of your Crownstones

Firstly run the example script that simply lists the IDs of the Crownstones. They are located in /examples/examplesUsb:
```
$ python3 ./examples/discoveryExample.py
```

Some systems may require calling python3 specifically:
```
$ python3 ./examples/discoveryExample.py
```

Once some IDs are printed, use one of them for the next example. This can take a while because Crownstones, if not switched, only broadcast their state every 60 seconds.


## Switch a Crownstone, and show power usage.

After filling in the port to use, and the Crownstone ID to switch, run the example with python 3:
```
$ python example.py
```

Some systems may require calling python3 specifically:
```
$ python3 example.py
```

## The code

The example is shown below to get an idea of how everything works:

```python
#!/usr/bin/env python3

"""An example that switches a Crownstone, and prints the power usage of the selected Crownstone."""

import time
from crownstone_uart import CrownstoneUart, UartEventBus, UartTopics


# This is the id of the Crownstone we will be switching
# change it to match the Crownstone Id you want to switch!
targetCrownstoneId = 3

def showNewData(data):
	global targetCrownstoneId
	if data["id"] == targetCrownstoneId:
		print("New data received!")
		print("PowerUsage of crownstone", data["id"], data["powerUsageReal"])
		print("-------------------")


uart = CrownstoneUart()

# Start up the USB bridge.
uart.initialize_usb_sync()
# you can alternatively do this async by
# await uart.initialize_usb()

# Set up event listeners
UartEventBus.subscribe(UartTopics.newDataAvailable, showNewData)

# Switch this Crownstone on and off.
turnOn = True

# The try except part is just to catch a control+c, time.sleep does not appreciate being killed.
try:
	for i in range(0, 10):
		if not uart.running:
			break

		if turnOn:
			print("Switching Crownstone on  (iteration: ", i,")")
		else:
			print("Switching Crownstone off (iteration: ", i,")")
		uart.switch_crownstone(targetCrownstoneId, on = turnOn)

		turnOn = not turnOn
		time.sleep(2)
except KeyboardInterrupt:
	print("\nClosing example.... Thanks for your time!")

uart.stop()

```



# Documentation

This lib is used to interpret the serial data from the Crownstone USB.

This library exposes the crownstone_uart module. From this module you can use CrownstoneUart.

```python

from crownstone_uart import CrownstoneUart

# this is what you will be working with:
uart = CrownstoneUart()

```

## Switching Crownstones on, off and dimming

You can use your CrownstoneUart instance to turn Crownstones on and off. This is done using the switchCrownstone function:

```python
# this Crownstone will be switched
target_crownstone_id = 15

# turn on
uart.switch_crownstone(target_crownstone_id, on = True)

# turn off
uart.switch_crownstone(target_crownstone_id, on = False)
```

The Crownstone IDs range from 1 to 255. There is a limit of 255 Crownstones per Sphere. More on Spheres and Crownstone IDs can be found here (TODO).

To dim a Crownstone, you first need to tell it that is it allowed to dim. Currently this is done through the Crownstone app.
When it is set to allow dimming, it can dim and switch up to 100 W devices.

You can dim your Crownstones with the dimCrownstone method:

```python

# any value between 0 and 100 can be used. 0 is off, 100 is on
uart.dim_crownstone(target_crownstone_id, 50)

```

## Getting Data

The CrownstoneUart python lib uses an event bus to deliver updates to you. You can request an instance of the event bus from CrownstoneUart:

## EventBus API

You can obtain the eventBus directly from the lib:

```
from crownstone_uart import UartEventBus, UartTopics
```

##### `subscribe(topic_name: enum, function) -> subscription_id`
> Returns a subscription ID that can be used to unsubscribe again with the unsubscribe method

##### `unsubscribe(subscription_id: number)`
> This will stop the invocation of the function you provided in the subscribe method, unsubscribing you from the event.

These can be used like this:

```python

# simple example function to print the data you receive
def showNewData(data):
	print("received new data: ", data)


# Set up event listeners
UartEventBus.subscribe(UartTopics.newDataAvailable, showNewData) # keep in mind that this is using the UartTopics

# unsubscribe again
UartEventBus.unsubscribe(subscriptionId)
```

## Events

These events are available for the USB part of the lib.

##### `UartTopics.newDataAvailable`
> This is a topic with a summary of the data of a message received via the mesh. If you care about the power usage, you can get it from here. If the hasError: true, the accumulated energy is not filled, nor is the power factor and the powerUsageApparent.
> Data format is a dictionary with the fields shown below:
>```python
> {
>     id:                           int    # crownstone id (0-255)
>     setupMode:                    bool   # is in setup mode
>     switchState:                  int
>     temperature:                  int    # chip temp in Celcius
>     powerFactor:                  int    # factor between real and apparent
>     powerUsageReal:               int    # power usage in watts (W)
>     powerUsageApparent:           int    # power usage in VA
>     accumulatedEnergy:            int
>     timestamp:                    int    # time on Crownstone seconds since epoch with locale correction
>     dimmingAvailable:             bool   # dimming is available for use (it is not in the first 60 seconds after boot)
>     dimmingAllowed:               bool   # this Crownstone can dim
>     switchLocked:                 bool   # this Crownstone is switch-locked
>     hasError:                     bool   # this crownstone has an error, if the crownstone has an error, the errors: {} dict is only valid if errorMode: true. This boolean is always valid.
>     errorMode:                    bool   # summary type errorMode : the errors JSON is valid. This alternates with normal advertisements
>     errors: {
>         overCurrent:              bool
>         overCurrentDimmer:        bool
>         temperatureChip:          bool
>         temperatureDimmer:        bool
>         dimmerOnFailure:          bool
>         dimmerOffFailure:         bool
>         bitMask:                  int
>     }
>     timeIsSet:                    bool   # this crownstone knows what time it is
> }
>```

##### `UartTopics.uartMessage`
> This topic will print anything you send to the USB dongle using CrownstoneUart.uartEcho. This can be used for a ping-pong implementation.
> Data format is a dictionary with the fields shown below:
>```python
> {
>     data:             [array of bytes]
>     string:           stringified representation of the data
> }
>```



## CrownstoneUart Synchronous API

The library can be designed synchronously (blocking) or asynchronously (asyncio). We will be moving

#### `initialize_usb_sync(self, port : str = None, baudrate : int = 230400)`
>> port: optional, COM port used by the serial communication. If None or not provided automatic connect will be performed.
>>
>> baudrate: optional, set baudrate. Do not use if you don't know what this does.
>
> Sets up the communication with the Crownstone USB. This can take a few seconds and is blocking. There is a async version available.
> 
> You can optionally specify a port, but if you don't it will automatically connect to available comports and handshake. This will automatically
> connect within a second.
> For Windows devices this is commonly `COM1`, for Linux based system `/dev/ttyUSB0` and for OSX `/dev/tty.SLAB_USBtoUART`. Addresses and number can vary from system to system.

#### `switch_crownstone(crownstone_id: int, on: Boolean)`
>> crownstone_id: uid of the targeted Crownstone.
>>
>> on: True for on, False for off.
>
> Switch a Crownstone on and off
> This method is fire and forget, it will be sent over the mesh and is not acknowledged.

#### `dim_crownstone(crownstone_id: int, value: int)`
>> crownstone_id: uid of the targeted Crownstone.
>>
>> value: 0 is off, 100 is fully on.
>
> Dim the Crownstone. 0 is off, 100 is fully on. While dimming, the Crownstone is rated a maximum power usage of 100 W.
> This method is fire and forget, it will be sent over the mesh and is not acknowledged.

#### `get_crownstone_ids() -> List[int]`
> Get a list of the Crownstone IDs (ints) that are known to the library.
> After the usb is initialized, it will automatically keep a list of Crownstone IDs it has heard. Crownstones broadcast their state
> about once a minute and when they're switched. This method immediately returns with the currently known of ids

#### `stop()`
> Stop any running processes.

#### `uart_echo(text: str)`
> send a string command to the Crownstone. This will trigger a UartTopics.uartMessage event if a reply comes in.

#### `is_ready()`
> Returns True if the uart is ready for commands, False if not.

## CrownstoneUart Async API

### Async methods have to be awaited.



#### await initialize_usb(self, port = None, baudrate=230400):
> Set up the communication with the Crownstone USB.


### Mesh Module

The mesh module houses most of the mesh commands. Some of these are presented on the main CrownstoneUart class for easy access.
You can call these methods like so: 

```python
# initialization
uart = CrownstoneUart()
uart.initialize_usb_sync()

# synchronous mesh methods
uart.mesh.<method-name>

# async mesh methods
await uart.mesh.<method-name>
```

#### turn_crownstone_on(crownstone_id: int)
>> crownstone_id: uid of the targeted Crownstone.
>
> This will turn the Crownstone with the specified ID on. Turning it on with this method will respect any Twilight intensity.
> Fire and forget. Is not acked.

#### turn_crownstone_off(crownstone_id: int)
>> crownstone_id: uid of the targeted Crownstone.
>
> This will turn the Crownstone with the specified ID off.
> Fire and forget. Is not acked.

#### set_crownstone_switch(crownstone_id: int, switch_val: int)
>> crownstone_id: uid of the targeted Crownstone.
>>
>> switch_state: 0 is off, 100 is fully on.
>
> switch_val is a percentage (0 - 100) or a special value (see SwitchValSpecial). If the Crownstone can't dim, any number between 1 and 100 will turn it on.
> Fire and forget. Is not acked.

### Async methods

#### await set_time(timestamp: int = None)
>> timestamp: optional, seconds since Epoch
>
> Set the time on all Crownstones in reach of this Crownstone. If timestamp is not provided, current time is used.

#### await send_no_op()
> Send an empty message into the mesh.


#### await set_ibeacon_uuid(crownstone_id: int, uuid: str, index: int = 0) -> MeshResult
>> crownstone_id: uid of the targeted Crownstone.
>>
>> uuid: string like "d8b094e7-569c-4bc6-8637-e11ce4221c18"
>>
>> index: 0 or 1
>
> By default, the iBeacon config at index 0 is active. It is set by the Crownstone setup process. 
> This method will set the iBeacon UUID on this specific Crownstone via the mesh. 
> Returns a MeshResult class instance. Defined below.

#### await set_ibeacon_major(self, crownstone_id: int, major: int, index: int = 0) -> MeshResult:
>> crownstone_id: uid of the targeted Crownstone.
>>
>> major: int 0 - 65535
>>
>> index: 0 or 1
>
> By default, the iBeacon config at index 0 is active. It is set by the Crownstone setup process.
> This method will set the iBeacon major on this specific Crownstone via the mesh. 
> Returns a MeshResult class instance. Defined below.

#### await set_ibeacon_minor(self, crownstone_id: int, minor: int, index: int = 0) -> MeshResult:
>> crownstone_id: uid of the targeted Crownstone.
>>
>> minor: int 0 - 65535
>>
>> index: 0 or 1
>
> By default, the iBeacon config at index 0 is active. It is set by the Crownstone setup process.
> This method will set the iBeacon minor on this specific Crownstone via the mesh. 
> Returns a MeshResult class instance. Defined below.

#### await periodically_activate_ibeacon_index(self, crownstone_uid_array: List[int], index : int, interval_seconds: int, offset_seconds: int = 0) -> MeshResult:
>> crownstone_uid_array: array of Crownstone uids to target
>>
>> index: 0 or 1
>> 
>> interval_seconds: every interval_seconds the ibeacon config at this index will be activated.
>>
>> offset_seconds: if you set multiple intervals, you can use this offset to sync them up. These are based on the Crownstone time.
>
> You need to have 2 stored ibeacon payloads (at index 0 and 1) in order for this to work. This can be done by the set_ibeacon methods
> available in this module.
> ```
> Once the interval starts, it will set this ibeacon ID to be active. In order to have 2 ibeacon payloads interleaving, you have to call this method twice.
> To interleave every minute
> First,    periodically_activate_ibeacon_index, index 0, interval = 120 (2 minutes), offset = 0
> Secondly, periodically_activate_ibeacon_index, index 1, interval = 120 (2 minutes), offset = 60
> 
> This will change the active ibeacon payload every minute:
> T        = 0.............60.............120.............180.............240
> activeId = 0.............1...............0...............1...............0
> period_0 = |------------120s-------------|--------------120s-------------|
> ```

#### await stop_ibeacon_interval_and_set_index(self, crownstone_uid_array: List[int], index) -> MeshResult:
>> crownstone_uid_array: array of Crownstone uids to target
>>
>> index: 0 or 1
>
> If you have set an interval using the periodically_activate_ibeacon_index, this method will stop those intervals and
> the iBeacon config defined by index will be active for broadcasting after this method has completed.

# License

MIT

