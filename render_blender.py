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
    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)
    scene.render.filepath = os.path.join(args.output_dir, args.prefix)
    scene.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
