from datetime import datetime
from pathlib import Path
import threading

class LogManager:
    def __init__(self, log_folder: str = "logs"):
        self.log_folder = Path(log_folder)
        self.log_folder.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.logs = []

    def _append(self, level, msg):
        ts = datetime.now().isoformat()
        entry = f"[{ts}] {level.upper()}: {msg}"
        with self.lock:
            self.logs.append(entry)
        print(entry)

    def log_info(self, msg):
        self._append("info", msg)

    def log_error(self, msg):
        self._append("error", msg)

    def save_to_file(self, version="nover", running="norun"):
        fname = self.log_folder / f"log_{version}_{running}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(self.logs))
        return str(fname)
