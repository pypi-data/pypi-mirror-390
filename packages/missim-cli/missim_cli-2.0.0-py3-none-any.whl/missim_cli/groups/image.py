import os
import subprocess
import shutil
from pathlib import Path
from typing import List

import click


def find_model_files(directory: Path, recursive: bool = False) -> List[Path]:
    """Find all FBX, OBJ, GLB, and GLTF files in a directory."""
    extensions = ["*.fbx", "*.FBX", "*.obj", "*.OBJ", "*.glb", "*.GLB", "*.gltf", "*.GLTF"]
    files = []

    if recursive:
        for ext in extensions:
            files.extend(directory.rglob(ext))
    else:
        for ext in extensions:
            files.extend(directory.glob(ext))

    return files


def check_blender_installed() -> bool:
    """Check if Blender is installed and available in PATH."""
    if not shutil.which("blender"):
        click.echo(click.style("Error: Blender is not installed or not in PATH.", fg="red"))
        click.echo(
            click.style(
                "Please install Blender and ensure it's available in your PATH.", fg="yellow"
            )
        )
        click.echo(click.style("Download from: https://www.blender.org/download/", fg="cyan"))
        return False
    return True


def render_model(
    model_path: Path, blender_script: Path, output_path: Path = None, rotation: int = 0
) -> bool:
    """Render a 3D model to PNG using Blender."""
    if not model_path.exists():
        click.echo(click.style(f"Error: Model file not found: {model_path}", fg="red"))
        return False

    # Build the command
    cmd = ["blender", "--background", "--python", str(blender_script), "--", str(model_path)]

    if output_path:
        cmd.append(str(output_path))

    cmd.append(str(rotation))

    try:
        click.echo(f"Rendering {model_path.name}...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Show debug output
        for line in result.stdout.split("\n"):
            if "DEBUG:" in line:
                click.echo(click.style(f"  {line}", fg="yellow"))

        # Extract success message from Blender output
        if "Rendering complete" in result.stdout:
            output_file = output_path if output_path else model_path.with_suffix(".png")

            # Verify the file actually exists
            if output_file and output_file.exists():
                click.echo(click.style(f"✓ Created {output_file}", fg="green"))
                return True
            else:
                click.echo(
                    click.style(
                        f"✗ Failed to render {model_path.name} - output file not created", fg="red"
                    )
                )
                click.echo(f"  Expected: {output_file}")
                # Show last few lines of output for debugging
                click.echo(click.style("  Last output lines:", fg="yellow"))
                for line in result.stdout.split("\n")[-10:]:
                    if line.strip():
                        click.echo(f"    {line}")
                return False
        else:
            click.echo(click.style(f"✗ Failed to render {model_path.name}", fg="red"))
            # Show error details
            if result.stderr:
                for line in result.stderr.split("\n"):
                    if line.strip() and (
                        "Error" in line or "error" in line or "Traceback" in line
                    ):
                        click.echo(click.style(f"  {line}", fg="red"))
            return False

    except subprocess.CalledProcessError as e:
        click.echo(click.style(f"✗ Error rendering {model_path.name}: {e}", fg="red"))
        if e.stderr:
            click.echo(click.style(f"  {e.stderr}", fg="red"))
        return False


@click.command(name="generate-image")
@click.argument(
    "path",
    type=click.Path(exists=True),
    required=True,
)
@click.option(
    "-r",
    "--recursive",
    is_flag=True,
    help="Recursively process all model files in subdirectories",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output PNG file path (single file) or directory path (multiple files)",
)
@click.option(
    "--rotation",
    type=click.IntRange(0, 3),
    default=0,
    help="Rotate camera in 90-degree increments (0=0°, 1=90°, 2=180°, 3=270°)",
)
def generate_image(path: str, recursive: bool, output: str, rotation: int):
    """Generate PNG images from 3D model files (FBX/OBJ/GLB/GLTF) using Blender.

    PATH can be either a single model file or a directory containing model files.

    Examples:
        missim generate-image model.fbx                         # Creates model.png
        missim generate-image model.glb -o out.png              # Creates out.png
        missim generate-image model.fbx --rotation 2            # Rotate 180°
        missim generate-image ./models/                         # Renders all models
        missim generate-image ./models/ -r                      # Recursively renders
        missim generate-image ./models/ -o ./output/            # Saves to output dir
        missim generate-image ./models/ --rotation 1            # All rotated 90°
    """
    # Check if Blender is installed before doing anything
    if not check_blender_installed():
        raise click.Abort()

    path_obj = Path(path).resolve()
    output_path = Path(output).resolve() if output else None

    # Get the blender script path
    script_dir = Path(__file__).parent.parent
    blender_script = script_dir / "render_fbx.py"

    if not blender_script.exists():
        click.echo(
            click.style(
                f"Error: Blender script not found at {blender_script}",
                fg="red",
            )
        )
        raise click.Abort()

    # Handle single file
    if path_obj.is_file():
        if path_obj.suffix.lower() not in [".fbx", ".obj", ".glb", ".gltf"]:
            click.echo(click.style(f"Error: Unsupported file type: {path_obj.suffix}", fg="red"))
            return

        # If output is a directory, append the filename
        final_output_path = output_path
        if output_path:
            if output_path.is_dir() or (not output_path.exists() and output_path.suffix == ""):
                # Output is a directory, create filename
                output_path.mkdir(parents=True, exist_ok=True)
                final_output_path = output_path / (path_obj.stem + ".png")
            # Otherwise, use output_path as-is (it's a file path)

        success = render_model(path_obj, blender_script, final_output_path, rotation)
        if not success:
            raise click.Abort()
        return

    # Handle directory
    if path_obj.is_dir():
        # Check if output is a directory or should be created as one
        output_dir = None
        if output_path:
            # Create output directory if it doesn't exist
            if output_path.exists() and not output_path.is_dir():
                click.echo(
                    click.style(
                        f"Error: Output path exists but is not a directory: {output_path}",
                        fg="red",
                    )
                )
                raise click.Abort()

            output_dir = output_path
            output_dir.mkdir(parents=True, exist_ok=True)
            click.echo(f"Output directory: {output_dir}")

        model_files = find_model_files(path_obj, recursive)

        if not model_files:
            click.echo(
                click.style(
                    f"No model files (FBX/OBJ/GLB/GLTF) found in {path_obj}"
                    + (" (recursive)" if recursive else ""),
                    fg="yellow",
                )
            )
            return

        click.echo(f"Found {len(model_files)} model file(s)")

        successful = 0
        failed = 0

        for model_file in model_files:
            # Determine output path for this file
            if output_dir:
                file_output = output_dir / (model_file.stem + ".png")
            else:
                file_output = None  # Will save next to source file

            if render_model(model_file, blender_script, file_output, rotation):
                successful += 1
            else:
                failed += 1

        # Summary
        click.echo()
        click.echo(click.style(f"Summary: {successful} successful, {failed} failed", fg="cyan"))

        if failed > 0:
            raise click.Abort()
