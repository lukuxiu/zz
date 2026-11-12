import zipfile
import sqlite3
import tempfile
import re
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

cursor.execute("SELECT * FROM ZBOOKNOTE")
rows = cursor.fetchall()

# Map note ID to note
notes_by_id = {r['ZNOTEID']: r for r in rows}

# Find all category notes and their child links
category_map = {}
for r in rows:
    title = (r['ZNOTETITLE'] or '').strip()
    links = (r['ZMINDLINKS'] or '').strip()
    if links:
        child_ids = links.split('|')
        category_map[title] = child_ids

print("=== Category hierarchy in MarginNote ===")
for cat, child_ids in category_map.items():
    children_titles = [notes_by_id[cid]['ZNOTETITLE'] for cid in child_ids if cid in notes_by_id and notes_by_id[cid]['ZNOTETITLE']]
    print(f"[{cat}]: {len(children_titles)} children -> {children_titles[:10]}")

print("\n=== All 68 Question Notes Details ===")
q_rows = [r for r in rows if re.search(r'20\d\d\.\d+', r['ZNOTETITLE'] or '')]
print(f"Total question notes found: {len(q_rows)}")

for idx, q in enumerate(sorted(q_rows, key=lambda x: x['ZNOTETITLE'])):
    t = q['ZNOTETITLE']
    ht = (q['ZHIGHLIGHT_TEXT'] or '').strip()
    nt = (q['ZNOTES_TEXT'] or '').strip()
    media = (q['ZMEDIA_LIST'] or '').strip()
    print(f"{idx+1}. [{t}] Text len: {len(ht)} | Media: {bool(media)} | Note: {repr(nt[:70])}")
    if ht:
        print(f"   Text excerpt: {repr(ht[:90])}")

conn.close()
os.unlink(tmp_path)
