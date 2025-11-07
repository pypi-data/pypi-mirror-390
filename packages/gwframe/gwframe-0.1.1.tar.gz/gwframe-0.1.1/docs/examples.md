# Examples

This page provides comprehensive examples of using gwframe for various tasks.

## Reading Examples

### Example 1: Basic File Reading

Read a single channel from a GWF file and inspect the data:

```python
import gwframe
import numpy as np

# Read channel data
data = gwframe.read('L-L1_GWOSC_16KHZ_R1-1240215487-32.gwf', 'L1:GWOSC-16KHZ_R1_STRAIN')

# Print metadata
print(f"Channel: {data.name}")
print(f"Type: {data.type}")
print(f"Start time (GPS): {data.t0:.9f}")
print(f"Duration: {data.duration:.1f} seconds")
print(f"Sample rate: {data.sample_rate:.1f} Hz")
print(f"Array shape: {data.array.shape}")
print(f"Array dtype: {data.array.dtype}")

# Access the numpy array
strain = data.array
print(f"Data range: [{strain.min():.6e}, {strain.max():.6e}]")
print(f"RMS: {np.sqrt(np.mean(strain**2)):.6e}")

# Create time array
t = np.arange(len(strain)) * data.dt
print(f"Time span: {t[0]:.6f} to {t[-1]:.6f} seconds")
```

### Example 2: File Inspection

Get information about a GWF file before reading:

```python
import gwframe

# Get file information
info = gwframe.get_info('data.gwf')
print(f"Number of frames: {info.num_frames}")

# Print frame details
for frame in info.frames:
    print(f"Frame {frame.index}: {frame.name} at GPS {frame.t0:.6f}, duration {frame.duration:.1f}s")

# Get available channels
channels = gwframe.get_channels('data.gwf')
if channels:
    for channel in channels:
        print(channel)
```

### Example 3: Time-Based Slicing

Read data for a specific time range spanning multiple frames:

```python
import gwframe

# Read 10 seconds of data starting at GPS 1234567890
data = gwframe.read(
    'multi_frame.gwf',
    'L1:STRAIN',
    start=1234567890.0,
    end=1234567900.0
)

print(f"Read {data.duration} seconds from {data.t0} to {data.t0 + data.duration}")
print(f"Total samples: {len(data.array)}")
```

### Example 4: Reading from Memory

Read GWF data from memory without writing to disk:

```python
import gwframe
from io import BytesIO

# Read from file-like object
with open('data.gwf', 'rb') as f:
    data = gwframe.read(f, 'L1:STRAIN')

# Read from BytesIO
with open('data.gwf', 'rb') as f:
    gwf_bytes = f.read()
data = gwframe.read_bytes(gwf_bytes, 'L1:STRAIN')

# Read from BytesIO object
bio = BytesIO(gwf_bytes)
data = gwframe.read(bio, 'L1:STRAIN')
```

## Writing Examples

### Example 5: Simple Single-Channel Write

Write a single channel to a GWF file:

```python
import numpy as np
import gwframe

# Generate test data
data = np.sin(np.linspace(0, 2 * np.pi, 16384))

# Write to file
gwframe.write(
    'output.gwf',
    data,
    t0=1234567890.0,
    sample_rate=16384,
    name='H1:TEST-SINE',
    unit='strain'
)

# Verify
result = gwframe.read('output.gwf', 'H1:TEST-SINE')
print(f"Wrote {len(data)} samples, read back {len(result.array)} samples")
print(f"Data integrity: {np.allclose(data, result.array)}")
```

### Example 6: Multiple Channels

Write multiple channels with different units:

```python
import numpy as np
import gwframe

# Generate different types of data
strain = np.random.randn(16384) * 1e-21  # Simulated strain
darm = np.random.randn(16384)             # Simulated DARM
laser_power = np.random.randn(16384) + 100  # Simulated laser power

# Write all channels to one file
gwframe.write(
    'multi_channel.gwf',
    channels={
        'L1:GDS-CALIB_STRAIN': strain,
        'L1:LSC-DARM_ERR': darm,
        'L1:PSL-LASER_POWER': laser_power
    },
    t0=1234567890.0,
    sample_rate=16384,
    name='L1',
    unit={
        'L1:GDS-CALIB_STRAIN': 'strain',
        'L1:LSC-DARM_ERR': 'counts',
        'L1:PSL-LASER_POWER': 'W'
    }
)

# Verify channels were written
channels = gwframe.get_channels('multi_channel.gwf')
print(f"Wrote {len(channels)} channels: {channels}")
```

