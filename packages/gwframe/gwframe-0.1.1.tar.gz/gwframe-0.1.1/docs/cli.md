# CLI Tools

`gwframe` provides a comprehensive command-line interface for manipulating GWF
files without writing Python code. All commands support both single files and
batch processing of directories.

## Common Options

All commands support these common patterns:

- **File or directory input**: Pass individual files or directories
- **Batch processing**: Use glob patterns like `data/*.gwf`
- **Recursive processing**: Use `-r/--recursive` to process subdirectories
- **In-place editing**: Use `-i/--in-place` to modify files directly
- **Output control**: Specify output directory with `-o/--output-dir`

!!! tip
    Use `gwframe COMMAND --help` to see detailed help for any command.

## Commands

### `rename` - Rename Channels

Rename channels within frame files while preserving all other data.

**Usage:**
```bash
gwframe rename INPUT... -m "OLD=>NEW" [-o OUTPUT] [-i] [-r]
```

**Options:**

- `-m, --map TEXT` - Channel mapping in format `OLD=>NEW` (required, can specify multiple)
- `-o, --output-dir PATH` - Output directory or file
- `-i, --in-place` - Modify files in place
- `-r, --recursive` - Recurse into subdirectories

**Examples:**

Rename a single channel in one file:
```bash
gwframe rename input.gwf -o output.gwf -m "L1:OLD_CHAN=>L1:NEW_CHAN"
```

Rename multiple channels:
```bash
gwframe rename input.gwf -o output/ \
    -m "L1:CHAN1=>L1:NEW1" \
    -m "L1:CHAN2=>L1:NEW2"
```

Process entire directory:
```bash
gwframe rename data/ -o output/ -m "L1:GDS-CALIB_STRAIN=>L1:STRAIN"
```

In-place rename (**modifies originals**):
```bash
gwframe rename data/*.gwf --in-place -m "L1:OLD=>L1:NEW"
```

---

### `combine` - Combine Channels

Merge channels from multiple sources covering the same time period. Useful for
combining data from different acquisition systems or adding calibrated channels
to raw data files.

**Usage:**
```bash
gwframe combine SOURCE1 SOURCE2 [SOURCE3...] -o OUTPUT [--keep CHAN] [--drop CHAN]
```

**Options:**

- `-o, --output-dir PATH` - Output directory (required)
- `-k, --keep TEXT` - Only include these channels (can specify multiple)
- `-d, --drop TEXT` - Exclude these channels (can specify multiple)

**Examples:**

Combine two files:
```bash
gwframe combine raw_data.gwf calibrated.gwf -o output/
```

Combine directories (matches frame files by time):
```bash
gwframe combine raw_dir/ calibrated_dir/ -o combined/
```

Combine with channel filtering (keep only specific channels):
```bash
gwframe combine dir1/ dir2/ dir3/ -o output/ \
    --keep L1:STRAIN \
    --keep L1:LSC-DARM_IN1_DQ
```

Combine and drop unwanted channels:
```bash
gwframe combine source1/ source2/ -o output/ \
    --drop L1:TEMPORARY_CHANNEL
```

!!! warning
    All sources must cover the same time ranges. Mismatched time ranges will cause an error.

---

### `drop` - Remove Channels

Remove specified channels from frame files, reducing file size and removing unnecessary data.

**Usage:**
```bash
gwframe drop INPUT... -c CHANNEL [-o OUTPUT] [-i] [-r]
```

**Options:**

- `-c, --channel TEXT` - Channel(s) to drop (required, can specify multiple)
- `-o, --output-dir PATH` - Output directory or file
- `-i, --in-place` - Modify files in place
- `-r, --recursive` - Recurse into subdirectories

**Examples:**

Drop single channel:
```bash
gwframe drop input.gwf -o output.gwf -c L1:UNWANTED_CHANNEL
```

Drop multiple channels:
```bash
gwframe drop input.gwf -o output.gwf \
    -c L1:CHAN1 \
    -c L1:CHAN2 \
    -c L1:CHAN3
```

Process directory and drop channels:
```bash
gwframe drop data/ -o cleaned/ -c L1:TEMPORARY_DATA
```

In-place removal (**modifies originals**):
```bash
gwframe drop data/*.gwf --in-place -c L1:DEBUG_CHANNEL
```

---

### `resize` - Change Frame Duration

Split or combine frames to achieve a target duration. Used to convert
between different frame lengths (e.g., 64s → 4s).

**Usage:**
```bash
gwframe resize INPUT... -d DURATION [-o OUTPUT] [-i] [-r]
```

**Options:**

- `-d, --duration FLOAT` - Target frame duration in seconds (required)
- `-o, --output-dir PATH` - Output directory or file
- `-i, --in-place` - Modify files in place
- `-r, --recursive` - Recurse into subdirectories

**Examples:**

Split 64-second frames into 4-second frames:
```bash
gwframe resize input.gwf -o output/ -d 4.0
```

Combine 1-second frames into 16-second frames:
```bash
gwframe resize data/ -o output/ -d 16.0 --recursive
```

