import pandas as pd
from datetime import datetime
import json
import sqlite3
# with open('Promotion/queries/config.json', 'r',encoding="utf-8", errors="replace") as file:
#     Format_Design = json.load(file)

def parse_date_safe(input_data):
    """
    Safely parses a given input into a date object. The function handles various types of input, including 
    strings, integers, floats, and null values. If parsing fails or the input is invalid, it returns `None`.

    **Function Details**:
    - If the input is `None` or an empty string (`""`), the function returns `None`.
    - If the input is a numeric value (`int` or `float`), it assumes the value is a UNIX timestamp 
      and attempts to convert it to a date.
        - Example: `1698056400` → `2024-10-23`
    - If the input is a string, it checks against a predefined list of date formats to parse the string.
        - Supported Formats:
            - `"YYYY-MM-DD HH:MM:SS"` → Example: `"2024-10-23 14:30:00"`
            - `"YYYY-MM-DD"` → Example: `"2024-10-23"`
            - `"DD/MM/YYYY HH:MM:SS"` → Example: `"23/10/2024 14:30:00"`
            - `"DD/MM/YYYY"` → Example: `"23/10/2024"`
            - `"MM/DD/YYYY"` → Example: `"10/23/2024"` (U.S. format)
            - `"Mon DD, YYYY"` → Example: `"Oct 23, 2024"`
            - `"Month DD, YYYY"` → Example: `"October 23, 2024"`
            - `"DD-Mon-YYYY"` → Example: `"23-Oct-2024"`
            - `"DD-Month-YYYY"` → Example: `"23-October-2024"`
            - `"UNIX timestamp` → Example: ``1698056400`
        - If the input string uses forward slashes (`/`) as separators, the function attempts to normalize 
          it by replacing `/` with `-` and parsing it in `"YYYY-MM-DD"` format.
        - Example: `"2024/10/23"` → `2024-10-23`

    **Input Types Handled**:
    - **`None` or Empty Strings**: Returns `None`.
    - **`int` or `float`**: Interpreted as UNIX timestamps. If invalid, returns `None`.
    - **`str`**: Tries multiple date formats. If all attempts fail, returns `None`.

    **Returns**:
    - A `datetime.date` object if the input is successfully parsed.
    - `None` if the input is invalid or cannot be parsed.

    **Examples**:
    ```python
    parse_date_safe(None)  # Output: None
    parse_date_safe(1698056400)  # Output: datetime.date(2024, 10, 23)
    parse_date_safe("2024-10-23 14:30:00")  # Output: datetime.date(2024, 10, 23)
    parse_date_safe("23/10/2024")  # Output: datetime.date(2024, 10, 23)
    parse_date_safe("Invalid Date String")  # Output: None
    ```
    """
    if input_data is None or input_data == "":
        # If the input is None or an empty string, return None
        return None
    
    # If the input is a numeric type (timestamp or invalid number)
    if isinstance(input_data, (int, float)):
        try:
            # Assume the number is a UNIX timestamp
            return datetime.fromtimestamp(input_data).date()
        except (ValueError, OSError):
            # If the number is not a valid timestamp, return None
            return None

    # If the input is a string
    if isinstance(input_data, str):
        # Define possible date formats
        formats = ["%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d",
                    "%d/%m/%Y %H:%M:%S",
                    "%d/%m/%Y",
                    "%m/%d/%Y",
                    "%b %d, %Y",
                    "%B %d, %Y",
                    "%d-%b-%Y",
                    "%d-%B-%Y"]
        for fmt in formats:
            try:
                # Try to parse the input using the current format
                return datetime.strptime(input_data, fmt).date()
            except ValueError:
                continue
        
        # Attempt to handle unusual formats like 'YYYY/MM/DD'
        try:
            normalized_input = input_data.replace("/", "-")  # Normalize separators
            return datetime.strptime(normalized_input, "%Y-%m-%d").date()
        except ValueError:
            pass

    # If the input type is unknown or cannot be parsed, return None
    return None
def convert_to_yyyymmdd(date_str):
    try:
        # แปลงวันที่จากรูปแบบ DD/MM/YYYY เป็น YYYY-MM-DD
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return None
# ฟังก์ชันตรวจสอบว่า date อยู่ในช่วง start_date ถึง end_date หรือไม่
def is_in_range(date, start_date, end_date):
    """
    This function checks if a given date is within a range specified by start_date and end_date.
    """
    return start_date <= date <= end_date

