import sys
from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel
from argparse import ArgumentParser

from mediaproc.processors.video_processor import VideoProcessor
from mediaproc.processors.image_processor import ImageProcessor
from mediaproc.pipeline import Pipeline
from mediaproc.validators.filesystem import FilesystemValidator


class Args(BaseModel):
    version: Optional[str] = None
    mode: Literal['video', 'image', 'both']
    input_folder_path: str
    output_folder_path: str
    watermark: Optional[str] = None
    skip_size: Optional[float] = None


def main():
    app_name = "mediaproc"

    parser = ArgumentParser(
        description="A media processor tool. \nIt can resize or compress a video, add watermark to the video, take screenshots from the video and much more",
        prog=app_name,
        usage='%(prog)s [options]'
    )
    parser.add_argument('--version', '-v', nargs='?', help='Display current version')
    parser.add_argument('--mode', '-m', choices=['video', 'image', 'both'], default='video', required=True, type=str)
    parser.add_argument('--input-folder-path', '-p', help='The absolute path to the folder with the videos or images', required=True, type=str)
    parser.add_argument('--output-folder-path', '-o', help='The absolute path to the folder for storing the results.', required=True, type=str)
    parser.add_argument('--watermark', '-w', help='The watermark to add on the image and video. Leave empty to skip adding watermark')
    parser.add_argument('--skip-size', '-s', type=float, help='Skip files smaller than this size in MB (no need to compress small files). e.g. --skip-size 10 skips files under 10MB')

    args = parser.parse_args()

    validator = FilesystemValidator(
        Path(args.input_folder_path),
        Path(args.output_folder_path),
        args.skip_size
    )
    success, errors, files = validator.run_checks_and_return_files_to_process()

    if not success:
        for err in errors:
            print(f"ERROR: {err}")
        sys.exit(1)

    processors = []
    if args.mode == 'video':
        processors.append(VideoProcessor())
    elif args.mode == 'image':
        processors.append(ImageProcessor())
    elif args.mode == 'both':
        processors.extend([VideoProcessor(), ImageProcessor()])

    pipeline = Pipeline(processors)
    pipeline.run(files, Path(args.output_folder_path), args.watermark, args.skip_size)


if __name__ == "__main__":
    main()
