import pyodbc
import pandas as pd
from .config_manager import ConfigManager
class DatabaseManager:
    def __init__(self, config, log):
        self.config:ConfigManager = config
        self.log = log
        self.conn = None
        self.check_connection =True
    @staticmethod
    def check_connection_database(conn_str: str = ""
    ) -> tuple[bool, str]:

        try:
            with pyodbc.connect(conn_str, timeout=5) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True, f"Database connection successful: {conn_str}"
        except Exception as e:
            return False, f"Database connection failed: {str(e)}"

    def connect(self, which="Promotion"):
 
        host = self.config.get_config(which, "host")
        port = self.config.get_config(which, "port")
        database = self.config.get_config(which, "database")
        user = self.config.get_config(which, "user")
        password = self.config.get_config(which, "password")
        driver = "ODBC+Driver+17+for+SQL+Server"
        connecter = self.config.get_config(which, "connecter").lower() == "true"
        
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={host},{port};"
            f"DATABASE={database};"
            f"UID={user};PWD={password}"
        ) 
        cons = False
        if self.check_connection:
            cons ,text = DatabaseManager.check_connection_database(conn_str)
            print(text)
            self.check_connection = False
            self.config.update_config("Promotion","connecter", str(cons))
        if cons or connecter :
            try:
                self.conn = pyodbc.connect(conn_str, timeout=5)
                self.log.log_info("Connected to SQL Server")
            except Exception as e:
                self.log.log_error(f"DB connect error: {e}")
        else:
            self.conn = None
        return self.conn
    def insert_dataframe(self, df: pd.DataFrame, table_name: str):
        if self.conn is None:
            self.connect()
        if self.conn is None:
            raise RuntimeError("No DB connection")
        cursor = self.conn.cursor()
        cols = list(df.columns)
        qmarks = ",".join("?" for _ in cols)
        insert_sql = f"INSERT INTO {table_name} ({','.join(cols)}) VALUES ({qmarks})"
        for _, row in df.iterrows():
            try:
                cursor.execute(insert_sql, tuple(row[col] for col in cols))
            except Exception as e:
                self.log.log_error(f"Insert row error: {e}")
        self.conn.commit()
