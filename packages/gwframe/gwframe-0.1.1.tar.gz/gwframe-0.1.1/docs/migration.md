# Migration Guide from SWIG Bindings

This guide helps you migrate from the SWIG-based `LDAStools.frameCPP` bindings to gwframe.

## Key Differences

gwframe provides an alternative interface to frameCPP with:

- **High level API**
- **Multi-frame support**: Simplified writing of multiple frames per file
- **Type hints**: Full type annotations for IDE support
- **Automatic type handling**: Data types inferred from NumPy arrays
- **Pre-built wheels**: No local compilation required

## Quick Comparison

### Reading Data

=== "SWIG"

    ```python
    import LDAStools.frameCPP as fc

    # Open file
    ifo_file = fc.IFrameFStream("data.gwf")

    # Get TOC
    toc = ifo_file.GetTOC()

    # Read channel
    fr_data = ifo_file.ReadFrProcData(0, "L1:STRAIN")
    vect = fr_data.GetDataVector(0)
    array = vect.GetDataArray()

    # Get metadata manually
    dt = vect.GetDim(0).dx
    n_samples = len(array)
    duration = dt * n_samples
    ```

=== "gwframe"

    ```python
    import gwframe

    # Read channel
    data = gwframe.read("data.gwf", "L1:STRAIN")

    # Metadata included in TimeSeries object
    array = data.array
    dt = data.dt
    duration = data.duration
    sample_rate = data.sample_rate
    ```

### Writing Single Frame

=== "SWIG"

    ```python
    import LDAStools.frameCPP as fc
    import numpy as np

    # Create frame
    gps_time = fc.GPSTime(1234567890, 0)
    frame = fc.FrameH(gps_time, "L1", 1, 1.0)

    # Create FrVect
    dim = fc.Dimension(len(data), 1.0/16384, "s", 0.0)
    vect = fc.FrVect("L1:TEST", fc.FrVect.FR_VECT_8R, 1, dim, "strain")
    vect.GetDataArray()[:] = data

    # Create FrProcData
    fr_data = fc.FrProcData("L1:TEST", "", 1, 0, 0.0, 1.0, 0.0, 0.0, 8192.0, 0.0)
    fr_data.AppendData(vect)
    frame.AppendFrProcData(fr_data)

    # Write frame
    stream = fc.OFrameFStream("output.gwf")
    frame.Write(stream)
    ```

=== "gwframe"

    ```python
    import gwframe
    import numpy as np

    # Write data
    gwframe.write(
        "output.gwf",
        data,
        t0=1234567890.0,
        sample_rate=16384,
        name="L1:TEST",
        unit="strain"
    )
    ```

### Writing Multiple Frames

=== "SWIG"

    ```python
    import LDAStools.frameCPP as fc

    # Create stream
    stream = fc.OFrameFStream("output.gwf")

    # Create and write each frame
    for i in range(100):
        gps_time = fc.GPSTime(start_time + i, 0)
        frame = fc.FrameH(gps_time, "L1", 1, 1.0)

        # ... create FrVect, FrProcData ...

        frame.Write(stream, 6, 6)
    ```

=== "gwframe"

    ```python
    import gwframe

    # Use FrameWriter context manager
    with gwframe.FrameWriter("output.gwf") as writer:
        for i in range(100):
            writer.write(
                data[i],
                t0=start_time + i,
                sample_rate=16384,
                name="L1:TEST"
            )
    ```

## API Translation Table

### Data Types

| SWIG | gwframe |
|------|---------|
| `fc.FrVect.FR_VECT_8R` | Inferred from `np.float64` |
| `fc.FrVect.FR_VECT_4R` | Inferred from `np.float32` |
| `fc.FrVect.FR_VECT_4S` | Inferred from `np.int32` |
| `fc.FrVect.FR_VECT_2S` | Inferred from `np.int16` |
| Compression constant 6 | `gwframe.Compression.ZERO_SUPPRESS_OTHERWISE_GZIP` |
| Compression constant 257 | `gwframe.Compression.GZIP` |

### Reading Operations

| SWIG | gwframe |
|------|---------|
| `IFrameFStream(filename)` | `read(filename, channel)` |
| `ReadFrProcData(idx, name)` | `read(file, name, frame_index=idx)` |
| `GetDataVector(0).GetDataArray()` | `read(...).array` |
| `GetTOC()` | `get_info(filename)` |
| `toc.GetProc()` | `get_channels(filename)['proc']` |

### Writing Operations

| SWIG | gwframe |
|------|---------|
| `FrameH(gps_time, name, run, dt)` | `Frame(t0, duration, name, run)` |
| `AppendFrProcData(fr_data)` | `frame.add_channel(name, data, sample_rate)` |
| `OFrameFStream(filename)` | `FrameWriter(filename)` |
| `frame.Write(stream, comp, level)` | `writer.write_frame(frame)` |

### Metadata

| SWIG | gwframe |
|------|---------|
| `vect.GetDim(0).dx` | `data.dt` |
| `1.0 / vect.GetDim(0).dx` | `data.sample_rate` |
| `vect.GetName()` | `data.name` |
| `vect.GetUnitY()` | `data.unit` |
| `frame.GetGTime()` | `data.t0` |

