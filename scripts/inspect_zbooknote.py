import zipfile
import sqlite3
import tempfile
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
fname = '政治解题方法一页纸（含答案和解析）(2025-11-06-16-23-08).marginpkg'

with zipfile.ZipFile(fname, 'r') as z:
    inner_name = z.namelist()[0]
    data = z.read(inner_name)
    with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

conn = sqlite3.connect(tmp_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(ZBOOKNOTE)")
columns = [col['name'] for col in cursor.fetchall()]
print('Columns in ZBOOKNOTE:', columns)

cursor.execute("SELECT * FROM ZBOOKNOTE LIMIT 5")
for idx, row in enumerate(cursor.fetchall()):
    print(f"\n--- Row {idx+1} ---")
    for col in columns:
        val = row[col]
        if val is not None and val != '' and val != 0:
            print(f"  {col}: {repr(val)[:150]}")

conn.close()
os.unlink(tmp_path)
