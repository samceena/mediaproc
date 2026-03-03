from dataclasses import dataclass
from pathlib import Path
import uuid
import subprocess

from mediaproc.processors.base import Processor


@dataclass
class ThumbnailOptions:
    screenshot_time: str = '00:00:01'
    width: int = 1280
    height: int = 720
    quality: int = 85


class VideoProcessor(Processor):
    """
    This processor will:
    - Compress a video (skipped if file is smaller than skip_size_mb)
    - Add watermark to the compressed video (optional)
    - Generate thumbnail from video (always)
    - Add watermark to the thumbnail (optional)
    """

    def should_skip_compression(self, input_path: Path, skip_size_mb: float | None) -> bool:
        """Check if compression should be skipped based on file size."""
        if skip_size_mb is None:
            return False

        file_size_mb = input_path.stat().st_size / (1024 * 1024)

        if file_size_mb < skip_size_mb:
            print(f"SKIP: {input_path.name} ({file_size_mb:.1f}MB) - smaller than {skip_size_mb}MB, skipping compression")
            return True

        print(f"COMPRESS: {input_path.name} ({file_size_mb:.1f}MB) - larger than {skip_size_mb}MB, will compress")
        return False

    def compress_video(self, input_path: Path, output_path: Path, watermark: str | None = None):
        print(f"Compressing video {input_path} to output {output_path}")

        watermark_filter = [
            '-vf', f"drawtext=text='{watermark}':fontsize=90:fontcolor=white@0.3:x=(w-tw)/2:y=(h-th)/2"
        ] if watermark else []

        command = [
            'ffmpeg', '-y',
            '-i', str(input_path),
            *watermark_filter,
            '-c:v', 'libx264',
            '-crf', '28',
            '-preset', 'medium',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            str(output_path)
        ]

        subprocess.run(command, check=True)

    def generate_thumbnail(self, input_path: Path, output_path: Path, watermark: str | None = None, thumbnail_options: ThumbnailOptions = None):
        if thumbnail_options is None:
            thumbnail_options = ThumbnailOptions()

        print(f"Generating thumbnail {input_path} to output {output_path}")

        watermark_filter = [
            '-vf', f"drawtext=text='{watermark}':fontsize=24:fontcolor=white:x=w-tw-30:y=h-th-30"
        ] if watermark else []

        command = [
            'ffmpeg', '-y',
            '-i', str(input_path),
            '-ss', thumbnail_options.screenshot_time,
            '-vframes', '1',
            '-q:v', '2',
            '-update', '1',
            *watermark_filter,
            str(output_path)
        ]

        subprocess.run(command, check=True)

    def process(self, input_path: Path, output_path: Path, watermark: str | None = None, skip_size_mb: float | None = None) -> Path:
        print(f"Start - Processing file {input_path} to output {output_path}")

        output_name = f"{uuid.uuid4()}"
        video_output_path = output_path / f"{output_name}.mp4"
        image_output_path = output_path / f"{output_name}.jpg"

        self.generate_thumbnail(input_path, image_output_path, watermark)

        if self.should_skip_compression(input_path, skip_size_mb):
            print(f"""
          End - Processing file {input_path}.
          Video: SKIPPED (file too small)
          Image: {image_output_path}
          """)
            return image_output_path

        self.compress_video(input_path, video_output_path, watermark)

        print(f"""
          End - Processing file {input_path}.
          Video: {video_output_path}
          Image: {image_output_path}
          """)

        return video_output_path
