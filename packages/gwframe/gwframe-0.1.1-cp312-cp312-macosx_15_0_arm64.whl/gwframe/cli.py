# Copyright (c) 2025, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/patrick.godwin/gwframe/-/raw/main/LICENSE

"""CLI module for gwframe."""

from __future__ import annotations

import shutil
import sys
import tempfile

try:
    import typer
    from rich.console import Console
except ImportError:
    print(
        "CLI dependencies not installed. Install with: pip install gwframe[cli]",
        file=sys.stderr,
    )
    sys.exit(1)

from pathlib import Path

from gwframe import operations
from gwframe.types import Compression

# Initialize Typer app and Rich console
app = typer.Typer(
    name="gwframe",
    help="CLI tools for manipulating gravitational wave frame (GWF) files",
    add_completion=False,
)
console = Console()


def expand_paths(
    paths: list[Path],
    recursive: bool = False,
) -> list[Path]:
    """
    Expand paths to list of files, handling both files and directories.

    Directories are searched for *.gwf files.

    Parameters
    ----------
    paths : list[Path]
        List of file or directory paths
    recursive : bool, optional
        If True, recurse into subdirectories (default: False)

    Returns
    -------
    files : list[Path]
        Expanded list of file paths
    """
    files = []
    for path in paths:
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            if recursive:
                files.extend(sorted(path.rglob("*.gwf")))
            else:
                files.extend(sorted(path.glob("*.gwf")))
        else:
            console.print(f"[yellow]Warning: Skipping invalid path: {path}[/yellow]")
    return files


def validate_output_options(output: Path | None, in_place: bool) -> None:
    """Validate that output options are correctly specified."""
    if in_place and output is not None:
        console.print(
            "[red]Error: --in-place and --output-dir are mutually exclusive[/red]"
        )
        raise typer.Exit(1)

    if not in_place and output is None:
        console.print(
            "[red]Error: Either --in-place or --output-dir must be specified[/red]"
        )
        raise typer.Exit(1)


def call_operation(
    operation_func,
    input_files: list[Path],
    output_dir: Path | None,
    in_place: bool,
    **operation_kwargs,
) -> list[str]:
    """
    Call an operation function, handling single-file output case.

    Parameters
    ----------
    operation_func : callable
        Operation function from operations module
    input_files : list[Path]
        Input files to process
    output_dir : Path or None
        Output directory or file path
    in_place : bool
        Whether to modify in place
    **operation_kwargs
        Additional keyword arguments for operation_func

    Returns
    -------
    output_files : list[str]
        List of output file paths
    """
    # Handle single-file output case
    if not in_place and output_dir is not None and output_dir.suffix == ".gwf":
        if len(input_files) != 1:
            console.print(
                "[red]Error: Single file output requires single file input[/red]"
            )
            raise typer.Exit(1)

        # Use temporary directory for operation to avoid filename collisions
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)

            output_files = operation_func(
                [str(f) for f in input_files],
                str(temp_dir),
                **operation_kwargs,
            )

            # Move to final location
            temp_output = Path(output_files[0])
            final_output = output_dir
            final_output.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(temp_output), str(final_output))

            return [str(final_output)]

    # Standard operation (directory output or in-place)
    return operation_func(
        [str(f) for f in input_files],
        str(output_dir) if output_dir else None,
        in_place=in_place,
        **operation_kwargs,
    )


