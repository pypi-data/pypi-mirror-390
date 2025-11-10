from typing import Any,List
from pandas import  DataFrame,to_datetime,isna # type: ignore
from datetime import datetime
from dateutil.relativedelta import relativedelta
# -------------------- Helper Functions --------------------
def to_int(val:Any)->int|None:
    try:
        return int(val)
    except (ValueError, TypeError):
        return None

def to_decimal(val:Any)->float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def to_date(val:Any):
    try:
        return to_datetime(val, errors='coerce', dayfirst=True)
    except Exception:
        return None

def clean_cell(val:Any):
    """Clean single cell value by removing unwanted ".0" or "nan"."""
    if isna(val):
        return ""
    val_str = str(val)
    if val_str.lower() == "nan":
        return ""
    return val_str.replace(".0", "")

def clean_dataframe(df:DataFrame)->DataFrame:
    """Clean entire DataFrame."""
    return df.applymap(clean_cell)

def convert_types(df:DataFrame)->DataFrame:
    """Convert DataFrame columns to appropriate types."""
    int_cols:List = [
        'promotion_code','levelid','redemption_limit_per_transaction',
        'redemption_limit_per_day','maximum_redemption_limit','bucketid',
        'trigger_value','attachmentmode','entity_type','limit_number_of_items_to'
    ]
    decimal_cols:List = ['reward_value']
    date_cols:List = ['active_from','active_to','optimal_date','updated_date']

    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].apply(to_int)
    for col in decimal_cols:
        if col in df.columns:
            df[col] = df[col].apply(to_decimal)
    for col in date_cols:
        if col in df.columns:
            df[col] = df[col].apply(to_date)
    return df
def format_text(value: str) -> str:
    """
    ตัดเว้นวรรค, ตัวแรกตัวใหญ่, ภาษาไทยคงเดิม
    """
    value = value.replace(" ", "")
    if value:
        value = value[0].upper() + value[1:]
    return value
def get_version() -> tuple[str, str, str]:
    """คืนค่า (เดือน, ปี, version_id)"""
    now = datetime.now()+ relativedelta(months=1)
    month = f"{now.month:02d}"
    year = str(now.year)
    version_code = f"{year[-2:]}0{month}"
    return (month, year, version_code)