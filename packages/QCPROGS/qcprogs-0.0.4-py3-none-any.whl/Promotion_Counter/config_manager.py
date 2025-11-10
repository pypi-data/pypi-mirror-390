import sqlite3
from pathlib import Path
from datetime import datetime
import os
from .utils import get_version
PORT = 1143
USER ="sa"
PASSWORD ="Admin2000"
DATABASE ="master"
DRIVER ="ODBC Driver 17 for SQL Server"
ROOT_PATH = ".Promotion"
BACKUP_PATH = "backup"
IMPORT_PATH = "import"
REPORT_PATH = "export"
DB_PATH ="config.db"
TRUE = True
FALSE = False
class ConfigManager:
    def __init__(self, db_path=DB_PATH):
        self.root = Path(os.path.join("C:/Users", os.getlogin(), ROOT_PATH))
        self.root.mkdir(parents=TRUE, exist_ok=TRUE)  
        self.db_path = Path(f'{self.root}/{db_path}')
        Path(os.path.join(str(self.root) , BACKUP_PATH)).parent.mkdir(parents=TRUE, exist_ok=TRUE)
        Path(IMPORT_PATH).mkdir(parents=TRUE, exist_ok=TRUE)

        print(f"Database path: {self.db_path}")
        self.conn = self.create_database()
        if not self.db_path.exists():
            self.init_default_config()




    def create_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS config_table(
            function TEXT,
            keywords TEXT,
            value TEXT,
            create_date TEXT,
            update_date TEXT,
            status TEXT
        )
        """)
        conn.commit()
        return conn

    def init_default_config(self):
        if not self.db_path.exists():
            return
        defaults = [
            ("info", "User", os.getlogin()),
            ("info", "path_root", str(self.root)),
            ("info", "path_backup", str(self.root / "backup")),
            ("info", "path_import", str(self.root / "import")),
            ("info", "path_report", str(self.root / "backup" / "export")),
            ("data", "version", "25011"),
            ("data", "running No.", "01"),
            ("Promotion", "host", "localhost"),
            ("Promotion", "port", "1143"),
            ("Promotion", "database", "master"),
            ("Promotion", "user", "sa"),
            ("Promotion", "password", "Admin2000"),
            ("Promotion", "driver", "ODBC Driver 17 for SQL Server"),
            ("Promotion", "connecter", "true"),
            ("production", "host", "117.113.122.109"),
            ("production", "port", "1143"),
            ("production", "database", "master"),
            ("production", "user", "sa"),
            ("production", "password", "Admin2000"),
            ("production", "driver", "ODBC Driver 17 for SQL Server"),
            ("production", "connecter", "false"),
        ]
        cursor = self.conn.cursor()
        for fn, key, val in defaults:
            cursor.execute("SELECT 1 FROM config_table WHERE function=? AND keywords=?", (fn, key))
            if not cursor.fetchone():
                now = datetime.now().isoformat()
                cursor.execute(
                    "INSERT INTO config_table VALUES (?,?,?,?,?,?)",
                    (fn, key, val, now, now, "active")
                )
        self.conn.commit()

    def get_config(self, function, keywords):
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM config_table WHERE function=? AND keywords=?", (function, keywords))
        row = cursor.fetchone()
        return row[0] if row else None

    def update_config(self, function, keywords, value):
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE config_table SET value=?, update_date=? WHERE function=? AND keywords=?
        """, (value, now, function, keywords))
        self.conn.commit()


if __name__ == "__main__":
    cm = ConfigManager()
    cm.init_default_config()
    cm.update_config("info.", "User", "NewUser")
    print(cm.get_config("info.", "User"))