## Common Patterns

### Pattern 1: Reading from Multiple Frames

=== "SWIG"

    ```python
    import LDAStools.frameCPP as fc

    stream = fc.IFrameFStream("multi.gwf")
    n_frames = stream.GetNumberOfFrames()

    all_data = []
    for i in range(n_frames):
        fr_data = stream.ReadFrProcData(i, "L1:STRAIN")
        vect = fr_data.GetDataVector(0)
        all_data.append(vect.GetDataArray())

    combined = np.concatenate(all_data)
    ```

=== "gwframe"

    ```python
    import gwframe

    # Automatic stitching with time-based slicing
    data = gwframe.read(
        "multi.gwf",
        "L1:STRAIN",
        start=start_time,
        end=end_time
    )
    # data.array contains stitched frames
    ```

### Pattern 2: Checking Available Channels

=== "SWIG"

    ```python
    import LDAStools.frameCPP as fc

    stream = fc.IFrameFStream("data.gwf")
    try:
        toc = stream.GetTOC()
        proc_channels = list(toc.GetProc())
        adc_channels = list(toc.GetAdc())
    except RuntimeError:
        # TOC not available
        proc_channels = []
        adc_channels = []
    ```

=== "gwframe"

    ```python
    import gwframe

    # Handles TOC unavailability automatically
    channels = gwframe.get_channels("data.gwf")
    proc_channels = channels['proc']
    adc_channels = channels['adc']
    ```

### Pattern 3: Adding History/Metadata

=== "SWIG"

    ```python
    import LDAStools.frameCPP as fc

    history = fc.FrHistory("CREATOR", int(t0), "my_pipeline")
    frame.AppendFrHistory(history)
    ```

=== "gwframe"

    ```python
    import gwframe

    frame = gwframe.Frame(t0=t0, duration=1.0, name="L1")
    frame.add_history("CREATOR", "my_pipeline")
    ```

### Pattern 4: Different Data Types

=== "SWIG"

    ```python
    import LDAStools.frameCPP as fc

    # Must specify FrVect type explicitly
    if data.dtype == np.float64:
        vect_type = fc.FrVect.FR_VECT_8R
    elif data.dtype == np.float32:
        vect_type = fc.FrVect.FR_VECT_4R
    elif data.dtype == np.int32:
        vect_type = fc.FrVect.FR_VECT_4S
    # ... etc

    vect = fc.FrVect(name, vect_type, 1, dim, unit)
    ```

=== "gwframe"

    ```python
    import gwframe

    # Automatic dtype detection from NumPy array
    frame.add_channel(name, data, sample_rate=16384, unit=unit)
    ```

## Parameter Differences

### Time Parameters

| SWIG | gwframe | Conversion |
|------|---------|------------|
| `GPSTime(sec, nsec)` | `t0` (float) | `t0 = sec + nsec * 1e-9` |
| `dt` (sample spacing) | `sample_rate` or `dt` | Both available; `sample_rate = 1/dt` |

### Method vs Property Access

| SWIG | gwframe |
|------|---------|
| `vect.GetDataArray()` | `data.array` |
| `vect.GetName()` | `data.name` |
| `vect.GetUnitY()` | `data.unit` |

## Migration Checklist

When migrating from SWIG to gwframe:

- [ ] Replace `import LDAStools.frameCPP` with `import gwframe`
- [ ] Replace `IFrameFStream.ReadFrProcData()` with `gwframe.read()`
- [ ] Replace manual FrVect/FrProcData creation with `gwframe.write()` or `Frame.add_channel()`
- [ ] Use `FrameWriter` context manager for multi-frame files
- [ ] Replace `GPSTime(sec, nsec)` with float GPS time
- [ ] Replace `.Get*()` method calls with property access (e.g., `.array`, `.name`)
- [ ] Remove manual type specifications - inferred from NumPy dtype
- [ ] Consider using time-based slicing instead of manual frame loops

## Important Notes

### GPS Time Handling

SWIG uses `GPSTime` objects with separate seconds and nanoseconds:

```python
# SWIG
gps_time = fc.GPSTime(1234567890, 500000000)  # sec, nsec

# gwframe
t0 = 1234567890.5  # Float representation
```

### Frame Number Auto-increment

In SWIG, frame numbers must be managed manually. gwframe's `FrameWriter` auto-increments:

```python
# SWIG - manual tracking needed
for i in range(100):
    frame = fc.FrameH(gps_time, "L1", 1, 1.0)  # frame number always 1

# gwframe - automatic
with gwframe.FrameWriter("file.gwf") as writer:
    for i in range(100):
        writer.write(...)  # Frame numbers auto-increment: 0, 1, 2, ...
```

### Data Type Specification

SWIG requires explicit FrVect type codes. gwframe infers from NumPy dtype:

```python
# SWIG
vect = fc.FrVect(name, fc.FrVect.FR_VECT_8R, ...)  # Explicit type

# gwframe
frame.add_channel(name, data, ...)  # Type inferred from data.dtype
```

## See Also

- [Quick Start Guide](quickstart.md) - Learn gwframe basics
- [Examples](examples.md) - Comprehensive examples
- [API Reference](reference/) - Complete API documentation
