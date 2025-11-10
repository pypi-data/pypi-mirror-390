from pathlib import Path
import pandas as pd

class ReportManager:
    def __init__(self, log):
        self.log = log
        self.reports_folder = Path("reports")
        self.reports_folder.mkdir(parents=True, exist_ok=True)

    def generate_summary(self):
        fname = self.reports_folder / "summary.txt"
        with open(fname, "w", encoding="utf-8") as f:
            if hasattr(self.log, "logs"):
                f.write("\n".join(self.log.logs))
        self.log.log_info(f"Generated report: {fname}")
        return str(fname)

    def export_to_excel(self, df: pd.DataFrame, version, running, filename=None):
        if filename is None:
            filename = f"promotion_{version}_{running}.xlsx"
        out = self.reports_folder / filename
        df.to_excel(out, index=False)
        self.log.log_info(f"Exported excel: {out}")
        return str(out)