# ฟังก์ชันนี้ใช้ในการจัดเรียงข้อมูลใน DataFrame
def sort_data_by_columns(df: pd.DataFrame, sort_columns: list, ascending_order: list):
    """
    This function sorts the data in a DataFrame by the columns specified in `sort_columns` 
    and in the order specified in `ascending_order`.
    
    Parameters:
    - df (DataFrame): The DataFrame containing the data to be sorted.
    - sort_columns (list): A list of columns by which the sorting will be done.
    - ascending_order (list): A list indicating the sort order for each column 
      (True for ascending, False for descending).
    
    Returns:
    - DataFrame: The sorted DataFrame.
    """
    return df.sort_values(sort_columns, ascending=ascending_order)


# ฟังก์ชันนี้ใช้ในการกรองช่วงวันที่ที่ไม่ซ้ำจาก DataFrame
def process_unique_date_ranges(df: pd.DataFrame,column:str|None=None):
    """
    This function processes date ranges from a DataFrame by filtering out NaN values, 
    removing duplicate date ranges, and returning both the valid date ranges and unique date ranges.
    Parameters:
    - df (DataFrame): The DataFrame containing date ranges (start date and end date).
    Returns:
    - valid_date_ranges (list): A list of valid date ranges including duplicates.
    - unique_date_ranges (list): A list of unique date ranges with duplicates removed.
    """
    df = df.drop_duplicates(subset=['active_from', 'active_to'])
    # Convert the DataFrame to a numpy array for faster processing
    date_array = df.to_numpy()

    # Use list comprehension to filter out NaN values and convert date strings to datetime.date objects
    valid_date_ranges = [
        [parse_date_safe(str(row[0])),
        parse_date_safe(str(row[1]))]
        for row in date_array if pd.notna(row[0]) and pd.notna(row[1])]
    
    # Remove duplicates using Pandas DataFrame for efficient filtering while preserving the original order
    date_df = pd.DataFrame(valid_date_ranges, columns=["START_DATE", "END_DATE"])
    date_df = date_df.drop_duplicates()  # Remove duplicate date ranges
    
    # Convert the DataFrame back to a list
    unique_date_ranges = date_df.values.tolist()

    return valid_date_ranges, unique_date_ranges


# ฟังก์ชันนี้ใช้หาวันที่เริ่มต้นของช่วงวันที่ที่ไม่ทับซ้อน
def find_non_overlapping_start_dates(date_ranges):
    """
    This function identifies the start dates of date ranges that do not overlap with any other date ranges.
    
    Parameters:
    - date_ranges (list): A list of date ranges represented as tuples, where each tuple contains a start and an end date.
    
    Returns:
    - list: A list of start dates that do not overlap with any other date ranges.
    """
    indexed_date_ranges = [[range_item, idx] for range_item, idx in zip(date_ranges, range(len(date_ranges)))]
    
    previous_overlapping_ranges = None  # Initialize a variable to track the previous overlapping date ranges
    non_overlapping_start_dates = []  # Initialize the list to store non-overlapping start dates
    
    for current_range in indexed_date_ranges:
        overlapping_ranges = None
        
        # Check if there's an overlap with the current date range
        if previous_overlapping_ranges is not None:
            # Identify date ranges that overlap with the current start date
            overlapping_ranges = [range_item for range_item in indexed_date_ranges if range_item[0][0] <= current_range[0][0] and range_item[0][1] >= current_range[0][0]]
            
            if len(overlapping_ranges) < len(previous_overlapping_ranges):
                non_overlapping_start_dates.append(previous_range[0][0])
            elif len(overlapping_ranges) == len(previous_overlapping_ranges) and [item[1] for item in overlapping_ranges] not in [item[1] for item in previous_overlapping_ranges]:
                non_overlapping_start_dates.append(previous_range[0][0])

        previous_overlapping_ranges = [range_item for range_item in indexed_date_ranges if range_item[0][0] <= current_range[0][0] and range_item[0][1] >= current_range[0][0]] if overlapping_ranges is None else overlapping_ranges.copy()
        previous_range = current_range.copy()  # Track the current date range for comparison
    
    overlapping_ranges = None
    if previous_overlapping_ranges is not None:
        overlapping_ranges = [range_item for range_item in indexed_date_ranges if range_item[0][0] <= current_range[0][0] and range_item[0][1] >= current_range[0][0]]
        if len(overlapping_ranges) < len(previous_overlapping_ranges):
            non_overlapping_start_dates.append(previous_range[0][0])
        elif len(overlapping_ranges) == len(previous_overlapping_ranges) and [item[1] for item in overlapping_ranges] not in [item[1] for item in previous_overlapping_ranges]:
            non_overlapping_start_dates.append(previous_range[0][0])
    
    # Remove duplicate start dates
    unique_non_overlapping_start_dates = []
    for start_date in non_overlapping_start_dates:
        if start_date not in unique_non_overlapping_start_dates:
            unique_non_overlapping_start_dates.append(start_date)

    return unique_non_overlapping_start_dates