Convert entire directory:
```bash
gwframe resize original_data/ -o resized_data/ -d 8.0
```

!!! note
    - The total duration of input data must be evenly divisible by the target duration
    - All channels in the frame will be resized together
    - Frame metadata (GPS time, run number, etc.) is preserved

---

### `impute` - Replace Values

Replace specific values (like NaN, -999, or sentinel values) with a fill value.

**Usage:**
```bash
gwframe impute INPUT... [-r VALUE] [-f VALUE] [-c CHANNEL] [-o OUTPUT] [-i]
```

**Options:**

- `-r, --replace-value FLOAT` - Value to replace (default: NaN)
- `-f, --fill-value FLOAT` - Replacement value (default: 0.0)
- `-c, --channel TEXT` - Specific channel(s) to impute (if omitted, processes all channels)
- `-o, --output-dir PATH` - Output directory or file
- `-i, --in-place` - Modify files in place
- `--recursive` - Recurse into subdirectories

**Examples:**

Replace NaN with zeros (default behavior):
```bash
gwframe impute input.gwf -o output.gwf
```

Replace specific sentinel value:
```bash
gwframe impute input.gwf -o output.gwf \
    --replace-value -999.0 \
    --fill-value 0.0
```

Impute only specific channels:
```bash
gwframe impute data.gwf -o clean.gwf \
    --fill-value 0.0 \
    --channel L1:STRAIN \
    --channel L1:LSC-DARM
```

Process directory and replace -inf values:
```bash
gwframe impute data/ -o cleaned/ \
    --replace-value -inf \
    --fill-value 0.0
```

!!! warning
    The fill value is cast to the dtype of each channel, so precision may be lost for integer channels.

---

### `replace` - Update Channel Data

Replace channel data in base files with updated versions from other files.

**Usage:**
```bash
gwframe replace BASE... --update UPDATE -o OUTPUT [-c CHANNEL] [-r]
```

**Options:**

- `-u, --update PATH` - Source of updated channel data (required)
- `-o, --output-dir PATH` - Output directory (required)
- `-c, --channel TEXT` - Specific channel(s) to replace (if omitted, replaces all matching channels)
- `-r, --recursive` - Recurse into subdirectories

**Examples:**

Replace all matching channels from update file:
```bash
gwframe replace base.gwf --update updated.gwf -o output/
```

Replace only specific channel:
```bash
gwframe replace base.gwf --update calibrated.gwf -o output/ -c L1:STRAIN
```

Replace data in entire directory (matches by filename/time):
```bash
gwframe replace base_dir/ --update update_dir/ -o output/ --recursive
```

Replace multiple specific channels:
```bash
gwframe replace data.gwf --update new_data.gwf -o output/ \
    -c L1:STRAIN \
    -c L1:LSC-DARM_IN1_DQ
```

!!! tip "Use Cases"
    - **Data fixes**: Replace corrupted segments with corrected data
    - **Reprocessing**: Update specific channels while keeping others unchanged

---

### `recompress` - Change Compression

Rewrite frame files with different compression settings.

**Usage:**
```bash
gwframe recompress INPUT... [-c TYPE] [-l LEVEL] [-o OUTPUT] [-i] [-r]
```

**Options:**

- `-c, --compression TEXT` - Compression type (default: ZERO_SUPPRESS_OTHERWISE_GZIP)
  - `RAW` - No compression (fastest, largest)
  - `GZIP` - Standard gzip compression
  - `DIFF_GZIP` - Differentiate then gzip (good for slowly-varying data)
  - `ZERO_SUPPRESS_OTHERWISE_GZIP` - Zero-suppression with gzip fallback (recommended)
- `-l, --level INT` - Compression level 0-9 (default: 6, higher = more compression)
- `-o, --output-dir PATH` - Output directory or file
- `-i, --in-place` - Modify files in place
- `-r, --recursive` - Recurse into subdirectories

**Examples:**

Maximum compression for archival:
```bash
gwframe recompress input.gwf -o archive.gwf -c GZIP -l 9
```

Re-compress entire directory with optimal settings:
```bash
gwframe recompress data/ -o compressed/ \
    -c ZERO_SUPPRESS_OTHERWISE_GZIP \
    -l 6 \
    --recursive
```

## Error Handling

Common errors and solutions:

### "Channel not found"
```
Error: Channel 'L1:MISSING' not found in frame
```
**Solution**: Use `gwframe` Python API to list available channels:
```python
import gwframe
channels = gwframe.get_channels("file.gwf")
print(channels)
```

### "Time ranges don't match"
```
Error: Source time ranges do not match
```
**Solution**: Use `combine` only with files covering identical time spans. Check with:
```python
import gwframe
for file in ["file1.gwf", "file2.gwf"]:
    info = gwframe.read(file, channel_list=True)
    print(f"{file}: {info}")
```

### "Duration not evenly divisible"
```
Error: Total duration 100.0s not evenly divisible by target 64.0s
```
**Solution**: Choose a target duration that evenly divides the input duration,
or pre-process to trim data.
