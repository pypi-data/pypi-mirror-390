import pandas as pd
import numpy as np
from icecream import ic
import os
import re
from typing import Optional, Tuple, List, Any
import logging
from datetime import datetime, date
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
import platform
import requests
import shutil
import subprocess
from matplotlib import font_manager
import ctypes

class DataCleaner:
    """
    Enterprise-grade Data Cleaner
    --------------------------------------------------------
    Features:
      - clean_dataframe() : ล้างค่าผิดรูป เช่น ".0", "nan"
      - clean_series()    : ล้างเฉพาะคอลัมน์เดียว
      - clean_numeric_columns() : แปลงตัวเลขในคอลัมน์ให้อยู่ในรูป numeric
      - validate_data_types()   : ตรวจสอบและแปลงชนิดข้อมูลตาม expected schema
    """

    def __init__(self, enable_log=True):
        self.enable_log = enable_log

    def _log(self, message, level="INFO"):
        if self.enable_log:
            ic(f"[{level}] {message}")


    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """ล้างข้อมูล DataFrame ทั่วไป เช่น nan, .0, ช่องว่าง"""
        self._log("Start cleaning DataFrame")

        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")

        df_clean = df.copy()
        df_clean = df_clean.astype(str).replace({
            "nan": "",
            "NaN": "",
            "None": "",
        })

        df_clean = df_clean.applymap(lambda x: x[:-2] if x.endswith(".0") else x)
        df_clean = df_clean.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        self._log("Data cleaning complete")
        return df_clean

 
    def clean_series(self, series: pd.Series) -> pd.Series:
        """ล้างข้อมูลใน Series เดียว"""
        self._log(f"Cleaning Series: {series.name}")

        series_clean = (
            series.astype(str)
            .replace({"nan": "", "NaN": "", "None": ""})
            .map(lambda x: x[:-2] if x.endswith(".0") else x)
            .map(lambda x: x.strip())
        )

        self._log(f"Series {series.name} cleaned")
        return series_clean


    def clean_numeric_columns(self, df: pd.DataFrame, numeric_cols: list) -> pd.DataFrame:
        """
        แปลงคอลัมน์ตัวเลขให้ถูกต้อง เช่น "1,000" -> 1000, " " -> 0
        ถ้าไม่สามารถแปลงได้ จะเป็น NaN
        """
        self._log("Cleaning numeric columns")

        df_numeric = df.copy()
        for col in numeric_cols:
            if col in df_numeric.columns:
                self._log(f"Processing column: {col}")
                df_numeric[col] = (
                    df_numeric[col]
                    .astype(str)
                    .replace({",": "", "nan": "", "NaN": "", "None": ""}, regex=True)
                    .str.strip()
                    .replace("", np.nan)
                )
                df_numeric[col] = pd.to_numeric(df_numeric[col], errors="coerce")

        self._log("Numeric column cleaning complete")
        return df_numeric

    def validate_data_types(self, df: pd.DataFrame, schema: dict) -> pd.DataFrame:
        """
        ตรวจสอบและแปลงชนิดข้อมูลตาม expected schema
        Example schema:
            {
                "version": "str",
                "count": "int",
                "price": "float"
            }
        """
        self._log("Validating and converting data types")

        df_validated = df.copy()

        for col, expected_type in schema.items():
            if col not in df_validated.columns:
                self._log(f"Column {col} not found in DataFrame", level="WARNING")
                continue

            try:
                if expected_type == "int":
                    df_validated[col] = pd.to_numeric(df_validated[col], errors="coerce").fillna(0).astype(int)
                elif expected_type == "float":
                    df_validated[col] = pd.to_numeric(df_validated[col], errors="coerce").astype(float)
                elif expected_type == "str":
                    df_validated[col] = df_validated[col].astype(str).fillna("")
                else:
                    self._log(f"Unknown type '{expected_type}' for column '{col}'", level="WARNING")
            except Exception as e:
                self._log(f"Failed to convert column {col}: {e}", level="ERROR")

        self._log("Data type validation complete")
        return df_validated