@app.command()
def rename(
    input_paths: list[Path] = typer.Argument(
        ...,
        help="Input GWF file(s) or directory/directories to process",
        exists=True,
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory or file for processed files",
    ),
    channel_map: list[str] = typer.Option(
        ...,
        "--map",
        "-m",
        help="Channel mapping in format OLD=>NEW (can be specified multiple times)",
    ),
    in_place: bool = typer.Option(
        False,
        "--in-place",
        "-i",
        help="Modify files in place instead of creating new ones",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Recurse into subdirectories when processing directories",
    ),
):
    """
    Rename channels in frame files.

    Accepts files or directories.

    Examples:
        gwframe rename input.gwf -o output.gwf -m "L1:OLD_CHAN=>L1:NEW_CHAN"
        gwframe rename input.gwf -o output/ -m "L1:OLD_CHAN=>L1:NEW_CHAN"
        gwframe rename input.gwf --in-place -m "L1:OLD_CHAN=>L1:NEW_CHAN"
        gwframe rename data/ -o output/ -m "L1:OLD_CHAN=>L1:NEW_CHAN"
        gwframe rename data/*.gwf -o output/ -m "L1:CHAN1=>L1:NEW1" -m "L1:CHAN2=>L1:NEW2"
    """  # noqa: E501
    # Expand paths to files
    input_files = expand_paths(input_paths, recursive=recursive)

    if not input_files:
        console.print("[red]Error: No files found matching criteria[/red]")
        raise typer.Exit(1)

    # Parse channel mappings
    mapping = {}
    for item in channel_map:
        if "=>" not in item:
            console.print(
                f"[red]Error: Invalid mapping format '{item}'. Expected OLD=>NEW[/red]"
            )
            raise typer.Exit(1)
        old, new = item.split("=>", 1)
        mapping[old.strip()] = new.strip()

    # Validate output options
    validate_output_options(output_dir, in_place)

    console.print(f"[cyan]Renaming channels in {len(input_files)} file(s)...[/cyan]")

    try:
        output_files = call_operation(
            operations.rename_channels,
            input_files,
            output_dir,
            in_place,
            channel_map=mapping,
        )

        if in_place:
            console.print(
                f"[green]Modified {len(output_files)} file(s) in place[/green]"
            )
        else:
            console.print(
                f"[green]Wrote {len(output_files)} file(s) to {output_dir}[/green]"
            )
    except (ValueError, OSError) as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def combine(
    input_sources: list[Path] = typer.Argument(
        ...,
        help="N source files or N source directories to combine (N >= 2)",
        exists=True,
    ),
    output_dir: Path = typer.Option(
        ...,
        "--output-dir",
        "-o",
        help="Output directory for combined files",
    ),
    keep: list[str] | None = typer.Option(
        None,
        "--keep",
        "-k",
        help="Only include these channels (can be specified multiple times)",
    ),
    drop: list[str] | None = typer.Option(
        None,
        "--drop",
        "-d",
        help="Exclude these channels (can be specified multiple times)",
    ),
):
    """
    Combine channels from N sources covering the same time ranges.

    Takes N files (covering the same time) or N directories (with matching
    frame sets) and merges their channels. All sources must be the same type.

    Examples:
        gwframe combine file1.gwf file2.gwf -o output/
        gwframe combine dir1/ dir2/ -o output/ --keep L1:STRAIN --keep L1:LSC
        gwframe combine dir1/ dir2/ -o output/ --drop L1:UNWANTED
    """
    if len(input_sources) < 2:
        console.print("[red]Error: combine requires at least 2 sources[/red]")
        raise typer.Exit(1)

    # Check that keep and drop are mutually exclusive
    if keep is not None and drop is not None:
        console.print("[red]Error: --keep and --drop are mutually exclusive[/red]")
        raise typer.Exit(1)

    # Check that all sources are the same type
    are_files = [p.is_file() for p in input_sources]
    are_dirs = [p.is_dir() for p in input_sources]

    if not (all(are_files) or all(are_dirs)):
        console.print(
            "[red]Error: All sources must be same type (files or directories)[/red]"
        )
        raise typer.Exit(1)

    source_type = "files" if all(are_files) else "directories"

    # Build status message
    status_msg = f"Combining channels from {len(input_sources)} {source_type}"
    if keep:
        status_msg += f" (keeping {len(keep)} channel(s))"
    elif drop:
        status_msg += f" (dropping {len(drop)} channel(s))"
    console.print(f"[cyan]{status_msg}...[/cyan]")

    try:
        output_files = operations.combine_channels(
            [str(s) for s in input_sources],
            str(output_dir),
            keep_channels=keep,
            drop_channels=drop,
        )
        console.print(
            f"[green]Wrote {len(output_files)} combined file(s) to {output_dir}[/green]"
        )
    except (ValueError, OSError) as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def drop(
    input_paths: list[Path] = typer.Argument(
        ...,
        help="Input GWF file(s) or directory/directories to process",
        exists=True,
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory or file for processed files",
    ),
    channels: list[str] = typer.Option(
        ...,
        "--channel",
        "-c",
        help="Channel(s) to drop (can be specified multiple times)",
    ),
    in_place: bool = typer.Option(
        False,
        "--in-place",
        "-i",
        help="Modify files in place instead of creating new ones",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Recurse into subdirectories when processing directories",
    ),
):
    """
    Remove specified channels from frame files.

    Accepts files or directories.

    Examples:
        gwframe drop input.gwf -o output.gwf -c L1:UNWANTED_CHANNEL
        gwframe drop input.gwf --in-place -c L1:UNWANTED_CHANNEL
        gwframe drop data/ -o output/ -c L1:CHAN1 -c L1:CHAN2
    """
    # Expand paths to files
    input_files = expand_paths(input_paths, recursive=recursive)

    if not input_files:
        console.print("[red]Error: No files found matching criteria[/red]")
        raise typer.Exit(1)

    # Validate output options
    validate_output_options(output_dir, in_place)

    console.print(
        f"[cyan]Dropping {len(channels)} channel(s) in "
        f"{len(input_files)} file(s)...[/cyan]"
    )

    try:
        output_files = call_operation(
            operations.drop_channels,
            input_files,
            output_dir,
            in_place,
            channels_to_drop=channels,
        )
        if in_place:
            console.print(
                f"[green]Modified {len(output_files)} file(s) in place[/green]"
            )
        else:
            console.print(
                f"[green]Wrote {len(output_files)} file(s) to {output_dir}[/green]"
            )
    except (ValueError, OSError) as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def resize(
    input_paths: list[Path] = typer.Argument(
        ...,
        help="Input GWF file(s) or directory/directories to process",
        exists=True,
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory or file for processed files",
    ),
    duration: float = typer.Option(
        ...,
        "--duration",
        "-d",
        help="Target frame duration in seconds",
    ),
    in_place: bool = typer.Option(
        False,
        "--in-place",
        "-i",
        help="Modify files in place instead of creating new ones",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Recurse into subdirectories when processing directories",
    ),
):
    """
    Resize frames to a different duration (e.g., 64s to 4s).

    Accepts files or directories.

    Examples:
        gwframe resize input.gwf -o output.gwf -d 4.0
        gwframe resize input.gwf --in-place -d 4.0
        gwframe resize data/ -o output/ -d 4.0
    """
    # Expand paths to files
    input_files = expand_paths(input_paths, recursive=recursive)

    if not input_files:
        console.print("[red]Error: No files found matching criteria[/red]")
        raise typer.Exit(1)

    # Validate output options
    validate_output_options(output_dir, in_place)

    console.print(f"[cyan]Resizing frames to {duration}s duration...[/cyan]")

    try:
        output_files = call_operation(
            operations.resize_frames,
            input_files,
            output_dir,
            in_place,
            target_duration=duration,
        )
        if in_place:
            console.print(
                f"[green]Modified {len(output_files)} file(s) in place[/green]"
            )
        else:
            console.print(
                f"[green]Wrote {len(output_files)} file(s) to {output_dir}[/green]"
            )
    except (ValueError, OSError) as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def impute(
    input_paths: list[Path] = typer.Argument(
        ...,
        help="Input GWF file(s) or directory/directories to process",
        exists=True,
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory or file for processed files",
    ),
    replace_value: float = typer.Option(
        float("nan"),
        "--replace-value",
        "-r",
        help="Value to replace (default: NaN)",
    ),
    fill_value: float = typer.Option(
        0.0,
        "--fill-value",
        "-f",
        help="Value to use for replacement (will be cast to appropriate dtype)",
    ),
    channels: list[str] | None = typer.Option(
        None,
        "--channel",
        "-c",
        help="Channel(s) to impute (can be specified multiple times)",
    ),
    in_place: bool = typer.Option(
        False,
        "--in-place",
        "-i",
        help="Modify files in place instead of creating new ones",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        help="Recurse into subdirectories when processing directories",
    ),
):
    """
    Replace specific values in frame file channels with a fill value.

    Accepts files or directories.

    Examples:
        gwframe impute input.gwf -o output.gwf
        gwframe impute input.gwf --in-place --fill-value 0.0 --channel L1:STRAIN
        gwframe impute data/ -o output/ --replace-value -999.0 --fill-value 0.0
    """
    # Expand paths to files
    input_files = expand_paths(input_paths, recursive=recursive)

    if not input_files:
        console.print("[red]Error: No files found matching criteria[/red]")
        raise typer.Exit(1)

    # Validate output options
    validate_output_options(output_dir, in_place)

    # Build status message
    replace_str = (
        "NaN" if replace_value != replace_value else str(replace_value)
    )  # NaN != NaN
    status_msg = f"Replacing {replace_str} with {fill_value}"
    if channels:
        status_msg += f" in {len(channels)} channel(s)"
    console.print(f"[cyan]{status_msg}...[/cyan]")

    try:
        output_files = call_operation(
            operations.impute_missing_data,
            input_files,
            output_dir,
            in_place,
            replace_value=replace_value,
            fill_value=fill_value,
            channels=channels,
        )
        if in_place:
            console.print(
                f"[green]Modified {len(output_files)} file(s) in place[/green]"
            )
        else:
            console.print(
                f"[green]Wrote {len(output_files)} file(s) to {output_dir}[/green]"
            )
    except (ValueError, OSError) as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def replace(
    base_paths: list[Path] = typer.Argument(
        ...,
        help="Base GWF file(s) or directory/directories",
        exists=True,
    ),
    update_paths: list[Path] = typer.Option(
        ...,
        "--update",
        "-u",
        help="GWF file(s) or directory/directories containing updated channel data",
        exists=True,
    ),
    output_dir: Path = typer.Option(
        ...,
        "--output-dir",
        "-o",
        help="Output directory for processed files",
    ),
    channels: list[str] | None = typer.Option(
        None,
        "--channel",
        "-c",
        help="Channel(s) to replace (if not specified, replaces all)",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Recurse into subdirectories when processing directories",
    ),
):
    """
    Replace data in channels with updated versions from another frame file.

    Accepts files or directories.

    Examples:
        gwframe replace base.gwf --update updated.gwf -o output/ -c L1:STRAIN
        gwframe replace base_dir/ --update update_dir/ -o output/
        gwframe replace data/*.gwf --update updates/*.gwf -o output/ --recursive
    """
    # Expand paths to files
    base_files = expand_paths(base_paths, recursive=recursive)
    update_files = expand_paths(update_paths, recursive=recursive)

    if not base_files:
        console.print("[red]Error: No base files found matching criteria[/red]")
        raise typer.Exit(1)

    if not update_files:
        console.print("[red]Error: No update files found matching criteria[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Replacing channels in {len(base_files)} file(s)...[/cyan]")

    try:
        output_files = operations.replace_channels(
            [str(f) for f in base_files],
            [str(f) for f in update_files],
            str(output_dir),
            channels,
        )
        console.print(
            f"[green]Wrote {len(output_files)} file(s) to {output_dir}[/green]"
        )
    except (ValueError, OSError) as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def recompress(
    input_paths: list[Path] = typer.Argument(
        ...,
        help="Input GWF file(s) or directory/directories to process",
        exists=True,
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory or file for processed files",
    ),
    compression: str = typer.Option(
        "ZERO_SUPPRESS_OTHERWISE_GZIP",
        "--compression",
        "-c",
        case_sensitive=False,
        help="Compression type (e.g., RAW, GZIP, DIFF_GZIP)",
    ),
    level: int = typer.Option(
        6,
        "--level",
        "-l",
        help="Compression level (0-9)",
        min=0,
        max=9,
    ),
    in_place: bool = typer.Option(
        False,
        "--in-place",
        "-i",
        help="Modify files in place instead of creating new ones",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Recurse into subdirectories when processing directories",
    ),
):
    """
    Rewrite frame files with different compression settings.

    Accepts files or directories.

    Examples:
        gwframe recompress input.gwf -o output.gwf -c GZIP -l 9
        gwframe recompress input.gwf --in-place -c GZIP -l 9
        gwframe recompress data/ -o output/ -c RAW
    """
    # Expand paths to files
    input_files = expand_paths(input_paths, recursive=recursive)

    if not input_files:
        console.print("[red]Error: No files found matching criteria[/red]")
        raise typer.Exit(1)

    # Validate output options
    validate_output_options(output_dir, in_place)

    # Convert compression string to Compression enum
    try:
        compression_enum = Compression[compression.upper()]
    except KeyError:
        console.print(
            f"[red]Error: Invalid compression type '{compression}'. "
            f"Valid options: {', '.join(c.name for c in Compression)}[/red]"
        )
        raise typer.Exit(1) from None

    console.print(
        f"[cyan]Recompressing {len(input_files)} file(s) with "
        f"{compression_enum.name} (level {level})...[/cyan]"
    )

    try:
        output_files = call_operation(
            operations.recompress_frames,
            input_files,
            output_dir,
            in_place,
            compression=compression_enum,
            compression_level=level,
        )
        if in_place:
            console.print(
                f"[green]Modified {len(output_files)} file(s) in place[/green]"
            )
        else:
            console.print(
                f"[green]Wrote {len(output_files)} file(s) to {output_dir}[/green]"
            )
    except (ValueError, OSError) as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