# ฟังก์ชันนี้ใช้ในการตรวจสอบวันที่ที่อยู่ในช่วงที่กำหนด
def check_dates_in_range(data,Date_Data):
    """
    This function checks if any date in 'data' falls within the date ranges specified in 'date_ranges'.
    If a match is found, the corresponding date is added to the result list. 
    If no match is found, 'error' is added.
    """
    # แปลงค่างหมดใน Date_play
    conn = sqlite3.connect(Date_Data["Database Path"])
    # converted_dates = [convert_to_yyyymmdd(date) for date in data]
    cursor = conn.cursor()
    for date_list in data:
        datestr = date_list.strftime('%d/%m/%Y')
        date_str = date_list.strftime('%Y-%m-%d')  # แปลง datetime.date เป็น string
        cursor.execute('''
            UPDATE promotion_data
            SET optimal_date = ?
            WHERE DATE(SUBSTR(`active_from`, 7, 4) || '-' || SUBSTR(`active_from`, 4, 2) || '-' || SUBSTR(`active_from`, 1, 2)) <= ?
            AND DATE(SUBSTR(`active_to`, 7, 4) || '-' || SUBSTR(`active_to`, 4, 2) || '-' || SUBSTR(`active_to`, 1, 2)) >= ?
                AND optimal_date = "" AND version = ? AND round =?
        ''', (datestr, date_str, date_str,Date_Data["Version"][:5],Date_Data["Version"][6:]))
    cursor.execute('''
            UPDATE promotion_data
            SET optimal_date = `active_to`
            WHERE `active_from`= `active_to` AND optimal_date = "" AND version = ? AND round =?
        ''', (Date_Data["Version"][:5],Date_Data["Version"][6:],))
    cursor.execute('''
            UPDATE promotion_data
            SET optimal_date = 'ERROR'
            WHERE optimal_date = "" AND Version = ? AND round =?
        ''', (Date_Data["Version"][:5],Date_Data["Version"][6:],))
    conn.commit() 
    conn.close()


# ฟังก์ชันหลักที่จัดการช่วงเวลาโปรโมชั่น
def Promotion_Time_Zone_Management(Date_Data: pd.DataFrame):
    """
    Main function that manages date ranges for promotions, performing sorting, processing unique date ranges,
    and checking if specific dates fall within these ranges.
    """
    conn = sqlite3.connect(Date_Data["Database Path"])
    query = "SELECT `active_from`, `active_to` FROM promotion_data WHERE  version = ? AND round = ?"
    df = pd.read_sql_query(query, conn, params=(str(Date_Data["Version"])[:5], str(Date_Data["Version"])[6:]))
    conn.close()
    # แปลงคอลัมน์เป็น datetime
    df["active_from"] = pd.to_datetime(df["active_from"], errors="coerce")
    df["active_to"] = pd.to_datetime(df["active_to"], errors="coerce")
    # ปิดการเชื่อมต่อฐานข้อมูล
    _ = sort_data_by_columns(Date_Data, ["active_from", "active_to"], [True, True])
    _, unique_date_ranges = process_unique_date_ranges(df)
    Date_play = find_non_overlapping_start_dates(unique_date_ranges)
    Date_play = check_dates_in_range(Date_play,Date_Data)

    return Date_play
