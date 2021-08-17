# Documentation

This lib is used to interpret the serial data from the Crownstone USB.

## Async functions

This library uses async methods. This is part of Python and uses the asyncio core module to do this. Async methods must be awaited.
If you're unsure about how to use these, there's a million guides and tutorials online. We will assume you know how to use these in the rest of the documentation.

## Usage

This library exposes the crownstone_uart module. From this module you can use CrownstoneUart.

```python

from crownstone_uart import CrownstoneUart

# this is what you will be working with:
uart = CrownstoneUart()

```


### Switching Crownstones on, off and dimming

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


# API

The library can be designed synchronously (blocking) or asynchronously (asyncio). The async methods are prefixed by the `async` keyword.

**Async methods have to be awaited.**

### `initialize_usb_sync(port : str = None, baudrate : int = 230400)`
> port: optional, COM port used by the serial communication. If None or not provided automatic connect will be performed.
>
> baudrate: optional, set baudrate. Do not use if you don't know what this does.

Sets up the communication with the Crownstone USB. This can take a few seconds and is blocking. There is a async version available.

You can optionally specify a port, but if you don't it will automatically connect to available comports and try a handshake. This will automatically
connect within a second.
For Windows devices this is commonly `COM1`, for Linux based system `/dev/ttyUSB0` and for OSX `/dev/tty.SLAB_USBtoUART`. Addresses and number can vary from system to system.

### `async initialize_usb(port = None, baudrate=230400):`
Set up the communication with the Crownstone USB using an async method.

### `switch_crownstone(crownstone_id: int, on: Boolean)`
Switch a Crownstone on or off.
This method is fire and forget, it will be sent over the mesh and is not acknowledged.

### `dim_crownstone(crownstone_id: int, value: int)`
Dim a Crownstone. 0 is off, 100 is fully on. While dimming, the Crownstone is rated a maximum power usage of 100 W.
This method is fire and forget, it will be sent over the mesh and is not acknowledged.

### `get_crownstone_ids() -> List[int]`
Get a list of the Crownstone IDs (ints) that are known to the library.
After the usb is initialized, it will automatically keep a list of Crownstone IDs it has heard. Crownstones broadcast their state
about once a minute and when they're switched. This method immediately returns the currently known IDs.

### `stop()`
Stop any running processes.

### `uart_echo(text: str)`
Send a string command to the Crownstone. This will trigger a UartTopics.uartMessage event if a reply comes in.

### `is_ready()`
Returns True if the uart is ready for commands, False if not.



## Mesh module

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

### `turn_crownstone_on(crownstone_id: int)`
This will turn the Crownstone with the specified ID on. Turning it on with this method will respect any Twilight intensity.
Fire and forget. Is not acked.

### `turn_crownstone_off(crownstone_id: int)`
This will turn the Crownstone with the specified ID off.
Fire and forget. Is not acked.

### `set_crownstone_switch(crownstone_id: int, switch_val: int)`
You can switch the Crownstone. 0 for off, 100 for on, between 0 and 100 to dim. If the Crownstone can't dim, any number between 1 and 100 will turn it on.
Fire and forget. Is not acked.

### `async set_time(timestamp: int = None)`
Set the time on all Crownstones in reach of this Crownstone. If timestamp is not provided, current time is used. Time is defined in seconds since epoch. The lib will transform this timestamp
to one that corrects for the timezone.

### `async send_no_op()`
Send an empty message into the mesh.


### `async set_ibeacon_uuid(crownstone_id: int, uuid: str, index: int = 0) -> MeshResult`
> crownstone_id: uid of the targeted Crownstone.
>
> uuid: string like "d8b094e7-569c-4bc6-8637-e11ce4221c18"
>
> index: 0 or 1

By default, the iBeacon config at index 0 is active. It is set by the Crownstone setup process. 
This method will set the iBeacon UUID on this specific Crownstone via the mesh. 
Returns a MeshResult class instance. Defined below.

### `async set_ibeacon_major(crownstone_id: int, major: int, index: int = 0) -> MeshResult`
> crownstone_id: uid of the targeted Crownstone.
>
> major: int 0 - 65535
>
> index: 0 or 1

By default, the iBeacon config at index 0 is active. It is set by the Crownstone setup process.
This method will set the iBeacon major on this specific Crownstone via the mesh. 
Returns a MeshResult class instance. Defined below.

### `async set_ibeacon_minor(crownstone_id: int, minor: int, index: int = 0) -> MeshResult`
> crownstone_id: uid of the targeted Crownstone.
>
> minor: int 0 - 65535
>
> index: 0 or 1

By default, the iBeacon config at index 0 is active. It is set by the Crownstone setup process.
This method will set the iBeacon minor on this specific Crownstone via the mesh. 
Returns a MeshResult class instance. Defined below.

### `async periodically_activate_ibeacon_index(crownstone_uid_array: List[int], index : int, interval_seconds: int, offset_seconds: int = 0) -> MeshResult`
> crownstone_uid_array: array of Crownstone uids to target
>
> index: 0 or 1
> 
> interval_seconds: every interval_seconds the ibeacon config at this index will be activated.
>
> offset_seconds: if you set multiple intervals, you can use this offset to sync them up. These are based on the Crownstone time.

