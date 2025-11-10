

import sqlite3
import os
import pandas as pd
import hashlib
from datetime import datetime
from sqlalchemy import create_engine, text,NVARCHAR
from decimal import Decimal
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError

# load_dotenv()
# class manage_locater():
#     def __init__(self):
#         self.DATABASE = 'master' #master
#         self.DRIVERS ="driver=ODBC+Driver+17+for+SQL+Server"
#         self.SERVERS ="""117.113.122.109\SQLEXPRESS2008R2"""    #117.113.122.109\SQLEXPRESS2008R2
#         self.USER ="sa"
#         self.PASSWORD ="Admin2000"
#         self.ENV =os.getenv('ENV')



#     def get_load(self,*args):
#           return f"mssql+pyodbc://{self.USER}:{self.PASSWORD}@{self.SERVERS}/{self.DATABASE}?{self.DRIVERS}"
#     def get_sqlserver(self,*args):
#           return f"mssql+pyodbc://sqlserver555:sqlserver@34.80.44.135/PROMOTION?{self.DRIVERS}"

class MetadataHandler:
    def __init__(self, db_path = "instance/database.db", folder_path = "Temp/Propuct",ip='117.113.122.109',user = 'sa',password ='Admin2000'):
        self.db_path = db_path
        self.folder_path = folder_path     
        self.URL = f"mssql+pyodbc://{user}:{password}@{ip}/master?driver=ODBC+Driver+17+for+SQL+Server"
         
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()
    def connect_sqlserver(self,server='117.113.122.109'):
        try:
            engine = create_engine(self.URL)
            with engine.connect() as conn:
                print("เชื่อมต่อฐานข้อมูลสำเร็จ")
            return engine

        except OperationalError as e:
            error_msg = str(e).lower()
            if "could not open a connection" in error_msg or "login timeout" in error_msg:
                print("ไม่สามารถเชื่อมต่อกับฐานข้อมูลได้ กรุณาตรวจสอบ:")
                print(f" - IP : {server} ถูกต้องหรือไม่")
            else:
                print("เกิดข้อผิดพลาดขณะเชื่อมต่อฐานข้อมูล:", e)

        except Exception as e:
            print("Unexpected error:", e)
    def create_table(self):
        """Create table for storing product data and products_history."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                PRODUCT_CODE TEXT PRIMARY KEY,
                PRODUCT_NAME TEXT,
                SHORT_NAME TEXT,
                SALE_PRICE TEXT,
                PTYPE TEXT,
                BTYPE TEXT,
                barcode TEXT,
                QTY TEXT,
                UNIT TEXT,
                QTY_TARGET TEXT,
                UNIT_TARGET TEXT,
                PRODUCT_TARGET TEXT,
                SHORT_TARGET TEXT,
                VERSION TEXT,
                STATUS TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products_history (
                IP TEXT,
                USER TEXT ,
                last_updated TEXT PRIMARY KEY
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS barcode_MAP (
                PROMOTION_CODE TEXT  PRIMARY KEY,
                PROMOTION_MAP TEXT ,
                COUPON_ID TEXT ,
                MAPCODE TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS REPORTS (
                RP_version TEXT,
                FILE_NAME TEXT ,
                SHEET_NAME TEXT ,
                COU_ROW_INIT TEXT ,
                COU_COL_INIT TEXT ,
                STATUS TEXT ,
                COU_MAP_BAR TEXT ,
                COU_COL_CUT TEXT ,
                COU_ROW_CUT TEXT,
                REMART TEXT
                            
            )
        ''')
        self.conn.commit()

    def get_metadata(self):
        """Get products_history from SQLite."""
        self.cursor.execute('SELECT * FROM products_history ORDER BY 2 LIMIT 1 ')
        return self.cursor.fetchone()

    def save_metadata(self,IP):
        """Save metadata to SQLite with current timestamp for last_updated."""
        last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get current timestamp
        self.cursor.execute('''
            REPLACE INTO products_history (  IP,USER, last_updated)
            VALUES (?,?, ?)
        ''', (IP,os.getlogin(), last_updated))
        self.conn.commit()

    def get_file_hash(self, file_path):
        """Generate hash for the Excel file to compare with stored metadata."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def load_excel_to_sql(self,excel_file):
        """Load data from Excel 'Product' sheet and insert into SQLite database."""
        df = pd.read_excel(excel_file, sheet_name='Product', dtype=str)  # Ensure all data is treated as string
        for index, row in df.iterrows():
            self.cursor.execute('''
                INSERT OR REPLACE INTO products (PRODUCT_CODE, PRODUCT_NAME, SALE_PRICE, barcode)
                VALUES (?, ?, ?, ?)
            ''', (row['PRODUCT_CODE'], row['PRODUCT_NAME'], row['SALE_PRICE'], row['barcode']))
        self.conn.commit()

    def delete_excel_file(self, excel_file):
        print("""Delete Excel file after processing.""")
        os.remove(excel_file)
    def process_Load_LP(self):
        """Process Excel files and update SQLite database."""
        try:
            sql_server_engine = self.connect_sqlserver()
            with sql_server_engine.connect() as connection:
                # คำสั่ง SQL ที่ต้องการรัน
                query = text(f"""  SELECT     
                            CAST(A.MMBR_PROM_ID AS VARCHAR(255)) AS 'PROMOTION_CODE',
                            CAST(B.MMBR_PROM_ID AS VARCHAR(255)) AS 'PROMOTION_MAP',
                            CAST(A.COUPON_ID AS VARCHAR(255)) AS 'COUPON_ID',
                            CAST(A.MMBR_ACCT_ID AS VARCHAR(255)) AS 'MAPCODE'
                        FROM		[LPE_PROM].[dbo].[LPE_PromotionHeader] AS A 
                            LEFT JOIN [LPE_PROM].[dbo].[LPE_PromotionHeader] AS B 
                                ON A.MMBR_ACCT_ID =B.MMBR_ACCT_ID 
                                    AND B.COUPON_ID = ''
                                    AND A.END_DATE > B.STRT_DATE
                            WHERE  A.MMBR_ACCT_ID !=0 
                                AND A.SUSPENDED =0 
                                AND A.COUPON_ID !=''
                                AND A.END_DATE >= GETDATE() 
                                AND B.END_DATE >= GETDATE() """)
                # รันคำสั่ง SQL และดึงข้อมูล
                result = connection.execute(query)
                data = pd.DataFrame(result.fetchall(), columns=result.keys())
                data = data.astype(str)
                # แปลงชนิดข้อมูล Decimal ให้เป็น Float (แก้ปัญหาเรื่อง Decimal)
                data = data.map(lambda x: float(x) if isinstance(x, Decimal) else x)
    
                # บันทึกข้อมูลลง SQLite
                data.to_sql("barcode_MAP", self.conn, if_exists="replace", index=False)
                print("Data successfully saved MAP_barcode")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            # ปิดการเชื่อมต่อ SQLite
            self.conn.commit()
    def process_files(self):
        """Process Excel files and update SQLite database."""
        # Check if there is an Excel file in the folder
        
            # file_hash = self.get_file_hash(excel_file)
            
            # Get metadata from SQLite to compare
        try:
            sql_server_engine = self.connect_sqlserver()
            with sql_server_engine.connect() as connection:
                # คำสั่ง SQL ที่ต้องการรัน
                query = text(f"""                WITH BASE AS (
                    SELECT 
                        MS_PRODUCT.PRODUCT_CODE,
                        MS_PRODUCT.PMA_CODE,
                        MS_PRODUCT.CAT_PMA,
                        MS_PRODUCT.SUBCAT_PMA,
                        MS_PRODUCT.PRODUCT_NAME,
                        MS_PRICE_SALE.SALE_PRICE,
                        MA_BARCODE.BARCODE,
                        MS_PMA.PMA_NAME,
                        MS_CAT.CATEGORY_NAME
                    FROM [POSG2].[dbo].[MA_BARCODE] MA_BARCODE
                    INNER JOIN [POSG2].[dbo].[MS_PRODUCT] MS_PRODUCT 
                        ON MS_PRODUCT.PRODUCT_CODE = MA_BARCODE.PRODUCT_CODE
                    INNER JOIN [POSG2].[dbo].[MS_PRICE_SALE] MS_PRICE_SALE 
                        ON MA_BARCODE.PRODUCT_CODE = MS_PRICE_SALE.PRODUCT_CODE
                    LEFT JOIN [POSG2].[dbo].[MS_PMA] MS_PMA 
                        ON MS_PMA.PMA_CODE = MS_PRODUCT.PMA_CODE
                    LEFT JOIN [POSG2].[dbo].[MS_CATEGORY] MS_CAT 
                        ON MS_CAT.PSA_CODE = MS_PRODUCT.PMA_CODE AND MS_CAT.CATEGORY_CODE = MS_PRODUCT.CAT_PMA
                )
                SELECT 
                    B.PMA_CODE AS PRODUCT_CODE,
                    MAX(B.PRODUCT_NAME) AS PRODUCT_NAME,
                    MAX(B.SALE_PRICE) AS SALE_PRICE,
                    MAX(B.BARCODE) AS BARCODE,
                    MAX(B.PMA_NAME)  AS TYPENAME
                FROM BASE B
                GROUP BY B.PMA_CODE
                UNION
                SELECT 
                    B.PMA_CODE + '_' + B.CAT_PMA AS PRODUCT_CODE,
                    MAX(B.PRODUCT_NAME) AS PRODUCT_NAME,
                    MAX(B.SALE_PRICE) AS SALE_PRICE,
                    MAX(B.BARCODE) AS BARCODE,
                    MAX(B.CATEGORY_NAME)  AS TYPENAME
                FROM BASE B
                GROUP BY B.PMA_CODE, B.CAT_PMA
                UNION
                SELECT 
                    B.PMA_CODE + '_' + B.CAT_PMA + '_' + B.SUBCAT_PMA AS PRODUCT_CODE,
                    MAX(B.PRODUCT_NAME) AS PRODUCT_NAME,
                    MAX(B.SALE_PRICE) AS SALE_PRICE,
                    MAX(B.BARCODE) AS BARCODE,
                    'PRODUCT'  AS TYPENAME
                FROM BASE B
                GROUP BY B.PMA_CODE, B.CAT_PMA, B.SUBCAT_PMA

                UNION
                SELECT 
                    B.PRODUCT_CODE,
                    MAX(B.PRODUCT_NAME) AS PRODUCT_NAME,
                    MAX(B.SALE_PRICE) AS SALE_PRICE,
                    MAX(B.BARCODE) AS BARCODE,
                    'PRODUCT'  AS TYPENAME
                FROM BASE B
                GROUP BY B.PRODUCT_CODE
                ORDER BY PRODUCT_CODE, PRODUCT_NAME, SALE_PRICE DESC;
                """)

                # รันคำสั่ง SQL และดึงข้อมูล
                result = connection.execute(query)
                data = pd.DataFrame(result.fetchall(), columns=result.keys())

                # แปลงชนิดข้อมูล Decimal ให้เป็น Float (แก้ปัญหาเรื่อง Decimal)
                data = data.map(lambda x: float(x) if isinstance(x, Decimal) else x)
                data = data.drop_duplicates(subset=['PRODUCT_CODE'], keep='first')
                for col in data.columns:
                    data[col] = data[col].astype(str)

                # บันทึกข้อมูลลง SQLite
                data.to_sql("products", self.conn, if_exists="replace", index=False)
                # sql_server_engine = create_engine(localsg.get_sqlserver())
                # with sql_server_engine.connect() as conn:
                #     data.to_sql("BarcodeData", conn, if_exists="replace", index=False,dtype={
                #                                                             "PRODUCT_NAME": NVARCHAR(100),
                #                                                             "SHORT_NAME": NVARCHAR(100),
                #                                                             "SHORT_TARGET": NVARCHAR(100)})
                #     print("Data successfully saved sqlserver")
                print("Data successfully saved PRODUCTCODE")

        except Exception as e:
            print(f"Error: {e}")
            # excel_files = [f for f in os.listdir(self.folder_path) if f.endswith('.xlsx')]
            # if excel_files:
            #     # Take the first Excel file (assuming only one file)
            #     excel_file = os.path.join(self.folder_path, excel_files[0])
            #     metadata = self.get_metadata()
            #     if metadata and metadata[0]:
            #         print("Metadata is the same, using existing data from SQLite.")
            #     else:
            #         print("Metadata has changed, updating data from Excel file.")
            #         self.load_excel_to_sql(self.folder_path)
            #         self.save_metadata(self.folder_path)  # Save with current timestamp
            #         self.delete_excel_file(excel_file)
            # else:
            #     print("No Excel file found, using data from SQLite.")
            #     # Handle the case when there are no Excel files, just fetch from SQLite
            #     # self.fetch_data_from_sqlite()
        finally:
            # ปิดการเชื่อมต่อ SQLite
            self.conn.commit()
            


    def fetch_data_from_sqlite(self):
        """Fetch all data from SQLite and print it."""
        self.cursor.execute('SELECT * FROM products')
        products = self.cursor.fetchall()
        for product in products:
            print(product)

    def close(self):
        """Close SQLite connection."""
        self.conn.close()


