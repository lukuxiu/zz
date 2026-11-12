import zipfile
import sqlite3
import tempfile
import plistlib
import os
import re
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

print(f"Total rows in ZBOOKNOTE: {len(rows)}")

q_notes = []
method_notes = []
other_notes = []

for r in rows:
    title = (r['ZNOTETITLE'] or '').strip()
    highlight_text = (r['ZHIGHLIGHT_TEXT'] or '').strip()
    notes_text = (r['ZNOTES_TEXT'] or '').strip()
    note_id = r['ZNOTEID']
    mind_links = (r['ZMINDLINKS'] or '').strip()
    
    if re.search(r'20\d\d\.\d+', title):
        q_notes.append(r)
    elif any(k in title for k in ['绝对', '时态', '夸张', '不合题意', '对冲', '国外', '美国', '唯心', '盯住', '名言', '墓碑', '解题']):
        method_notes.append(r)
    else:
        other_notes.append(r)

print(f"Question notes: {len(q_notes)}")
print(f"Method notes: {len(method_notes)}")
print(f"Other notes: {len(other_notes)}")

print("\n--- Method Notes ---")
for m in method_notes:
    print(f"  Title: {m['ZNOTETITLE']} (ID: {m['ZNOTEID']}, Links: {m['ZMINDLINKS'][:60] if m['ZMINDLINKS'] else ''})")

print("\n--- Sample Question Notes ---")
for q in q_notes[:10]:
    t = q['ZNOTETITLE']
    ht = (q['ZHIGHLIGHT_TEXT'] or '').replace('\n', ' ')
    nt = (q['ZNOTES_TEXT'] or '').replace('\n', ' ')
    print(f"[{t}] Highlight len: {len(ht)} | Note: {nt[:60]}")
    if ht:
        print(f"   Excerpt: {ht[:120]}...")

conn.close()
os.unlink(tmp_path)
