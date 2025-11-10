from .config_manager import ConfigManager
from .database_manager import DatabaseManager
from .file_manager import FileManager
from .excel_processor import ExcelProcessor
from .backup_manager import BackupManager
from .report_manager import ReportManager
from .log_manager import LogManager
from .utils import get_version
from pandas import DataFrame
from concurrent.futures import ProcessPoolExecutor, as_completed,ThreadPoolExecutor
from icecream import ic

from tqdm import tqdm
class FlowController:
    def __init__(self,max_workers:int=4):
        self.config:ConfigManager = ConfigManager()
        self.log = LogManager()
        self.db = DatabaseManager(self.config, self.log)
        self.file_manager = FileManager(self.config, self.log)
        self.excel_processor = ExcelProcessor(max_workers=6, use_polars=False, log=self.log)
        self.backup_manager = BackupManager(self.config, self.log)
        self.report_manager = ReportManager(self.log)
        self.running_no = None
        self.moth,self.year,self.version= get_version()
        self.max_workers = max_workers
    def run(self):
        self.log.log_info("Starting PromotionFlow...")
        self.config.init_default_config()
        try:
            self.file_manager.unzip_files()
        except Exception as e:
            self.log.log_error(f"Unzip step error: {e}")
        excel_files = self.file_manager.scan_import_folder()
        if not excel_files:
            self.log.log_info("No Excel files found in import path. Exiting.")
            return
        total_inserted = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.excel_processor._read_single_excels, f): f for f in excel_files}
            # progress bar สำหรับจำนวนไฟล์
            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing Excel Files"):
                file_path = futures[future]

                try:
                    dfs = future.result()
                    
                    for df in dfs:
                        inserted = self.db.insert_dataframe(df, "FlowReport.dbo.promotion_data")
                        total_inserted += inserted
                        tqdm.write(f"{file_path}: Inserted {inserted} rows")
                except Exception as e:
                    if self.log:
                        self.log.log_error(f"Error processing {file_path}: {e}")


        # dataframes:list[DataFrame] = self.excel_processor.read_excel_files(excel_files)            
        # for df in dataframes:
        #     self.log.log_info(f"DataFrame loaded with {df} rows and columns: {df.columns.tolist()}")
        #     try:
        #         self.db.insert_dataframe(df, table_name="FlowReport.dbo.promotion_data")
        #     except Exception as e:
        #         self.log.log_error(f"Insert error: {e}")
        
        # version = self.config.get_config("data.", "version") or "00000"
        # running = self.config.get_config("data.", "running No.") or "01"
        # backup_folder = self.backup_manager.create_backup_folder(version, running)
        # self.backup_manager.move_processed_files(excel_files, backup_folder)

        self.report_manager.generate_summary()

        self.log.log_info("PromotionFlow Completed Successfully.")
