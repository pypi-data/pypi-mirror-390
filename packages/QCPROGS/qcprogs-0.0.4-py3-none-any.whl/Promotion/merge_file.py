import os
import pandas as pd
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import shutil
def to_int(val):
    try:
        return int(val)
    except:
        return None

def to_decimal(val):
    try:
        return float(val)
    except:
        return None

def to_date(val):
    try:
        return pd.to_datetime(val, errors='coerce', dayfirst=True)
    except:
        return None
def convertypetosqlserver(df):
    # แปลงชนิดข้อมูล
    int_cols = ['promotion_code','levelid','redemption_limit_per_transaction',
                'redemption_limit_per_day','maximum_redemption_limit','bucketid',
                'trigger_value','attachmentmode','entity_type','limit_number_of_items_to']
    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].apply(to_int)

    decimal_cols = ['reward_value']
    for col in decimal_cols:
        if col in df.columns:
            df[col] = df[col].apply(to_decimal)

    date_cols = ['active_from','active_to','optimal_date','updated_date']
    for col in date_cols:
        if col in df.columns:
            df[col] = df[col].apply(to_date)
    return df

# with open('Promotion/queries/config.json', 'r',encoding="utf-8", errors="replace") as file:
#     data = json.load(file)
promotion_columns = ["promotion_code","promotion_name","active_from",
                     "active_to","entity_code","entity_name","coupon_code39",
                     "barcode","member_segmentation","levelid","barcode_code39",
                     "reward_type","reward_value","reward_ma_name","reward_ma_id",
                     "promotion_status","condition_name","condition_ma_id","condition_ma_name",
                     "promotion_type","receipt_promotion_name","group_name","coupon_id",
                     "redemption_limit_per_transaction","redemption_limit_per_day",
                     "maximum_redemption_limit","notes","sheet","worksheet","optimal_date",
                     "version","round","bucketid","trigger_value","attachmentmode","entity_type",
                     "all_members_card_required","member_segments_tiers","cv_code_supplier","cv_name",
                     "trigger_type","updated_date","external_id","limit_number_of_items_to"]
def clean_data(df):
    """
    Cleans the DataFrame by removing ".0" and converting it to an empty string "".
    """
    df = df.map(lambda x: str(x).replace("nan", "") if isinstance(x, (str,int, float)) else x)
    df = df.map(lambda x: str(x).replace(".0", "") if isinstance(x, (str,int, float)) else x)
    return df

def process_file(file_path, db_path,version, backup_folder):
    """
    Processes a single Excel file, extracting data and saving to the database. 
    Also moves the file to the backup folder if successful.
    """

    try:    
        conn = sqlite3.connect(db_path)
        table_name = "promotion_data"
        # อ่านทุก Sheet ในไฟล์ Excel
        excel_data = pd.read_excel(file_path, sheet_name=None, converters={col: str for col in promotion_columns})
        for sheet, df in excel_data.items():
            TEMP_REPORT= ['' for _ in range(10)]
            # แปลงชื่อคอลัมน์ในทุกแผ่นงานให้เป็นตัวพิมพ์ใหญ่
            df.columns = (df.columns.str.strip().str.lower().str.replace(r'[^\w\s]', '', regex=True).str.replace(r'\s+', '_', regex=True))
            TEMP_REPORT[0:5] =[str(version) ,os.path.basename(file_path),sheet,"0","0","0"]
            if "promotion_code" in df.columns:
                TEMP_REPORT[3:5] =[df.shape[0],df.shape[1],"1"]
                df.dropna(subset=["promotion_code"], inplace=True)
                df['sheet'] = sheet
                df['worksheet'] = os.path.basename(file_path)
                # กรองคอลัมน์ที่เกินออกและเพิ่มคอลัมน์ที่ขาดหาย
                df = clean_data(df)
                if "entity_code" not in df.columns:
                    df['entity_code'] = ''
                df['entity_code'] = df['entity_code'].apply(lambda x: f'0{str(x)}' if len(str(x)) == 6 else ('' if pd.isna(x) or str(x) == "nan" else str(x)))
                try:
                    df = map_barcode(df, conn)
                except Exception as e:
                    TEMP_REPORT[9] = str(e)
                    print(f"Error processing {e}")
                df = df[[col for col in df.columns if col in promotion_columns]]  # กรองคอลัมน์ที่มีใน promotion_columns
                for col in promotion_columns:
                    if col not in df.columns:
                        df[col] = ''  # เพิ่มคอลัมน์ที่ขาดหายไปพร้อมกับค่า NaN (ค่าว่าง)
                # df['UPDATE_SATE'] = str(datetime.date.today().strftime('%d/%m/%Y'))
                df['version'] = str(version)[:5]
                df['round'] = (str(version)[6:] or '0').zfill(2)
                df.dropna(subset=["promotion_code"], inplace=True)
                TEMP_REPORT[7:8] =[df.shape[0],df.shape[1]]
                df['barcode_code39'] = df['barcode'].apply(
                    lambda x: f'*{str(x)}*' if len(str(x)) > 7 else f'')
                df['coupon_id'] = df['coupon_id'].apply(str)
                df['optimal_date'] = df['active_from'].apply(str)
                df['coupon_code39'] = df['coupon_id'].apply(lambda x: f'*{str(x)}*' if len(str(x)) > 7 else f'')
                TEMP_REPORT[6]= str(df.apply(
                lambda row: row['barcode'] == '' 
                    and pd.notnull(row['barcode']) 
                    and pd.notnull(row['entity_code']) 
                    and len(row['entity_code']) == 7, axis=1
                ).sum())
                for i in df.columns:
                    df[i] = df[i].astype(str)
                df = clean_data(df)

                df.to_sql(table_name, conn, if_exists='append', index=False, chunksize=1000)
                # df = convertypetosqlserver(df)
                # connetdatbase(df)
                TEMP_REPORT[5] = "S"
            merge_report(TEMP_REPORT,db_path)   
            # Move file to backup folder if merge is successfulid

            # promotion_code bucketid entity_code entity_name barcode trigger_value trigger_type attachmentmode entity_type
            #   sale_price qty_target product_target short_target status version
        
            
    except Exception as e:
        TEMP_REPORT[9] = str(e)
        merge_report(TEMP_REPORT,db_path)
        print(f"Error processing file sheet {sheet}  : {os.path.basename(file_path)}: {e}")
        # unmerged_locations.append([None, os.path.basename(file_path)])
    finally:
        conn.close()
        shutil.move(file_path, os.path.join(backup_folder, os.path.basename(file_path)))
    # return unmerged_locations


