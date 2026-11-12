import zipfile
import sqlite3
import tempfile
import json
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

notes_by_id = {r['ZNOTEID']: r for r in rows}

# Map categories
category_parents = {}
for r in rows:
    title = (r['ZNOTETITLE'] or '').strip()
    links = (r['ZMINDLINKS'] or '').strip()
    if links:
        child_ids = links.split('|')
        for cid in child_ids:
            if cid in notes_by_id:
                category_parents[cid] = title

# Compare with our data/questions.json
existing_questions = json.load(open('data/questions.json', encoding='utf-8'))
existing_map = {q['id']: q for q in existing_questions}

print(f"Total existing questions in data/questions.json: {len(existing_questions)}")

margin_questions = {}
for r in rows:
    raw_title = (r['ZNOTETITLE'] or '').strip()
    m = re.search(r'20\d\d\.\d+', raw_title)
    if not m:
        continue
    qid = m.group(0)
    
    parent_title = category_parents.get(r['ZNOTEID'], '')
    highlight_text = (r['ZHIGHLIGHT_TEXT'] or '').strip()
    notes_text = (r['ZNOTES_TEXT'] or '').strip()
    media_list = [x for x in (r['ZMEDIA_LIST'] or '').split('-') if x]
    
    margin_questions[qid] = {
        'id': qid,
        'raw_title': raw_title,
        'parent_category': parent_title,
        'highlight_text': highlight_text,
        'notes_text': notes_text,
        'media_hashes': media_list,
        'note_id': r['ZNOTEID']
    }

print(f"MarginNote questions count: {len(margin_questions)}")

# Check differences in IDs
missing_in_margin = set(existing_map.keys()) - set(margin_questions.keys())
missing_in_existing = set(margin_questions.keys()) - set(existing_map.keys())

print(f"Missing in MarginNote: {missing_in_margin}")
print(f"Missing in existing questions.json: {missing_in_existing}")

# Now let's compare:
# 1. Notes/Tips (author's exact analysis)
# 2. Answers
# 3. Highlight text (stem + options)
differences = []
for qid in sorted(margin_questions.keys()):
    mq = margin_questions[qid]
    eq = existing_map.get(qid)
    
    if not eq:
        continue
        
    m_note = mq['notes_text'].replace('\r\n', '\n').strip()
    e_tip = eq['tip'].replace('\r\n', '\n').strip()
    
    # Check parent category vs existing methods
    parent = mq['parent_category']
    # If parent is 第一组 or 第二组, parent category is 不合题意
    if parent in ['第一组', '第二组']:
        parent = '不合题意'
        
    diff = {
        'id': qid,
        'margin_parent': parent,
        'existing_methods': eq['methods'],
        'has_highlight_text': len(mq['highlight_text']) > 0,
        'highlight_len': len(mq['highlight_text']),
        'note_match': m_note == e_tip,
        'margin_note': m_note,
        'existing_tip': e_tip,
        'existing_ans': eq['answer']
    }
    differences.append(diff)

print("\n--- Summary of Verification ---")
print(f"Notes matching exactly: {sum(1 for d in differences if d['note_match'])} / {len(differences)}")
print(f"Questions with direct Highlight Text in MarginNote: {sum(1 for d in differences if d['has_highlight_text'])} / {len(differences)}")

for d in differences:
    if not d['note_match']:
        print(f"Note mismatch in {d['id']}:")
        print(f"  MarginNote: {repr(d['margin_note'][:60])}")
        print(f"  Existing:   {repr(d['existing_tip'][:60])}")

conn.close()
os.unlink(tmp_path)
