from pathlib import Path
import uuid
import subprocess

from mediaproc.processors.base import Processor


class ImageProcessor(Processor):
    """
    This processor will:
    - Resize/compress images
    - Add watermark to images (optional)
    """

    def add_watermark(self, input_path: Path, output_path: Path, watermark: str):
        print(f"Adding watermark to {input_path}")

        command = [
            'ffmpeg', '-y',
            '-i', str(input_path),
            '-vf', f"drawtext=text='{watermark}':fontsize=24:fontcolor=white:x=w-tw-10:y=h-th-10",
            str(output_path)
        ]

        subprocess.run(command, check=True)

    def compress_image(self, input_path: Path, output_path: Path):
        print(f"Compressing image {input_path} to output {output_path}")

        command = [
            'ffmpeg', '-y',
            '-i', str(input_path),
            '-q:v', '2',
            str(output_path)
        ]

        subprocess.run(command, check=True)

    def process(self, input_path: Path, output_path: Path, watermark: str | None = None, skip_size_mb: float | None = None) -> Path:
        print(f"Start - Processing image {input_path} to output {output_path}")

        output_name = f"{uuid.uuid4()}"
        image_output_path = output_path / f"{output_name}{input_path.suffix}"

        if watermark:
            self.add_watermark(input_path, image_output_path, watermark)
        else:
            self.compress_image(input_path, image_output_path)

        print(f"End - Processing image {input_path}. Output: {image_output_path}")

        return image_output_path
