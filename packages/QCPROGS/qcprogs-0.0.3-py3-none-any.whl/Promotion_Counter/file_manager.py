from pathlib import Path
import zipfile
import shutil
from typing import List

class FileManager:
    def __init__(self, config, log):
        self.config = config
        self.log = log
        self.path_import = Path(self.config.get_config("info.", "path_import") or ".").resolve()

    def scan_import_folder(self) -> List[str]:
        if not self.path_import.exists():
            self.path_import.mkdir(parents=True, exist_ok=True)
            return []
        files = []
        for p in self.path_import.rglob("*"):
            if p.suffix.lower() in (".xlsx", ".xls"):
                files.append(str(p))
        return files

    def unzip_files(self):
        zips = list(self.path_import.glob("*.zip"))
        for z in zips:
            try:
                with zipfile.ZipFile(z, 'r') as zf:
                    zf.extractall(self.path_import)
                self.log.log_info(f"Unzipped {z.name}")
                processed = self.path_import / "processed_zips"
                processed.mkdir(exist_ok=True)
                shutil.move(str(z), str(processed / z.name))
            except Exception as e:
                self.log.log_error(f"Failed unzip {z.name}: {e}")
        return zips

    def move_processed_files(self, src_files, backup_folder):
        backup = Path(backup_folder)
        backup.mkdir(parents=True, exist_ok=True)
        for f in src_files:
            try:
                shutil.move(f, str(backup / Path(f).name))
                self.log.log_info(f"Moved {f} -> {backup}")
            except Exception as e:
                self.log.log_error(f"Move failed for {f}: {e}")
