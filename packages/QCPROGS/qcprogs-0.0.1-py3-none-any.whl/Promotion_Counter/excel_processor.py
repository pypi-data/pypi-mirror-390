import pandas as pd
from pandas import DataFrame
from typing import List,Any
from pathlib import Path
import re
from concurrent.futures import ProcessPoolExecutor, as_completed,ThreadPoolExecutor
from tqdm import tqdm
import os
from icecream import ic
class ExcelProcessor:
    def __init__(self, max_workers: int = 6, use_polars: bool = False, log=None):
        self.max_workers = max_workers
        self.use_polars = use_polars
        self.log = log
    @staticmethod
    def read_excel_file(file_path: str):
        try:
            df = pd.read_excel(file_path, engine="openpyxl")
            df["WORKSHEET"] = os.path.basename(file_path)  # เก็บชื่อไฟล์ไว้
            return df
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return None
        
    def read_excel_files(self, file_paths):
        all_dfs = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._read_single_excel, fp): fp for fp in file_paths}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Loading Excel Files"):
                fp = futures[future]
                try:
                    dfs: list[DataFrame] = future.result()  # อ่านทุกชีตในไฟล์
                    valid_dfs = [df for df in dfs if 'PROMOTION_CODE' in df.columns]

                    if valid_dfs:
                        all_dfs.extend(valid_dfs)

                    # if self.log:
                    #     self.log.log_info(f"Loaded {fp} ({len(valid_dfs)}/{len(dfs)} valid sheets)")

                except Exception as e:
                    if self.log:
                        self.log.log_error(f"Error loading {fp}: {e}")

        ic(f"Total valid sheets: {len(all_dfs)}")
        return all_dfs
    def read_all_excels(folder_path: str, max_workers: int = 4):
        # ดึงรายชื่อไฟล์ทั้งหมด
        excel_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.endswith((".xlsx", ".xls"))
        ]
        print(f"พบไฟล์ Excel ทั้งหมด {len(excel_files)} ไฟล์ ในโฟลเดอร์ {folder_path}")
        all_dataframes = []
        
        # แสดง progress bar พร้อม parallel อ่าน
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(ExcelProcessor.read_excel_file, file): file for file in excel_files}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Reading Excel Files", ncols=100):
                result:DataFrame = future.result()
                if  result is not None and 'PROMOTION_CODE'in result.columns.tolist():
                    result.dropna(subset=['PROMOTION_CODE'], inplace=True)
                    all_dataframes.append(result)

        # รวมทั้งหมดเป็น DataFrame เดียว
        if all_dataframes:
            return pd.concat(all_dataframes, ignore_index=True)
        return pd.DataFrame()
    def _read_single_excel(self, file_path):
        p = Path(file_path)
        xls = pd.ExcelFile(p, engine="openpyxl")
        dfs = []
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet, dtype=str, na_filter=False)
            df = self.clean_dataframe(df)
            dfs.append(df)
        return dfs

    def _read_single_excels(self, file_path):
        dfs = []
        try:
            xls = pd.ExcelFile(file_path)
            for sheet in xls.sheet_names:
                df = xls.parse(sheet)
                df = self.clean_dataframe(df)
                if 'PROMOTION_CODE' in df.columns:
                    dfs.append(df)
        except Exception as e:
            if self.log:
                self.log.log_error(f"Error reading {file_path}: {e}")
        return dfs

    def clean_dataframe(self, df):
        df = df.copy()
        df.columns = [self._normalize_colname(c) for c in df.columns]
        df = df.replace(["NaN", "None", "Null"], "")
        if df.shape[1] > 0:
            first_col = df.columns[0]
            df = df[df[first_col].notna() & (df[first_col] != "")]
        df = df.fillna("")
        return df

    def _normalize_colname(self, colname):
        colname = str(colname).strip().upper()
        colname = re.sub(r"\s+", "_", colname)
        colname = re.sub(r"[^\w\s]", "", colname)
        return colname
