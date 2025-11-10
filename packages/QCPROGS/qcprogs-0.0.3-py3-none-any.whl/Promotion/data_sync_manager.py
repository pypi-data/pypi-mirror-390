import os
import sqlite3
import pandas as pd
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine, text
import pyodbc
from enum import Enum, auto
from typing import Optional, List, Tuple, Any
from icecream import ic

class DBState(Enum):
    INIT = auto()
    CONNECTED = auto()
    CLOSED = auto()

class DisplayManager:
    """จัดการแสดงผลสถานะและข้อมูลแบบสวยงาม"""
    def __init__(self, enable_debug: bool = True):
        self.enable_debug = enable_debug
        ic.configureOutput(includeContext=True) 

    def log_state_change(self, old_state: DBState, new_state: DBState):
        if self.enable_debug:
            ic(f"State changed: {old_state.name} → {new_state.name}")

    def log_connect(self, db_type: str):
        ic(f"Connected to {db_type}")

    def log_close(self, db_type: str):
        ic(f"Connection closed ({db_type})")

    def log_query(self, query: str, params: Optional[Tuple[Any, ...]] = None):
        if self.enable_debug:
            ic("SQL Query:", query)
            if params:
                ic("Parameters:", params)

    def log_result(self, data: List[Tuple]):
        if self.enable_debug:
            ic(f"Return {len(data)} rows")
            for i, row in enumerate(data[:5], start=1):
                ic(f"Row {i}: {row}")
            if len(data) > 5:
                ic("... (more rows not shown)")

    def log_error(self, msg: str):
        ic(f"Error: {msg}")
SQLLIFT ='sqlite'
SQLSERVER = 'sqlserver'
PATH = "Promotion/queries/"
SQL = ".sql"
def load_query(name: str) -> str:
    with open(PATH+name+SQL, "r", encoding="utf-8") as f:
        return f.read()



class DatabaseConnector:
    def __init__(self, db_type: str, display: DisplayManager, **kwargs):
        self.db_type = db_type.lower()
        self.display = display
        self.config = kwargs
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            if self.db_type == SQLSERVER:
                conn_str = (
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={self.config.get('host')},{self.config.get('port', 1433)};"
                    f"DATABASE={self.config.get('database')};"
                    f"UID={self.config.get('user')};"
                    f"PWD={self.config.get('password')}"
                )
                self.connection = pyodbc.connect(conn_str)
            elif self.db_type == SQLLIFT:
                self.connection = sqlite3.connect(self.config.get("path"))
            else:
                raise ValueError("Unsupported database type")

            self.cursor = self.connection.cursor()
            self.display.log_connect(self.db_type)
        except Exception as e:
            self.display.log_error(str(e))
            raise

    def execute_query(self, query: str, params: Optional[Tuple[Any, ...]] = None):
        self.display.log_query(query, params)
        self.cursor.execute(query, params or ())
        data = self.cursor.fetchall()
        self.display.log_result(data)
        return data

    def execute_non_query(self, query: str, params: Optional[Tuple[Any, ...]] = None):
        self.display.log_query(query, params)
        self.cursor.execute(query, params or ())
        self.connection.commit()
        ic("✅ Non-query executed successfully")

    def close(self):
        if self.connection:
            self.connection.close()
            self.display.log_close(self.db_type)


