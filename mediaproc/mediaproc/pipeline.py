from pathlib import Path
from mediaproc.processors.base import Processor


class Pipeline:
    def __init__(self, processors: list[Processor]):
        self.processors = processors

    def run(self, files: list[Path], output_folder_path: Path, watermark: str | None = None, skip_size_mb: float | None = None) -> list:
        """Process files with registered processors."""
        results = []

        for file in files:
            for processor in self.processors:
                result = processor.process(file, output_folder_path, watermark, skip_size_mb)
                results.append(result)

        return results
