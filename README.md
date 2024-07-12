# SRBand

The `SRBand` class is used to monitor a value within a specified range, triggering events when the value crosses high and low thresholds.

## Installation

You can install SRBand from the REPL with mip.
```python
# micropython REPL
import mip
mip.install("github:surdouski/micropython-SRBand")
```

Alternatively, you can install it by using mpremote if you don't have network connectivity on device.
```
$ mpremote mip install github:surdouski/micropython-SRBand
```

## Usage

Here is an example of how to use the `SRBand` class:

```python
import asyncio
from sr_band import SRBand

async def main():
    # Initialize the SRBand with target, high, and low values
    band = SRBand(target=50, high=70, low=30)
    
    # Setup some tasks to trigger when the event is set
    # Don't forget to clear your events inside the tasks
    task1 = asyncio.create_task(do_something(sr.fall_event))
    task2 = asyncio.create_task(do_something(sr.rise_event))
    
    # This should trigger the fall_event 
    band.update(75)  # internal status: SET_FALL
    await asyncio.sleep(1)
    
    band.update(25)  # This should trigger the rise_event
    await asyncio.sleep(1)  # internal status: SET_RISE

    # These will trigger 3 more rise_event:    
    band.update(29)  # Successive updates after a triggered;        internal status: SET_RISE
    band.update(31)  # event, but while still below the;            internal status: SET_RISE
    band.update(49)  # target, will continue triggering that event. internal status: SET_RISE
    
    # No event is triggered here, as it has passed (or is equal to) the reset point.
    band.update(51)  # internal status: IDLE
    
    # cleanup tasks
    task1.cancel()
    task2.cancel()

async def do_something(event: asyncio.Event):
    while True:
        await event.wait()
        event.clear()
        # do stuff here
        
# Run the async main function
asyncio.run(main())
```

### SRBand Class

#### `SRBand(target: float, high: float, low: float)`
Initializes an `SRBand` object with specified target, high, and low thresholds.

**Parameters:**
- `target` (float): The target value.
- `high` (float): The high threshold.
- `low` (float): The low threshold.

**Raises:**
- `SRBandException`: If the provided arguments do not satisfy `low < target < high`.

#### `update(new_value: float) -> None`
Updates the current value and triggers events if thresholds are crossed.

**Parameters:**
- `new_value` (float): The new value to update.

### SRBandException Class

Custom exception for the `SRBand` class.

## Tests

To run tests, do the following.
```
# install unittest, mounting the volume locally
$ docker run --rm -v $(pwd)/lib:/root/.micropython/lib micropython/unix micropython -m mip install unittest

# run the test, using the mounted volume for the unittest deps
$ docker run --rm -v $(pwd):/code -v $(pwd)/lib:/root/.micropython/lib micropython/unix micropython test.py
```

If you want to edit tests, you only need to run the last command again to see results.


## License

This project is licensed under the MIT License. See the LICENSE file for details.