def connetdatbase(df):
    conn = pyodbc.connect(
        "DRIVER=ODBC Driver 17 for SQL Server;SERVER=localhost,1433;DATABASE=master;UID=sa;PWD=Admin2000"
    )
    cursor = conn.cursor()

    # ==========================
    # UPSERT DATA
    # ==========================
    for _, row in df.iterrows():
        # --- VERSION ---
        version_year = row.get('version', datetime.now().year)
        version_month = row.get('round', datetime.now().month)
        project_name = 'PromotionProject'

        cursor.execute("""
            MERGE PM_VERSION AS target
            USING (SELECT ? AS YEAR, ? AS MONTH) AS src
            ON target.YEAR = src.YEAR AND target.MONTH = src.MONTH
            WHEN NOT MATCHED THEN
                INSERT (PROJECT_NAME,YEAR,MONTH) VALUES (?, ?, ?)
            WHEN MATCHED THEN
                UPDATE SET PROJECT_NAME = ?
            ;
        """, version_year, version_month, project_name, version_year, version_month, project_name)

        cursor.execute("SELECT VERSION_ID FROM PM_VERSION WHERE YEAR=? AND MONTH=?", version_year, version_month)
        version_id = cursor.fetchone()[0]

        # --- WORKSHEET ---
        worksheet_name = row.get('worksheet','DefaultWorksheet')
        cursor.execute("""
            MERGE PM_WORKSHEET AS target
            USING (SELECT ? AS FILE_NAME, ? AS VERSION_ID) AS src
            ON target.FILE_NAME = src.FILE_NAME AND target.VERSION_ID = src.VERSION_ID
            WHEN NOT MATCHED THEN
                INSERT (VERSION_ID, FILE_NAME) VALUES (?, ?)
            WHEN MATCHED THEN
                UPDATE SET FILE_NAME = src.FILE_NAME
            ;
        """, worksheet_name, version_id, version_id, worksheet_name)

        cursor.execute("SELECT WORKSHEET_ID FROM PM_WORKSHEET WHERE FILE_NAME=? AND VERSION_ID=?", worksheet_name, version_id)
        worksheet_id = cursor.fetchone()[0]

        # --- SHEET ---
        sheet_name = row.get('sheet','DefaultSheet')
        cursor.execute("""
            MERGE PM_SHEET AS target
            USING (SELECT ? AS SHEET_NAME, ? AS WORKSHEET_ID) AS src
            ON target.SHEET_NAME = src.SHEET_NAME AND target.WORKSHEET_ID = src.WORKSHEET_ID
            WHEN NOT MATCHED THEN
                INSERT (WORKSHEET_ID, SHEET_NAME) VALUES (?, ?)
            WHEN MATCHED THEN
                UPDATE SET SHEET_NAME = src.SHEET_NAME
            ;
        """, sheet_name, worksheet_id, worksheet_id, sheet_name)

        cursor.execute("SELECT SHEET_ID FROM PM_SHEET WHERE SHEET_NAME=? AND WORKSHEET_ID=?", sheet_name, worksheet_id)
        sheet_id = cursor.fetchone()[0]

        # --- PROMOTION ---
        cursor.execute("""
            MERGE PM_PROMOTION AS target
            USING (SELECT ? AS SHEET_ID, ? AS PROMOTION_CODE) AS src
            ON target.SHEET_ID = src.SHEET_ID AND target.PROMOTION_CODE = src.PROMOTION_CODE
            WHEN NOT MATCHED THEN
                INSERT (SHEET_ID,PROMOTION_CODE,PROMOTION_NAME,PROMOTION_RECEIPT,PROMOTION_STATUS,
                        PROMOTION_TYPE,LEVEL_ID,ACTIVE_FROM,ACTIVE_TO,COUPON,LIMIT_PER_TRANSACTION,
                        LIMIT_PER_DAY,LIMIT_NUMBER_OF_ITEM,MAXIMUM_LIMIT,MEMBER_SEGMENTS,
                        ALL_MEMBER_CARD_REQUIRED,MEMBER_SEGMENTS_TIERS,REWARD_VALUE,REWARD_TYPE,
                        REWARD_MA_ID,REWARD_MA_NAME,CONDITION_NAME,CONDITION_MA_ID,CONDITION_MA_NAME,
                        GROUP_NAME,OPTION_TIME,UPDATED_DATE,EXTERNAL_ID,NOTES)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            WHEN MATCHED THEN
                UPDATE SET PROMOTION_NAME=?, PROMOTION_RECEIPT=?, PROMOTION_STATUS=?, PROMOTION_TYPE=?,
                           LEVEL_ID=?, ACTIVE_FROM=?, ACTIVE_TO=?, COUPON=?, LIMIT_PER_TRANSACTION=?,
                           LIMIT_PER_DAY=?, LIMIT_NUMBER_OF_ITEM=?, MAXIMUM_LIMIT=?, MEMBER_SEGMENTS=?,
                           ALL_MEMBER_CARD_REQUIRED=?, MEMBER_SEGMENTS_TIERS=?, REWARD_VALUE=?, REWARD_TYPE=?,
                           REWARD_MA_ID=?, REWARD_MA_NAME=?, CONDITION_NAME=?, CONDITION_MA_ID=?, CONDITION_MA_NAME=?,
                           GROUP_NAME=?, OPTION_TIME=?, UPDATED_DATE=?, EXTERNAL_ID=?, NOTES=?
            ;
        """,
            sheet_id, row['promotion_code'],
            sheet_id, row['promotion_code'], row['promotion_name'], row['receipt_promotion_name'], row['promotion_status'],
            row['promotion_type'], row['levelid'], row['active_from'], row['active_to'], row['coupon_code39'], 
            row['redemption_limit_per_transaction'], row['redemption_limit_per_day'], row['limit_number_of_items_to'],
            row['maximum_redemption_limit'], row['member_segmentation'], row['all_members_card_required'], 
            row['member_segments_tiers'], row['reward_value'], row['reward_type'], row['reward_ma_id'], row['reward_ma_name'],
            row['condition_name'], row['condition_ma_id'], row['condition_ma_name'], row['group_name'],
            row['optimal_date'], row['updated_date'], row['external_id'], row['notes'],
            # UPDATE values
            row['promotion_name'], row['receipt_promotion_name'], row['promotion_status'], row['promotion_type'],
            row['levelid'], row['active_from'], row['active_to'], row['coupon_code39'], 
            row['redemption_limit_per_transaction'], row['redemption_limit_per_day'], row['limit_number_of_items_to'],
            row['maximum_redemption_limit'], row['member_segmentation'], row['all_members_card_required'], 
            row['member_segments_tiers'], row['reward_value'], row['reward_type'], row['reward_ma_id'], row['reward_ma_name'],
            row['condition_name'], row['condition_ma_id'], row['condition_ma_name'], row['group_name'],
            row['optimal_date'], row['updated_date'], row['external_id'], row['notes']
        )

        cursor.execute("SELECT PROMOTION_ID FROM PM_PROMOTION WHERE SHEET_ID=? AND PROMOTION_CODE=?", sheet_id, row['promotion_code'])
        promotion_id = cursor.fetchone()[0]

        # --- PRODUCT ---
        cursor.execute("""
            MERGE PM_PRODUCT AS target
            USING (SELECT ? AS PROMOTION_ID, ? AS ENTITY_CODE) AS src
            ON target.PROMOTION_ID = src.PROMOTION_ID AND target.ENTITY_CODE = src.ENTITY_CODE
            WHEN NOT MATCHED THEN
                INSERT (PROMOTION_ID,ENTITY_CODE,ENTITY_NAME,ATTACHMENTMODE,ENTITY_TYPE,BUCKET_ID,
                        BARCODE,TRIGGER_TYPE,TRIGGER_VALUE)
                VALUES (?,?,?,?,?,?,?,?,?)
            WHEN MATCHED THEN
                UPDATE SET ENTITY_NAME=?, ATTACHMENTMODE=?, ENTITY_TYPE=?, BUCKET_ID=?, BARCODE=?, TRIGGER_TYPE=?, TRIGGER_VALUE=?
            ;
        """,
            promotion_id, row['entity_code'],
            promotion_id, row['entity_code'], row['entity_name'], row['attachmentmode'], row['entity_type'],
            row['bucketid'], row['barcode'], row['trigger_type'], row['trigger_value'],
            # UPDATE values
            row['entity_name'], row['attachmentmode'], row['entity_type'], row['bucketid'], 
            row['barcode'], row['trigger_type'], row['trigger_value']
        )

    # ==========================
    # COMMIT
    # ==========================
    conn.commit()
    conn.close()
    print("Import/Update Excel → SQL Server เสร็จเรียบร้อย ✅")