class NameFormatter:
    """
    Enterprise-grade Name Formatter
    --------------------------------------------
    ใช้จัดการชื่อไฟล์และชื่อชีต Excel ให้ปลอดภัยและเป็นมาตรฐานองค์กร
    """

    def __init__(self, max_sheet_len: int = 31, enable_log: bool = True):
        self.max_sheet_len = max_sheet_len
        self.enable_log = enable_log

    def _log(self, msg: str, level="INFO"):
        if self.enable_log:
            ic(f"[{level}] {msg}")

    # ------------------------------------------------------------
    # ฟังก์ชันย่อชื่อไฟล์: เอาคำแรก + คำสุดท้าย
    # ------------------------------------------------------------
    def shorten_filename(self, filename: str) -> str:
        """
        ตัดชื่อไฟล์ให้เหลือคำแรกและคำสุดท้าย (ไม่รวมสกุลไฟล์)
        เช่น:
            "สรุปบัญชี คูปอง รอบ ต.ค.68 (7Delivery TMW Prefixแบบใหม่) มูก้า-namm.xlsx"
            -> "สรุปบัญชีมูก้า-namm"
        """
        if not filename:
            return ""

        # แยกชื่อและสกุล
        name, _ = os.path.splitext(filename)

        # ลบช่องว่างซ้ำและ strip ขอบ
        name = re.sub(r"\s+", " ", name.strip())

        # แยกคำด้วย space
        parts = name.split(" ")

        if not parts:
            return name  # ไม่มีคำ

        short_name = parts[0] + parts[-1] if len(parts) >= 2 else parts[0]

        # ตัดความยาวเกินไป (ถ้ามี)
        if len(short_name) > 50:
            short_name = short_name[:50]

        self._log(f"Shortened filename: {short_name}")
        return short_name

    # ------------------------------------------------------------
    # ฟังก์ชันล้างชื่อ Sheet
    # ------------------------------------------------------------
    def sanitize_sheet_name(self, name: str) -> str:
        """
        ทำให้ชื่อ sheet ปลอดภัย:
        - ลบอักขระที่ Excel ไม่อนุญาต
        - ตัดชื่อไม่เกิน 31 ตัวอักษร
        """
        if not isinstance(name, str):
            name = str(name)

        invalid_chars = ['\\', '/', '*', '?', ':', '[', ']', ')', '(', ' ']
        for ch in invalid_chars:
            name = name.replace(ch, '')

        # ลบอักขระที่มองไม่เห็น เช่น \n หรือ \t
        name = re.sub(r'[\n\r\t]', '', name)

        # Trim length
        sanitized = name[:self.max_sheet_len]

        self._log(f"Sanitized sheet name: {sanitized}")
        return sanitized

    # ------------------------------------------------------------
    # Utility รวม — ทำชื่อให้พร้อมใช้กับ Excel
    # ------------------------------------------------------------
    def format_excel_name(self, filename: str, sheet_name: str) -> str:
        """
        รวมฟังก์ชันทั้ง 2:
        - ตัดชื่อไฟล์ให้สั้น
        - ทำชื่อ sheet ให้ปลอดภัย
        """
        short_file = self.shorten_filename(filename)
        clean_sheet = self.sanitize_sheet_name(sheet_name)
        formatted_name = f"{short_file}_{clean_sheet}"
        self._log(f"Formatted Excel name: {formatted_name}")
        return formatted_name


