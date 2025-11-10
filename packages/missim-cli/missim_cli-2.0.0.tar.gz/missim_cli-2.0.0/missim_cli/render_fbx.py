#!/usr/bin/env python3
"""
Blender script to render a 3D model file to a PNG with transparent background.
Usage: blender --background --python render_fbx.py -- <input.fbx|obj|glb|gltf> [output.png] [rotation]
If output.png is not specified, it will be saved next to the input file with .png extension.
Rotation is in 90-degree increments (0, 1, 2, 3) to rotate camera around the model.
"""

import bpy
import sys
import os
import math


def setup_transparent_rendering():
    """Configure render settings for transparent background."""
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.image_settings.color_mode = "RGBA"
    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 1024
    bpy.context.scene.render.resolution_percentage = 100


def clear_scene():
    """Remove all default objects from the scene."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_model(filepath):
    """Import FBX, OBJ, or GLB file into the scene.

    Args:
        filepath: Path to the model file
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=filepath)
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=filepath)
    elif ext == ".glb" or ext == ".gltf":
        bpy.ops.import_scene.gltf(filepath=filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def setup_camera_and_lighting(rotation_steps=0):
    """Add camera and lighting to the scene.

    Args:
        rotation_steps: Number of 90-degree rotations to apply to camera (0-3)
    """
    # Calculate camera rotation based on rotation steps
    # Base rotation has bow pointing SE
    base_rotation = -0.785  # -45 degrees
    rotation_offset = rotation_steps * (math.pi / 2)  # 90 degrees per step
    camera_z_rotation = base_rotation + rotation_offset

    print(
        f"DEBUG: Camera Z rotation: {camera_z_rotation} radians (base: {base_rotation}, offset: {rotation_offset})"
    )

    # Add camera
    bpy.ops.object.camera_add(location=(7, -7, 5))
    camera = bpy.context.object
    camera.rotation_euler = (1.1, 0, camera_z_rotation)
    bpy.context.scene.camera = camera

    # Add sun light
    bpy.ops.object.light_add(type="SUN", location=(5, 5, 5))
    light = bpy.context.object
    light.data.energy = 2.0


def frame_all_objects():
    """Frame all objects in the camera view."""
    # Select all mesh objects
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.select_set(True)

    # Frame selected objects in camera view
    if bpy.context.selected_objects:
        bpy.ops.view3d.camera_to_view_selected()


def render_to_file(output_path):
    """Render the scene to a PNG file."""
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)


def main():
    # Get command line arguments after '--'
    argv = sys.argv
    if "--" not in argv:
        print(
            "Usage: blender --background --python render_fbx.py -- <input.fbx> [output.png] [rotation]"
        )
        sys.exit(1)

    args = argv[argv.index("--") + 1 :]

    if len(args) < 1:
        print("Error: Please provide input model file")
        print(
            "Usage: blender --background --python render_fbx.py -- <input.fbx> [output.png] [rotation]"
        )
        sys.exit(1)

    input_fbx = args[0]

    # If output not specified, save next to input file with .png extension
    if len(args) >= 2 and not args[1].isdigit():
        output_png = args[1]
        rotation_steps = int(args[2]) if len(args) >= 3 else 0
    else:
        # Remove file extension and add .png
        base_name = os.path.splitext(input_fbx)[0]
        output_png = base_name + ".png"
        rotation_steps = int(args[1]) if len(args) >= 2 else 0

    # Validate rotation
    if rotation_steps < 0 or rotation_steps > 3:
        print(f"Warning: Rotation should be 0-3, got {rotation_steps}. Using modulo 4.")
        rotation_steps = rotation_steps % 4

    # Validate input file
    if not os.path.exists(input_fbx):
        print(f"Error: Input file not found: {input_fbx}")
        sys.exit(1)

    # Ensure output directory exists
    output_dir = os.path.dirname(output_png)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Rendering {input_fbx} to {output_png} (rotation: {rotation_steps * 90}°)...")

    # Execute rendering pipeline
    clear_scene()
    setup_transparent_rendering()
    import_model(input_fbx)
    setup_camera_and_lighting(rotation_steps)
    frame_all_objects()
    render_to_file(output_png)

    print(f"Rendering complete: {output_png}")


if __name__ == "__main__":
    main()
