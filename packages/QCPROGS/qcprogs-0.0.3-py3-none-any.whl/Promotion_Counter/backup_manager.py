from pathlib import Path
import shutil

class BackupManager:
    def __init__(self, config, log):
        self.config = config
        self.log = log
        self.path_backup = Path(self.config.get_config("info.", "path_backup") or "./backup")

    def create_backup_folder(self, version, running):
        folder = self.path_backup / str(version) / str(running)
        folder.mkdir(parents=True, exist_ok=True)
        self.log.log_info(f"Created backup folder: {folder}")
        return str(folder)

    def move_processed_files(self, files, backup_folder):
        for f in files:
            try:
                shutil.move(f, Path(backup_folder) / Path(f).name)
                self.log.log_info(f"Moved {f} to {backup_folder}")
            except Exception as e:
                self.log.log_error(f"Backup move failed for {f}: {e}")

    def cleanup_old_versions(self, keep_latest=2):
        self.log.log_info("cleanup_old_versions() not implemented in skeleton")
