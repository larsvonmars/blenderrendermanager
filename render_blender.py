import bpy
import argparse
import os
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Render a blend file using bpy")
    parser.add_argument("--blend-file", required=True, help="Blend file to render")
    parser.add_argument("--output-dir", required=True, help="Directory for rendered images")
    parser.add_argument("--prefix", default="", help="Filename prefix")
    parser.add_argument("--frame-start", type=int, help="Start frame")
    parser.add_argument("--frame-end", type=int, help="End frame")
    parser.add_argument("--resolution-x", type=int, help="Output resolution X")
    parser.add_argument("--resolution-y", type=int, help="Output resolution Y")
    parser.add_argument("--engine", help="Render engine (CYCLES, BLENDER_EEVEE, etc.)")
    parser.add_argument("--samples", type=int, help="Render samples for Cycles/Eevee")
    parser.add_argument("--file-format", help="Image file format e.g. PNG, JPEG")
    parser.add_argument("--color-depth", help="Color depth e.g. 8 or 16")
    parser.add_argument("--fps", type=int, help="Frames per second")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    return args


def main():
    args = parse_args()
    bpy.ops.wm.open_mainfile(filepath=args.blend_file)
    scene = bpy.context.scene
    if args.frame_start is not None:
        scene.frame_start = args.frame_start
    if args.frame_end is not None:
        scene.frame_end = args.frame_end

    if args.resolution_x is not None:
        scene.render.resolution_x = args.resolution_x
    if args.resolution_y is not None:
        scene.render.resolution_y = args.resolution_y
    if args.engine:
        scene.render.engine = args.engine
    if args.fps is not None:
        scene.render.fps = args.fps

    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)
    scene.render.filepath = os.path.join(args.output_dir, args.prefix)

    if args.file_format:
        scene.render.image_settings.file_format = args.file_format
    else:
        scene.render.image_settings.file_format = 'PNG'
    if args.color_depth:
        scene.render.image_settings.color_depth = args.color_depth
    if args.samples is not None:
        if scene.render.engine == 'CYCLES':
            scene.cycles.samples = args.samples
        elif scene.render.engine == 'BLENDER_EEVEE':
            scene.eevee.taa_render_samples = args.samples

    bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
