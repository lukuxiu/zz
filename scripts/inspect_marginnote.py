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
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables in database:')
for t in tables:
    try:
        cursor.execute(f'SELECT count(*) FROM "{t[0]}"')
        cnt = cursor.fetchone()[0]
        print(f'  Table: {t[0]:30s} Count: {cnt}')
    except Exception as e:
        print(f'  Table: {t[0]:30s} Error: {e}')
conn.close()
os.unlink(tmp_path)