### Example 7: Multi-Frame Writing

Write multiple frames efficiently using `FrameWriter`:

```python
import numpy as np
import gwframe

start_time = 1234567890.0
sample_rate = 16384
samples_per_frame = sample_rate  # 1 second per frame

# Write 10 one-second frames
with gwframe.FrameWriter('multi_frame.gwf') as writer:
    for i in range(10):
        # Generate test data (sine wave with increasing frequency)
        t = np.linspace(0, 1, samples_per_frame)
        data = np.sin(2 * np.pi * (10 + i) * t)

        # Write frame
        t0 = start_time + i
        writer.write(
            data,
            t0=t0,
            sample_rate=sample_rate,
            name='L1:TEST-STRAIN'
        )
        print(f"Wrote frame {i+1}: GPS {t0:.1f}")

# Verify file
info = gwframe.get_info('multi_frame.gwf')
print(f"File contains {info.num_frames} frames")
```

### Example 8: Advanced Frame Creation with Metadata

Use the `Frame` class for full control:

```python
import numpy as np
import gwframe

# Create frame with metadata
frame = gwframe.Frame(
    t0=1234567890.0,
    duration=1.0,
    name='H1',
    run=12345,
    frame_number=1
)

# Add history/metadata
frame.add_history('CREATOR', 'gwframe demo')
frame.add_history('VERSION', '0.1.0')
frame.add_history('PIPELINE', 'test_pipeline')

# Add multiple channels
frame.add_channel(
    'H1:STRAIN',
    np.random.randn(16384),
    sample_rate=16384,
    unit='strain',
    comment='Calibrated gravitational wave strain'
)
frame.add_channel(
    'H1:DARM',
    np.random.randn(16384),
    sample_rate=16384,
    unit='counts',
    comment='Differential arm length'
)

# Write frame
frame.write('frame_with_metadata.gwf')
print(f"Created frame: {frame}")
```

### Example 9: Writing Frame Objects with FrameWriter

Combine `Frame` objects with `FrameWriter` for maximum control:

```python
import numpy as np
import gwframe

start_time = 1234567890.0
sample_rate = 16384

with gwframe.FrameWriter('advanced_multi.gwf') as writer:
    for i in range(5):
        # Create frame with 2-second duration
        t0 = start_time + i * 2
        duration = 2.0
        frame = gwframe.Frame(t0=t0, duration=duration, name='L1', run=1)

        # Add multiple channels
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples)
        strain = np.sin(2 * np.pi * 10 * t)
        aux = np.cos(2 * np.pi * 5 * t)

        frame.add_channel('L1:STRAIN', strain, sample_rate=sample_rate, unit='strain')
        frame.add_channel('L1:AUX', aux, sample_rate=sample_rate, unit='counts')

        # Add metadata
        frame.add_history('PROCESSING', f'Demo frame {i+1}')

        # Write frame
        writer.write_frame(frame)
        print(f"Wrote frame {i+1}: 2 channels, {duration}s duration")

info = gwframe.get_info('advanced_multi.gwf')
print(f"File contains {info.num_frames} frames")
```

## Data Type Examples

### Example 10: Different NumPy Data Types

gwframe supports various NumPy data types:

```python
import numpy as np
import gwframe

data_types = {
    'FLOAT64': np.array([1.0, 2.0, 3.0], dtype=np.float64),
    'FLOAT32': np.array([1.0, 2.0, 3.0], dtype=np.float32),
    'INT32': np.array([1, 2, 3], dtype=np.int32),
    'INT16': np.array([1, 2, 3], dtype=np.int16),
    'COMPLEX64': np.array([1+2j, 3+4j], dtype=np.complex64),
    'COMPLEX128': np.array([1+2j, 3+4j], dtype=np.complex128),
}

for name, data in data_types.items():
    # Write
    gwframe.write(f'{name}.gwf', data, t0=1234567890.0, sample_rate=100, name=f'CH:{name}')

    # Read back and verify
    result = gwframe.read(f'{name}.gwf', f'CH:{name}')
    match = np.allclose(data, result.array)
    print(f"{name:12s} (dtype={data.dtype}): {'PASS' if match else 'FAIL'}")
```