#----------------- DATA------------------
def merge_report(Data,db_path):
    """
    Merges data from a large number of Excel files into a database using parallel processing.
    Moves processed files to a backup folder.
    """
    # สร้างฐานข้อมูลหากยังไม่มี
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
                INSERT OR REPLACE INTO REPORTS (RP_version, FILE_NAME, SHEET_NAME, COU_ROW_INIT,COU_COL_INIT,STATUS,COU_MAP_BAR,COU_COL_CUT,COU_ROW_CUT,REMART)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(Data[0:10]))
    conn.commit()
def merge_large_dataset(importd_dict,excel_files=[]):
    """
    Merges data from a large number of Excel files into a database using parallel processing.
    Moves processed files to a backup folder.
    """
    # สร้างฐานข้อมูลหากยังไม่มี
    db_path = importd_dict["Database Path"]
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS promotion_data (
            {', '.join([f'"{col}" TEXT' for col in promotion_columns])}
        )
    """)
    conn.commit()
    conn.close()
    try : 
        if len(excel_files) ==0 :
            excel_files = os.listdir(importd_dict["import file path"]) 
        # ใช้ ProcessPoolExecutor สำหรับการประมวลผลแบบขนาน
        with ThreadPoolExecutor(max_workers=4) as executor:
            with tqdm(total=len(excel_files), desc="Processing Excel files", ncols=90) as pbar:
                futures = [executor.submit(process_file, os.path.join(importd_dict["import file path"], file), db_path,importd_dict["Version"], importd_dict["Backup File Path"]) for file in excel_files]
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Error in thread processing: {e}")
        print('start map coupon')
    finally :
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE promotion_data
            SET coupon_code39 = (
            SELECT DISTINCT c2.coupon_code39
            FROM promotion_data AS c2
            WHERE c2.condition_name = promotion_data.condition_name
            AND c2.version = promotion_data.version
            AND c2.round = promotion_data.round
            AND  not(c2.coupon_code39 is null or c2.coupon_code39 ='') 
            AND (notes LIKE  '%On Top%'  OR notes LIKE  '%Line%' )
            )WHERE (coupon_code39 is null or coupon_code39 ='') 
            AND (notes LIKE  '%On Top%'  OR notes LIKE  '%Line%' )
            AND version = ?
            AND round = ?
        """, (str(importd_dict["Version"])[:5], str(importd_dict["Version"])[6:]))
        conn.commit()
        conn.close()

def map_barcode(df, conn):
    """
    Map barcode from Table 1 to DataFrame based on PRODUCT_CODE and entity_code.
    
    Parameters:
        df (DataFrame): DataFrame ที่ต้องการ Map ข้อมูล
        conn (sqlite3.Connection): Connection ของฐานข้อมูล SQLite
    
    Returns:
        DataFrame: DataFrame ที่มีการเติมข้อมูล barcode
    """
    # Query barcode จาก Table 1
    query = "SELECT PRODUCT_CODE,BARCODE as barcode FROM products"
    products = pd.read_sql_query(query, conn)

    # Map ข้อมูล barcode ไปยัง DataFrame

    # แทนที่ NaN ด้วยค่าว่าง (เช่น '') ก่อนแปลง
    products['PRODUCT_CODE'].fillna('').astype(str)
    df = pd.merge(
        df, 
        products[['PRODUCT_CODE', 'barcode']],  # เลือกเฉพาะคอลัมน์ที่ต้องการ
        left_on='entity_code',  # คอลัมน์ใน df ที่จะใช้จับคู่
        right_on='PRODUCT_CODE',  # คอลัมน์ใน products ที่จะใช้จับคู่
        how='left'  # ใช้ left join เพื่อรักษาข้อมูลทั้งหมดจาก df
    )
    # หากไม่ต้องการคอลัมน์ PRODUCT_CODE ใน df, ลบออก
    df.drop('PRODUCT_CODE', axis=1, inplace=True)
    df['barcode'].apply(lambda x: f'{str(x)}' if 6 < len(str(x)) < 15 else f'')
    return df