You need to have 2 stored ibeacon payloads (at index 0 and 1) in order for this to work. This can be done by the set_ibeacon methods
available in this module.
```
Once the interval starts, it will set this ibeacon ID to be active. In order to have 2 ibeacon payloads interleaving, you have to call this method twice.
To interleave every minute
First,    periodically_activate_ibeacon_index, index 0, interval = 120 (2 minutes), offset = 0
Secondly, periodically_activate_ibeacon_index, index 1, interval = 120 (2 minutes), offset = 60

This will change the active ibeacon payload every minute:
T        = 0.............60.............120.............180.............240
activeId = 0.............1...............0...............1...............0
period_0 = |------------120s-------------|--------------120s-------------|
```

### `async stop_ibeacon_interval_and_set_index(crownstone_uid_array: List[int], index) -> MeshResult`
> crownstone_uid_array: array of Crownstone uids to target
>
> index: 0 or 1

If you have set an interval using the periodically_activate_ibeacon_index, this method will stop those intervals and
the iBeacon config defined by index will be active for broadcasting after this method has completed.

### Control Module
This houses a number of control commands. More will be added when required.
```python
# initialization
uart = CrownstoneUart()
uart.initialize_usb_sync()

# synchronous control methods
uart.control.<method-name>

# async control methods
await uart.control.<method-name>
```

### `async def setFilters(self, filters: List[AssetFilter], masterVersion: int = None) -> int:`
Makes sure the given filters are set at the Crownstones.
Uploads and removes filters where necessary.




## EventBus API
The CrownstoneUart python lib uses an event bus to deliver updates to you.
You can obtain the eventBus directly from the lib:

```
from crownstone_uart import UartEventBus, UartTopics
```

### `subscribe(topic_name: enum, function) -> subscription_id`
Returns a subscription ID that can be used to unsubscribe again with the unsubscribe method

### `unsubscribe(subscription_id: number)`
This will stop the invocation of the function you provided in the subscribe method, unsubscribing you from the event.

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

### `UartTopics.newDataAvailable`
This is a topic to which events are posted which are unique. The same message will be repeated on the advertisement and the rawAdvertisement packets.
The payload of this event is different depending on what kind of data is received by the dongle.
These payloads all have a `type` field [which is defined here.](https://github.com/crownstone/crownstone-lib-python-core/blob/master/crownstone_core/packets/serviceDataParsers/containers/elements/AdvTypes.py)
Payloads come in these flavours:

- [CROWNSTONE_STATE](https://github.com/crownstone/crownstone-lib-python-core/blob/master/crownstone_core/packets/serviceDataParsers/containers/AdvCrownstoneState.py)
- [CROWNSTONE_ERROR](https://github.com/crownstone/crownstone-lib-python-core/blob/master/crownstone_core/packets/serviceDataParsers/containers/AdvErrorPacket.py)
- [EXTERNAL_STATE](https://github.com/crownstone/crownstone-lib-python-core/blob/master/crownstone_core/packets/serviceDataParsers/containers/AdvExternalCrownstoneState.py)
- [EXTERNAL_ERROR](https://github.com/crownstone/crownstone-lib-python-core/blob/master/crownstone_core/packets/serviceDataParsers/containers/AdvExternalErrorPacket.py)
- [ALTERNATIVE_STATE](https://github.com/crownstone/crownstone-lib-python-core/blob/master/crownstone_core/packets/serviceDataParsers/containers/AdvAlternativeState.py)
- [HUB_STATE](https://github.com/crownstone/crownstone-lib-python-core/blob/master/crownstone_core/packets/serviceDataParsers/containers/AdvHubState.py)
- [MICROAPP_DATA](https://github.com/crownstone/crownstone-lib-python-core/blob/master/crownstone_core/packets/serviceDataParsers/containers/AdvMicroappData.py)
- [SETUP_STATE](https://github.com/crownstone/crownstone-lib-python-core/blob/master/crownstone_core/packets/serviceDataParsers/containers/AdvCrownstoneSetupState.py)



### `UartTopics.uartMessage`
This topic will print anything you send to the USB dongle using CrownstoneUart.uartEcho. This can be used for a ping-pong implementation. Data format is a dictionary with the fields shown below:
```python
 {
     data:             [array of bytes]
     string:           stringified representation of the data
 }
```

### `UartTopics.assetTrackingReport`
This topic will give you a AssetMacReport class from the asset tracking system. This is only emitted if you've configured your Crownstone to do so.

### `UartTopics.nearestCrownstoneTrackingUpdate`
This topic will give you a NearestCrownstoneTrackingUpdate class from the asset localization system. This is only emitted if you've configured your Crownstone to do so.

### `UartTopics.nearestCrownstoneTrackingTimeout`
This topic will give you a NearestCrownstoneTrackingTimeout class from the asset localization system. This is only emitted if you've configured your Crownstone to do so.
