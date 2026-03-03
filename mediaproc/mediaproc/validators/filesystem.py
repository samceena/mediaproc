import os
from pathlib import Path


class FilesystemValidator:
    def __init__(self, input_folder_path: Path, output_folder_path: Path, skip_size_mb: float | None = None):
        self.input_path = input_folder_path
        self.output_path = output_folder_path
        self.skip_size_mb = skip_size_mb

    SUPPORTED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv'}

    def scan_supported_files(self) -> tuple[list[Path], list[str]]:
        """Scan folder and return supported files. Only call after access checks pass."""
        files = []
        unsupported_files = []
        extensions_found = set()
        unsupported_extensions_found = set()
        errors = []

        for item in self.input_path.iterdir():
            if item.is_file():
                ext = item.suffix.lower().strip()
                if ext:
                    if ext in self.SUPPORTED_VIDEO_EXTENSIONS:
                        files.append(item)
                        extensions_found.add(ext)
                    else:
                        unsupported_extensions_found.add(ext)
                        unsupported_files.append(item)

        if not files:
            errors.append("No supported media files found in input folder")
            return files, errors

        print(f"Found {len(files)} files with extensions: {extensions_found}")

        if unsupported_extensions_found:
            print(f"Skipping unsupported files {unsupported_files} with extensions: {unsupported_extensions_found}")

        return files, errors

    def check_read_access(self) -> tuple[bool, str | None]:
        if not self.input_path.exists():
            return False, f"Input path does not exist: {self.input_path}"
        if not self.input_path.is_dir():
            return False, f"Input path is not a directory: {self.input_path}"
        if not os.access(self.input_path, os.R_OK):
            return False, f"No read permission: {self.input_path}"
        return True, None

    def check_write_access(self) -> tuple[bool, str | None]:
        # Create output dir if it doesn't exist
        if not self.output_path.exists():
            try:
                self.output_path.mkdir(parents=True)
            except PermissionError:
                return False, f"Cannot create output directory: {self.output_path}"
        if not self.output_path.is_dir():
            return False, f"Output path is not a directory: {self.output_path}"
        if not os.access(self.output_path, os.W_OK):
            return False, f"No write permission: {self.output_path}"
        return True, None

    def run_checks_and_return_files_to_process(self) -> tuple[bool, list[str], list[Path]]:
        """Run all checks and return (success, errors, files)."""
        errors = []
        files = []

        ok, err = self.check_read_access()
        if not ok:
            errors.append(err)
            return False, errors, []

        ok, err = self.check_write_access()
        if not ok:
            errors.append(err)
            return False, errors, []

        files, scan_errors = self.scan_supported_files()
        if scan_errors:
            errors.extend(scan_errors)
            return False, errors, []

        return True, errors, files
