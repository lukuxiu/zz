import zipfile
import sqlite3
import tempfile
import plistlib
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

cursor.execute("SELECT ZNOTETITLE, ZHIGHLIGHT_TEXT, ZNOTES_TEXT, ZHIGHLIGHTS, ZNOTES, ZMEDIA_LIST, ZRECOGNIZE_TEXT FROM ZBOOKNOTE WHERE ZNOTETITLE IS NOT NULL")
rows = cursor.fetchall()

print("Checking plist contents for questions...")
for r in rows[:15]:
    t = r['ZNOTETITLE']
    print(f"\n=== Title: {t} ===")
    print("  Highlight text len:", len(r['ZHIGHLIGHT_TEXT'] or ''))
    print("  Notes text:", repr((r['ZNOTES_TEXT'] or '')[:100]))
    
    if r['ZHIGHLIGHTS']:
        try:
            pl = plistlib.loads(r['ZHIGHLIGHTS'])
            print("  ZHIGHLIGHTS plist keys/type:", type(pl), pl if isinstance(pl, dict) and len(pl) < 5 else f"size: {len(pl)}")
        except Exception as e:
            print("  ZHIGHLIGHTS plist parse error:", e)

    if r['ZNOTES']:
        try:
            pl = plistlib.loads(r['ZNOTES'])
            print("  ZNOTES plist keys/type:", type(pl), f"size: {len(pl)}")
            if '$objects' in pl:
                # Find strings in NSKeyedArchiver objects
                strings = [x for x in pl['$objects'] if isinstance(x, str) and len(x) > 5 and not x.startswith('$')]
                print("  ZNOTES strings in objects:", strings[:3])
        except Exception as e:
            print("  ZNOTES plist parse error:", e)

conn.close()
os.unlink(tmp_path)
