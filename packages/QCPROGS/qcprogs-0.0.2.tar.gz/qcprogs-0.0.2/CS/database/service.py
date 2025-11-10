
def compare_table_between_db(db1, db2, table_name, values, service=None, schema="ONLSTD"):
    """
    เปรียบเทียบข้อมูลจาก 2 DB (db1, db2) table เดียวกัน
    """
    df1 = db1.fetch_tables(values, service, [table_name])["results"].get(f"{schema}.{table_name}")
    df2 = db2.fetch_tables(values, service, [table_name])["results"].get(f"{schema}.{table_name}")

    if df1 is None or df2 is None:
        print(f"{table_name}: ข้อมูลไม่ครบ (DB1={df1 is not None}, DB2={df2 is not None})")
        return None

    if df1.shape != df2.shape:
        print(f"{table_name}: shape ต่างกัน {df1.shape} vs {df2.shape}")
        return None

    diff = df1.compare(df2, keep_shape=True, keep_equal=False)
    if diff.empty:
        print(f"{table_name}: ข้อมูลเหมือนกันทั้งหมด")
        return True
    else:
        print(f"{table_name}: พบความต่าง")
        return diff