class DatabaseManager:
    def __init__(self, connector: DatabaseConnector, display: DisplayManager):
        self.connector = connector
        self.display = display
        self.state = DBState.INIT

    def require_state(self, *allowed_states):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if self.state not in allowed_states:
                    msg = f"Cannot call {func.__name__}() in state {self.state.name}"
                    self.display.log_error(msg)
                    raise RuntimeError(msg)
                return func(*args, **kwargs)
            return wrapper
        return decorator


    @property
    def step1_connect(self):
        @self.require_state(DBState.INIT, DBState.CLOSED)
        def _():
            old = self.state
            self.connector.connect()
            self.state = DBState.CONNECTED
            self.display.log_state_change(old, self.state)
        return _


    @property
    def step2_select_data(self):
        @self.require_state(DBState.CONNECTED)
        def _(table: str, condition: str = "1=1"):
            query = f"SELECT * FROM {table} WHERE {condition}"
            return self.connector.execute_query(query)
        return _


    @property
    def step3_insert_data(self):
        @self.require_state(DBState.CONNECTED)
        def _(table: str, columns: List[str], values: Tuple[Any, ...]):
            cols = ", ".join(columns)
            placeholders = ", ".join(["?" for _ in values])
            query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
            self.connector.execute_non_query(query, values)
        return _


    @property
    def step4_update_data(self):
        @self.require_state(DBState.CONNECTED)
        def _(table: str, set_clause: str, condition: str):
            query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
            self.connector.execute_non_query(query)
        return _


    @property
    def step5_close(self):
        @self.require_state(DBState.CONNECTED)
        def _():
            old = self.state
            self.connector.close()
            self.state = DBState.CLOSED
            self.display.log_state_change(old, self.state)
        return _
