from typing import Optional
import os
from .merge_file import merge_large_dataset
from .Excel_Time import Promotion_Time_Zone_Management
from .Format_Product import MetadataHandler
from .Format_excel import format_and_save_excel
from pathlib import Path
from icecream import ic
ROOT_PATH = ".Promotion"
class CreatePromotionFile:
    def __init__(
        self,
        import_file_path: Optional[str] = "import",
        export_file_path: Optional[str] = "export",
        backup_file_path: Optional[str] = "backup",
        data_file_path: Optional[str] = "./Temp/Propuct",
        database_path: Optional[str] = "database.db",
        version: Optional[str] = "2024",
        load: Optional[bool] = True,
        sub_sheet: Optional[bool] = True,
        ip: Optional[str]='117.113.122.109',
        USER: Optional[str]='sa',
        PASSWORD: Optional[str]='Admin2000'
    ):
        """
        Initialize the CreatePromotionFile class.

        Parameters:
            import_file_path (Optional[str]): Path for imported files. Default is './import'.
            export_file_path (Optional[str]): Path for exported files. Default is './export'.
            backup_file_path (Optional[str]): Path for backup files. Default is './backup'.
            data_file_path (Optional[str]): Path for data files. Default is './data'.
            database_path (Optional[str]): Path for the database. Default is './promotion_database.db'.
            version (Optional[str]): Version identifier. Default is 'v1.0'.
        """
        self.root = Path(os.path.join("C:/Users", os.getlogin(), ROOT_PATH))
        self.import_file_path = self._ensure_folder(import_file_path)
        self.export_file_path = self._ensure_folder(self.root / export_file_path)
        self.backup_file_path = self._ensure_folder(self.root / backup_file_path)
        self.database_path = self.root / database_path
        self.version = version
        self.sub_sheet = sub_sheet
        handler = MetadataHandler(db_path=self.database_path,ip=ip,user = USER,password =PASSWORD)
        if load is True :
            handler.process_files()
            handler.process_Load_LP()
            handler.close()
    def _set_version(self,version):
        self.version = version
        self._reloadData()
    def _reloadData(self):
        self.import_file_path = self._ensure_folder(self.import_file_path)
        self.export_file_path = self._ensure_folder(self.export_file_path)
        self.backup_file_path = self._ensure_folder(self.backup_file_path)
        self.version_path = self.create_backup_folder(self.backup_file_path,self.version)
    @staticmethod
    def _ensure_folder(path: str) -> str:
        """
        Ensure the folder exists. If not, create it.

        Parameters:
            path (str): Folder path to check or create.

        Returns:
            str: The verified folder path.
        """
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    @staticmethod
    def create_backup_folder(base_path, versions):
        """
        Create a backup folder with versioning, e.g., 2024, 2024_01 if the folder exists.
        
        Parameters:
            base_path (str): The base directory where the backup folder will be created.
            versions (str): The base name of the version folder (e.g., '2024').
        
        Returns:
            str: The path to the created backup folder.
        """
        # Initialize the folder name

        # Check if the folder already exists, if it does, create a versioned folder
        version = 1
        folder_name = f"{versions}_{str(version).zfill(2)}"
        while os.path.exists(os.path.join(base_path, folder_name)):
            version += 1
            folder_name = f"{versions}_{str(version).zfill(2)}"
        # Create the backup folder
        full_path = os.path.join(base_path, folder_name)
        os.makedirs(full_path)
        return {"full_path":full_path,"folder_name":folder_name}
    def info(self):
        """
        Display the configuration information of the promotion file paths and version.
        """
        return {
            "Import File Path": self.import_file_path,
            "Export File Path": self.export_file_path,
            "Backup File Path": self.backup_file_path,
            "Data File Path": self.data_file_path,
            "Database Path": self.database_path,
            "Version": self.version_path["folder_name"],
        }
    def info_merge_large(self):
        """
        Display the configuration information of the expot File file paths and version.
        """
        return {
            "import file path": self.import_file_path,
            "Backup File Path": self.version_path["full_path"],
            "Database Path": self.database_path,
            "Version": self.version_path["folder_name"],
        }
    def info_export(self):
        """
        Display the configuration information of the expot File file paths and version.
        """
        return {
            "Export File Path": self.export_file_path,
            "Database Path": self.database_path,
            "Version": self.version_path["folder_name"],
            "save_to_file":True
        }
    def startui(self,list_ui):
        self._reloadData()
        merge_large_dataset(self.info_merge_large(),list_ui)

        # Promotion_Time_Zone_Management(self.info_merge_large())
        format_and_save_excel(self.info_export(),self.sub_sheet)
    def start(self):
        if len(os.listdir(self.import_file_path)) == 0:
                ic("No files to process in the import directory.")

        else :
            merge_large_dataset(self.info_merge_large())

            # Promotion_Time_Zone_Management(self.info_merge_large())
            format_and_save_excel(self.info_export(),self.sub_sheet)