### Example 11: Complex Data (Frequency-Domain)

Write and read complex-valued data:

```python
import numpy as np
import gwframe

# Generate complex frequency-domain data
n = 1000
freq_data = np.random.randn(n) + 1j * np.random.randn(n)

# Write complex64
gwframe.write(
    'fft_data.gwf',
    freq_data.astype(np.complex64),
    t0=1234567890.0,
    sample_rate=1000,
    name='L1:FFT',
    unit='1/sqrt(Hz)'
)

# Read back
result = gwframe.read('fft_data.gwf', 'L1:FFT')
print(f"Complex data: shape={result.array.shape}, dtype={result.array.dtype}")
print(f"Data integrity: {np.allclose(freq_data, result.array)}")
```

## Compression Examples

### Example 12: Compression Options

Control compression settings for file size optimization:

```python
import numpy as np
import gwframe
import os

data = np.random.randn(16384)

# No compression (fastest, largest file)
gwframe.write(
    'raw.gwf',
    data,
    t0=1234567890.0,
    sample_rate=16384,
    name='TEST:RAW',
    compression=gwframe.Compression.RAW
)

# GZIP compression
gwframe.write(
    'gzip.gwf',
    data,
    t0=1234567890.0,
    sample_rate=16384,
    name='TEST:GZIP',
    compression=gwframe.Compression.GZIP,
    compression_level=9
)

# Zero-suppress with GZIP fallback (recommended default)
gwframe.write(
    'zero_gzip.gwf',
    data,
    t0=1234567890.0,
    sample_rate=16384,
    name='TEST:ZERO_GZIP',
    compression=gwframe.Compression.ZERO_SUPPRESS_OTHERWISE_GZIP
)

# Compare file sizes
sizes = {
    'RAW': os.path.getsize('raw.gwf'),
    'GZIP': os.path.getsize('gzip.gwf'),
    'ZERO_GZIP': os.path.getsize('zero_gzip.gwf')
}
for comp, size in sizes.items():
    print(f"{comp:12s}: {size:8d} bytes ({size/sizes['RAW']:.2f}x)")
```

## Validation Examples

### Example 13: CRC Checksum Validation

Enable checksum validation for data integrity:

```python
import gwframe

# Write frame (checksums are automatically added)
gwframe.write(
    'validated.gwf',
    data,
    t0=1234567890.0,
    sample_rate=16384,
    name='L1:TEST'
)

# Read with checksum validation
try:
    data = gwframe.read('validated.gwf', 'L1:TEST', validate_checksum=True)
    print("Checksum validation passed")
except Exception as e:
    print(f"Checksum validation failed: {e}")
```

## Round-Trip Verification

### Example 14: Complete Data Integrity Test

Verify that data survives a complete write-read cycle:

```python
import numpy as np
import gwframe

# Generate various test signals
t = np.linspace(0, 1, 16384)
signals = {
    'SINE': np.sin(2 * np.pi * 10 * t),
    'COSINE': np.cos(2 * np.pi * 10 * t),
    'CHIRP': np.sin(2 * np.pi * (10 + 50 * t) * t),
    'NOISE': np.random.randn(len(t)),
}

# Write all signals
gwframe.write(
    'roundtrip.gwf',
    channels=signals,
    t0=1234567890.0,
    sample_rate=16384,
    name='TEST'
)

# Verify each channel
print("Round-trip verification:")
all_match = True
for name, original in signals.items():
    result = gwframe.read('roundtrip.gwf', name)
    match = np.allclose(original, result.array)
    all_match = all_match and match
    print(f"  {name:10s}: {'PASS' if match else 'FAIL'}")

print(f"\nOverall: {'ALL PASSED' if all_match else 'SOME FAILED'}")
```

## Performance Tips

- **Use `FrameWriter` for multiple frames**: Much more efficient than calling `write()` repeatedly
- **Choose compression wisely**:
  - `ZERO_SUPPRESS_OTHERWISE_GZIP` (default) is best for most data
  - `RAW` for speed when file size doesn't matter
  - `BEST_COMPRESSION` to minimize file size (slower)
