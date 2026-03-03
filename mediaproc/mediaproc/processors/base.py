from abc import ABC, abstractmethod
from pathlib import Path


class Processor(ABC):
    @abstractmethod
    def process(self, input_path: Path, output_path: Path, watermark: str | None = None, skip_size_mb: float | None = None) -> Path:
        """Process a single file and return output path"""
        pass
