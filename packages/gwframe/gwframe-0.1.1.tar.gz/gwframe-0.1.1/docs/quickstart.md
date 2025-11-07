# Quick Start

This guide will get you up and running with gwframe in just a few minutes.

## Installation

```bash
pip install gwframe
```

## Reading GWF Files

### Basic Reading

```python
import gwframe

# Read a single channel
data = gwframe.read('data.gwf', 'L1:STRAIN')

# Access the data and metadata
print(f"Channel: {data.name}")
print(f"Sample rate: {data.sample_rate} Hz")
print(f"Duration: {data.duration} seconds")
print(f"Data shape: {data.array.shape}")
```

The `read()` function returns a `TimeSeries` object with:

- `array`: NumPy array containing the data
- `name`: Channel name
- `t0`: Start time (GPS seconds)
- `dt`: Sample spacing (seconds)
- `duration`: Total duration (seconds)
- `sample_rate`: Sampling rate (Hz)
- `unit`: Physical unit
- `type`: Channel type ('proc', 'adc', or 'sim')

### Reading Multiple Channels

```python
# Read all channels
all_data = gwframe.read('data.gwf', channel=None)
for name, ts in all_data.items():
    print(f"{name}: {len(ts.array)} samples")

# Read specific channels
channels = ['L1:STRAIN', 'L1:AUX-CHANNEL']
data_dict = gwframe.read('data.gwf', channels)
```

### Time-Based Slicing

```python
# Read data for a specific time range
data = gwframe.read(
    'multi_frame.gwf',
    'L1:STRAIN',
    start=1234567890.0,  # GPS start time
    end=1234567900.0     # GPS end time
)
```

This automatically finds, reads, and stitches together all frames overlapping with the requested time range.

### Reading from Memory

```python
# Read from file-like object
with open('data.gwf', 'rb') as f:
    data = gwframe.read(f, 'L1:STRAIN')

# Read from bytes
from io import BytesIO
with open('data.gwf', 'rb') as f:
    gwf_bytes = f.read()
data = gwframe.read_bytes(gwf_bytes, 'L1:STRAIN')
```

## Writing GWF Files

### Simple Write

```python
import numpy as np
import gwframe

# Generate some data
t = np.linspace(0, 1, 16384)
data = np.sin(2 * np.pi * 10 * t)

# Write to file
gwframe.write(
    'output.gwf',
    data,
    t0=1234567890.0,      # GPS start time
    sample_rate=16384,     # Hz
    name='L1:TEST',
    unit='strain'
)
```

### Writing Multiple Frames

The key feature of gwframe is efficient multi-frame writing:

```python
with gwframe.FrameWriter('output.gwf') as writer:
    for i in range(100):
        data = np.random.randn(16384)
        writer.write(
            data,
            t0=1234567890.0 + i,
            sample_rate=16384,
            name='L1:TEST'
        )
```

### Writing Multiple Channels

```python
# Single frame with multiple channels
gwframe.write(
    'output.gwf',
    channels={
        'L1:STRAIN': strain_data,
        'L1:AUX': aux_data
    },
    t0=1234567890.0,
    sample_rate=16384,
    name='L1'
)
```

### Advanced Frame Creation

For more control, use the `Frame` class:

```python
# Create frame
frame = gwframe.Frame(
    t0=1234567890.0,
    duration=1.0,
    name='L1',
    run=1
)

# Add channels
frame.add_channel(
    'L1:STRAIN',
    strain_data,
    sample_rate=16384,
    unit='strain',
    comment='Calibrated strain'
)

# Add metadata
frame.add_history('CREATOR', 'my_pipeline')
frame.add_history('VERSION', '1.0.0')

# Write frame
frame.write('output.gwf')
```

## Inspecting GWF Files

```python
# Get file information
info = gwframe.get_info('data.gwf')
print(f"Number of frames: {info.num_frames}")
for frame in info.frames:
    print(f"Frame {frame.index}: {frame.name} at GPS {frame.t0}, duration {frame.duration}s")

# Get available channels
channels = gwframe.get_channels('data.gwf')
for channel in channels:
    print(channel)
```

## Data Validation

Enable CRC checksum validation for data integrity:

```python
# Validate checksums when reading
data = gwframe.read(
    'data.gwf',
    'L1:STRAIN',
    validate_checksum=True
)
```

## Next Steps

- See the [Examples](examples.md) page for more detailed examples
- Check the [API Reference](reference/) for complete documentation
- Read the [Migration Guide](migration.md) if you're coming from SWIG bindings