class DataCleaner:
    """
    A robust data cleaning and validation utility class for organization-level use.
    """

    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean DataFrame by removing '.0', 'nan', and converting invalid numbers to empty strings.
        """
        def _clean_cell(x: Any):
            if pd.isna(x):
                return ""
            x = str(x)
            x = x.replace("nan", "").replace(".0", "")
            return x.strip()
        
        return df.applymap(_clean_cell)

    @staticmethod
    def clean_numeric_columns(df: pd.DataFrame, numeric_columns: List[str]) -> pd.DataFrame:
        """
        Convert specified columns to numeric (int/float) safely.
        """
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df

    @staticmethod
    def validate_data_types(df: pd.DataFrame, schema: dict) -> pd.DataFrame:
        """
        Validate and convert DataFrame columns based on expected data types.
        Example schema:
            {
                "promotion_code": str,
                "reward_value": float,
                "redemption_limit_per_day": int
            }
        """
        for col, dtype in schema.items():
            if col not in df.columns:
                logging.warning(f"Column '{col}' not found in DataFrame.")
                continue

            try:
                if dtype == int:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                elif dtype == float:
                    df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)
                elif dtype == str:
                    df[col] = df[col].astype(str).fillna("")
                elif dtype == date:
                    df[col] = df[col].apply(DataCleaner.parse_date_safe)
            except Exception as e:
                logging.error(f"Error converting column '{col}' to {dtype}: {e}")

        return df

    # ----------------------------
    # DATE UTILITIES
    # ----------------------------
    @staticmethod
    def parse_date_safe(input_data: Any) -> Optional[date]:
        """
        Safely parse various input formats into a `datetime.date` object.
        """
        if input_data in (None, "", "nan"):
            return None

        if isinstance(input_data, (int, float)):
            try:
                return datetime.fromtimestamp(float(input_data)).date()
            except Exception:
                return None

        if isinstance(input_data, str):
            for fmt in config.DATE_FORMATS: # type: ignore
                try:
                    return datetime.strptime(input_data.strip(), fmt).date()
                except ValueError:
                    continue
            # Normalize `/` → `-`
            try:
                normalized = input_data.replace("/", "-")
                return datetime.strptime(normalized, "%Y-%m-%d").date()
            except Exception:
                return None
        return None

    @staticmethod
    def convert_to_yyyymmdd(date_str: str) -> Optional[str]:
        """
        Convert DD/MM/YYYY → YYYY-MM-DD
        """
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except Exception:
            return None

    @staticmethod
    def is_in_range(check_date: date, start_date: date, end_date: date) -> bool:
        """
        Check if a date is within a given range.
        """
        if not all(isinstance(d, date) for d in [check_date, start_date, end_date]):
            return False
        return start_date <= check_date <= end_date

    # ----------------------------
    # DATAFRAME OPERATIONS
    # ----------------------------
    @staticmethod
    def sort_data_by_columns(df: pd.DataFrame, sort_columns: list, ascending_order: list) -> pd.DataFrame:
        """
        Sort the DataFrame by given columns.
        """
        return df.sort_values(sort_columns, ascending=ascending_order)

    @staticmethod
    def process_unique_date_ranges(df: pd.DataFrame) -> Tuple[List[List[date]], List[List[date]]]:
        """
        Remove duplicates and return (valid_date_ranges, unique_date_ranges)
        """
        df = df.drop_duplicates(subset=Config.TIME_COLUMNS) # type: ignore

        valid_date_ranges = [
            [
                DataCleaner.parse_date_safe(str(row[0])),
                DataCleaner.parse_date_safe(str(row[1]))
            ]
            for row in df[Config.TIME_COLUMNS].to_numpy() # type: ignore
            if pd.notna(row[0]) and pd.notna(row[1])
        ]

        date_df = pd.DataFrame(valid_date_ranges, columns=Config.TIME_COLUMNS) # pyright: ignore[reportUndefinedVariable]
        date_df = date_df.drop_duplicates()

        return valid_date_ranges, date_df.values.tolist()



def check_and_install_fonts(fonts: dict, local_folder: str = "fonts"):
    """
    ตรวจสอบและติดตั้งฟอนต์หลายตัวพร้อมกัน
    Args:
        fonts (dict): dict ของชื่อฟอนต์และ URL เช่น {"Sarabun": "https://.../Sarabun-Regular.ttf"}
        local_folder (str): โฟลเดอร์เก็บฟอนต์ชั่วคราว
    """
    os.makedirs(local_folder, exist_ok=True)

    system_fonts = [os.path.basename(f).lower() for f in font_manager.findSystemFonts()]
    os_name = platform.system().lower()
    installed_any = False

    for font_name, font_url in fonts.items():
        print(f"\nตรวจสอบฟอนต์: {font_name}")

        # ถ้ามีอยู่แล้วให้ข้าม
        if any(font_name.lower() in f for f in system_fonts):
            print(f"ฟอนต์ '{font_name}' มีอยู่แล้วในระบบ")
            continue

        # ดาวน์โหลดไฟล์
        font_path = os.path.join(local_folder, f"{font_name}.ttf")
        if not os.path.exists(font_path):
            print(f"กำลังดาวน์โหลด {font_name} ...")
            response = requests.get(font_url, timeout=20)
            if response.status_code == 200:
                with open(font_path, "wb") as f:
                    f.write(response.content)
                print(f"ดาวน์โหลดสำเร็จ: {font_name}")
            else:
                print(f"ดาวน์โหลดไม่สำเร็จ: {response.status_code}")
                continue

        # ติดตั้งเข้าระบบจริง
        try:
            if "windows" in os_name:
                install_font_windows(font_path)
            elif "linux" in os_name:
                install_font_linux(font_path)
            elif "darwin" in os_name:  # macOS
                install_font_macos(font_path)
            installed_any = True
            print(f"ติดตั้งฟอนต์ '{font_name}' สำเร็จ")
        except Exception as e:
            print(f"ติดตั้งฟอนต์ '{font_name}' ล้มเหลว: {e}")

    if installed_any:
        print("\nกำลังรีโหลด cache ฟอนต์ ...")


def install_font_windows(font_path):
    """ติดตั้งฟอนต์ลง Windows"""
    font_dir = r"C:\Windows\Fonts"
    dest_path = os.path.join(font_dir, os.path.basename(font_path))
    shutil.copy(font_path, dest_path)
    ctypes.windll.gdi32.AddFontResourceW(dest_path)
    # แจ้งระบบให้รู้ว่ามีฟอนต์ใหม่
    ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001D, 0, 0, 0, 1000, None)


def install_font_linux(font_path):
    """ติดตั้งฟอนต์ใน Linux"""
    home = os.path.expanduser("~/.local/share/fonts")
    os.makedirs(home, exist_ok=True)
    shutil.copy(font_path, home)
    subprocess.run(["fc-cache", "-f", "-v"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def install_font_macos(font_path):
    """ติดตั้งฟอนต์ใน macOS"""
    home = os.path.expanduser("~/Library/Fonts")
    os.makedirs(home, exist_ok=True)
    shutil.copy(font_path, home)


font_list = {
        "Anuphan": "https://github.com/google/fonts/raw/main/ofl/anuphan/Anuphan-Regular.ttf",
        "Bar-Code 39": "https://fonts2u.com/download/bar-code-39.font"
    }

    


def get_version() -> str:
    now = datetime.now()+ relativedelta(months=1)
    month = f"{now.month:02d}"
    year = str(now.year)
    version_code = f"{year[-2:]}0{month}"
    return version_code