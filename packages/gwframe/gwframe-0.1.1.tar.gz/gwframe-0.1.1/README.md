<h1 align="center">gwframe</h1>

<p align="center">High-level Python library to work with gravitational-wave frame (GWF) files, based on framecpp</p>

<p align="center">
  <a href="https://git.ligo.org/patrick.godwin/gwframe/-/pipelines/latest">
    <img alt="ci" src="https://git.ligo.org/patrick.godwin/gwframe/badges/main/coverage.svg" />
  </a>
  <a href="https://git.ligo.org/patrick.godwin/gwframe/-/blob/main/LICENSE">
    <img alt="license" src="https://img.shields.io/badge/License-GPL%20v2-blue.svg" />
  </a>
  <a href="https://docs.ligo.org/patrick.godwin/gwframe/">
    <img alt="documentation" src="https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat" />
  </a>
  <a href="https://pypi.org/project/gwframe/">
    <img alt="pypi version" src="https://img.shields.io/pypi/v/gwframe.svg" />
  </a>
</p>

---

## Resources

* [Documentation](https://git.ligo.org/patrick.godwin/gwframe)
* [Source Code](https://git.ligo.org/patrick.godwin/gwframe)
* [Issue Tracker](https://git.ligo.org/patrick.godwin/gwframe/issues)

## Installation

With `pip`:

```bash
pip install gwframe
```

With `conda`:

```bash
conda install -c conda-forge gwframe
```

## Features

* **Multi-frame writing** - Write multiple frames to a single file
* **Multi-channel support** - Read all channels or specific lists with a single call
* **Self-contained wheels** - No external dependencies required for pip installation

## Quickstart

### Reading frames

```python
import gwframe

# Read single channel
data = gwframe.read('data.gwf', 'L1:GWOSC-16KHZ_R1_STRAIN')
print(f"Read {len(data.array)} samples at {data.sample_rate} Hz")
print(f"Time range: {data.t0} to {data.t0 + data.duration}")

# Read all channels
channels = gwframe.read('data.gwf', channel=None)
for name, timeseries in channels.items():
    print(f"{name}: {len(timeseries.array)} samples")

# Time-based slicing (automatically stitches multiple frames)
data = gwframe.read('multi_frame.gwf', 'L1:STRAIN',
                    start=1234567890.0, end=1234567900.0)
```

### Writing single frames

```python
import gwframe
import numpy as np

data = np.random.randn(16384)
gwframe.write('output.gwf', data, t0=1234567890.0,
              sample_rate=16384, name='L1:TEST')
```

### Writing multiple frames

```python
import gwframe
import numpy as np

# Write multiple frames to a single file
with gwframe.FrameWriter('multi_frame.gwf') as writer:
    for i in range(20):
        data = np.random.randn(16384)
        writer.write(data, t0=1234567890.0 + i,
                     sample_rate=16384, name='L1:TEST')
```

### Inspecting frames

```python
import gwframe

# Get frame information
info = gwframe.get_info('data.gwf')
print(f"Number of frames: {info.num_frames}")
for frame in info.frames:
    print(f"Frame {frame.index}: {frame.name} at GPS {frame.t0}, duration {frame.duration}s")

# List all channels
channels = gwframe.get_channels('data.gwf')
num_channels = len(channels)
for channel in channels:
    print(channel)
```

### Advanced: Full control with Frame objects

```python
import gwframe
import numpy as np

# Create frame with multiple channels and metadata
frame = gwframe.Frame(
    t0=1234567890.0,
    duration=1.0,
    name='L1',
    run=1
)

# Add channels
strain = np.random.randn(16384)
frame.add_channel('L1:STRAIN', strain,
                  sample_rate=16384,
                  unit='strain',
                  channel_type='proc')

aux = np.random.randn(1024).astype(np.float32)
frame.add_channel('L1:AUX', aux,
                  sample_rate=1024,
                  unit='counts',
                  channel_type='adc')

# Add metadata
frame.add_history('gwframe', 'Created with gwframe')

# Write with custom compression
frame.write('output.gwf', compression=gwframe.Compression.GZIP)
```

## CLI Tools

`gwframe` includes a command-line interface for common frame manipulation tasks:

```bash
# Rename channels
gwframe rename input.gwf -o output.gwf -m "L1:OLD=>L1:NEW"

# Combine channels from multiple files
gwframe combine file1.gwf file2.gwf -o output/

# Remove unwanted channels
gwframe drop input.gwf -o output.gwf -c L1:UNWANTED

# Change frame duration
gwframe resize input.gwf -o output/ -d 4.0

# Replace NaN or sentinel values
gwframe impute input.gwf -o output.gwf --fill-value 0.0

# Update channel data from another file
gwframe replace base.gwf --update new.gwf -o output/ -c L1:STRAIN

# Change compression settings
gwframe recompress input.gwf -o output.gwf -c GZIP -l 9
```

All commands support batch processing with directories and glob patterns. See
the [CLI documentation](https://docs.ligo.org/patrick.godwin/gwframe/cli/) for
detailed usage and examples.
