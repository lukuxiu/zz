import zipfile
import sqlite3
import tempfile
import json
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

pkg_path = '政治解题方法一页纸（含答案和解析）(2025-11-06-16-23-08).marginpkg'

with zipfile.ZipFile(pkg_path, 'r') as z:
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

# Map hierarchy
category_parents = {}
for r in rows:
    title = (r['ZNOTETITLE'] or '').strip()
    links = (r['ZMINDLINKS'] or '').strip()
    if links:
        child_ids = links.split('|')
        for cid in child_ids:
            if cid in notes_by_id:
                category_parents[cid] = title

# Map category names to method IDs
CAT_TO_METHOD_ID = {
    '绝对极端说法': 'absolute',
    '时态问题': 'tense',
    '夸张': 'exaggerate',
    '不合题意': 'irrelevant',
    '第一组': 'irrelevant',
    '第二组': 'irrelevant',
    '对冲命题': 'hedge',
    '国内上升到国外': 'foreign',
    '美国🇺🇸相关': 'us_related',
    '唯心': 'idealism',
    '三项解题法之盯住目标': 'target',
    '其他': 'others'
}

# Load existing questions.json
questions = json.load(open('data/questions.json', encoding='utf-8'))
q_map = {q['id']: q for q in questions}

def parse_highlight_text(ht):
    if not ht:
        return '', {'A':'', 'B':'', 'C':'', 'D':''}
    # Try to split by A． B． C． D． or A. B. C. D. or A、
    # Pattern to find options
    pattern = re.compile(r'([A-D])[．\.\、\:\_\s\-]+')
    splits = pattern.split(ht)
    if len(splits) >= 9:
        # splits: [stem, 'A', textA, 'B', textB, 'C', textC, 'D', textD]
        stem = splits[0].strip()
        opts = {'A':'', 'B':'', 'C':'', 'D':''}
        for i in range(1, len(splits), 2):
            opt_key = splits[i].upper()
            if opt_key in opts:
                opts[opt_key] = splits[i+1].strip()
        return stem, opts
    return ht.strip(), {'A':'', 'B':'', 'C':'', 'D':''}

# Parse MarginNote records
updated_count = 0
for r in rows:
    raw_title = (r['ZNOTETITLE'] or '').strip()
    m = re.search(r'20\d\d\.\d+', raw_title)
    if not m:
        continue
    qid = m.group(0)
    if qid not in q_map:
        continue
        
    q = q_map[qid]
    
    # 1. Author's exact note text
    exact_note = (r['ZNOTES_TEXT'] or '').strip()
    if exact_note:
        q['tip'] = exact_note
        
    # 2. Check category from hierarchy
    parent = category_parents.get(r['ZNOTEID'], '')
    if parent in CAT_TO_METHOD_ID:
        primary_mid = CAT_TO_METHOD_ID[parent]
        if primary_mid not in q['methods']:
            q['methods'].insert(0, primary_mid)
            
    # 3. Check highlight text
    ht = (r['ZHIGHLIGHT_TEXT'] or '').strip()
    if ht:
        stem, opts = parse_highlight_text(ht)
        if stem:
            q['stem'] = stem
        if any(opts.values()):
            for k in ['A', 'B', 'C', 'D']:
                if opts[k]:
                    q['options'][k] = opts[k]

    # 4. Answers verification
    # Parse answers from exact_note
    ans_m = re.search(r'(?:选|all in\s*)([A-D]{1,4})', exact_note)
    if ans_m:
        q['answer'] = list(ans_m.group(1))
    elif "ABCD" in exact_note:
        q['answer'] = ["A", "B", "C", "D"]
    elif "排除C" in exact_note and "ABD" in exact_note:
        q['answer'] = ["A", "B", "D"]
    elif exact_note == 'A':
        q['answer'] = ['A']
        
    # Specific known cases:
    if qid == '2020.31':
        q['answer'] = ['A', 'B', 'C', 'D']
    elif qid == '2021.33':
        q['answer'] = ['A', 'C', 'D']
    elif qid == '2022.4':
        q['answer'] = ['A']
        
    # Re-evaluate needsReview
    has_all_opts = all(len(q['options'][k].strip()) >= 2 for k in ['A', 'B', 'C', 'D'])
    has_stem = len(q['stem'].strip()) >= 8
    has_answer = len(q['answer']) > 0
    q['needsReview'] = not (has_all_opts and has_stem and has_answer)
    
    updated_count += 1

print(f"Updated {updated_count} questions from MarginNote ground truth.")

# Save updated questions.json
with open('data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print("Saved updated data/questions.json successfully!")

conn.close()
os.unlink(tmp_path)
