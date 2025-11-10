from typing import  TypeVar,List
T = TypeVar('T')

FONT_BARCODE ="Bar-Code 39"
FONT_NOMAL ="Anuphan"
C_GRAY ="808080"
C_WHITE:str ="FFFFFF"
SOLID ="solid"

COLUMN_BARCODE :List[T] =["L", "Q"]

HEARDER_COLOR = C_GRAY
HEARDER_FONT_SIZE =30
HEARDER_FONT_NOMAL =FONT_NOMAL
HEARDER_FONT_BARCODE = None
HEARDER_WIDTH=None
HEARDER_HEIGHT=105
HEARDER_FILL=SOLID

BACKGROUND_COLOR=C_WHITE
BACKGROUND_FONT_SIZE =12
BACKGROUND_FONT_BARCODE =FONT_BARCODE
BACKGROUND_FONT_NOMAL =FONT_NOMAL
BACKGROUND_WIDTH=None
BACKGROUND_HEIGHT=105
BACKGROUND_FILL=SOLID
BACKGROUND_WRAP_TEXT=True,
BACKGROUND_HORIZONTAL="center"
BACKGROUND_VERTICAL="center"

TABEL_LINE_TOP = "thin"
TABEL_LINE_LEFT = "thin"
TABEL_LINE_RIGHT = "thin"
TABEL_LINE_BOTTOM = "thin"
WIDTH_COLUMN=[10,10,6.3,6.3,7.5,5.3,5.3,5.3,11,11,16.5,53,7.5,10,50,15.3,53,8.6,15,15,15,15]
PRINT_WIDTH=1
PRINT_HEIGT=0
PRINT_SCALE=100
PRINT_SIZE_TOP=0.75
PRINT_SIZE_LEFT=0.25
PRINT_SIZE_RIGHT=0.25
PRINT_SIZE_BOTTOM=0.75
PRINT_SIZE_HEADER=0.30
PRINT_SIZE_FOOTER=0.30
PRINT_TEXT_HEARDER_LEFT = ""
PRINT_TEXT_HEARDER_CENTER = "&[Page] of &[Pages]"
PRINT_TEXT_HEARDER_RIGHT = "&[Tab]"

import os
import json
from typing import Dict, Any, Optional
from icecream import ic


class ConfigManager:
    """
    Class สำหรับจัดการ Configuration ของระบบ เช่น
    - Database Connection
    - Debug Mode
    - Paths / Environment Variables
    """

    def __init__(self, config_source: Optional[str]| None = 'Promotion/queries/config.json', env_prefix: str = "APP_"):
        """
        Parameters:
        - config_source: path ของไฟล์ config.json หรือ None เพื่ออ่านจาก environment
        - env_prefix: prefix สำหรับ environment variable เช่น APP_DB_HOST
        """
        self.env_prefix = env_prefix
        self.config_data: Dict[str, Any] = {}

        if config_source and os.path.exists(config_source):
            self.load_from_file(config_source)
        else:
            self.load_from_env()

        ic("ConfigManager initialized")

    # ------------------------------------------------------------
    # 🔹 โหลดจากไฟล์ JSON
    # ------------------------------------------------------------
    def load_from_file(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            self.config_data = json.load(f)
        ic(f"Loaded configuration from file: {path}")

    # ------------------------------------------------------------
    # 🔹 โหลดจาก Environment Variable
    # ------------------------------------------------------------
    def load_from_env(self):
        self.config_data = {
            "sqlserver": {
                "host": os.getenv(f"{self.env_prefix}DB_HOST_SQLSERVER", "localhost"),
                "port": int(os.getenv(f"{self.env_prefix}DB_PORT_SQLSERVER", "1433")),
                "database": os.getenv(f"{self.env_prefix}DB_NAME_SQLSERVER", "PROMOTION"),
                "user": os.getenv(f"{self.env_prefix}DB_USER_SQLSERVER", "sa"),
                "password": os.getenv(f"{self.env_prefix}DB_PASSWORD_SQLSERVER", "1234"),
            },
            "sqlite": {
                "path": os.getenv(f"{self.env_prefix}SQLITE_PATH", "data.db")
            },
            "debug": os.getenv(f"{self.env_prefix}DEBUG", "True").lower() == "true",
        }
        ic("🌱 Loaded configuration from environment")

    # ------------------------------------------------------------
    # 🔹 ดึง config เฉพาะฐานข้อมูล
    # ------------------------------------------------------------
    def get_database_config(self, db_type: str) -> Dict[str, Any]:
        db_type = db_type.lower()
        if db_type not in self.config_data:
            raise KeyError(f"Database config '{db_type}' not found")
        return self.config_data[db_type]

    # ------------------------------------------------------------
    # 🔹 ดึงค่า debug mode
    # ------------------------------------------------------------
    def is_debug(self) -> bool:
        return self.config_data.get("debug", False)

    # ------------------------------------------------------------
    # 🔹 บันทึก config กลับลงไฟล์
    # ------------------------------------------------------------
    def save_to_file(self, path: str = "config.json"):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=4, ensure_ascii=False)
        ic(f"Configuration saved to {path}")


