import zipfile
import sqlite3
import tempfile
import json
import glob
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load existing questions to preserve metadata (tip, answer, methods, etc.)
with open('data/questions.json', 'r', encoding='utf-8') as f:
    existing_questions = json.load(f)

q_meta_map = {q['id']: q for q in existing_questions}

# 2. Extract MarginNote typed text (combining ZHIGHLIGHT_TEXT and ZNOTES_TEXT)
fname = '政治解题方法一页纸（含答案和解析）(2025-11-06-16-23-08).marginpkg'
with zipfile.ZipFile(fname, 'r') as z:
    inner_name = z.namelist()[0]
    data = z.read(inner_name)
    with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

conn = sqlite3.connect(tmp_path)
c = conn.cursor()
c.execute('SELECT ZNOTETITLE, ZHIGHLIGHT_TEXT, ZNOTES_TEXT FROM ZBOOKNOTE')
all_notes = c.fetchall()
conn.close()
os.unlink(tmp_path)

# 3. Helper: inline text splitter
def split_stem_and_options(text):
    text = text.strip()
    trans = str.maketrans('ＡＢＣＤ', 'ABCD')
    text = text.translate(trans)
    
    # Matches option markers: A., A．, A。, A、, A，, A:, (A), （A）, or A directly after Chinese char
    opt_regex = re.compile(r'(?:[（(]|\b|\s|^|(?<=[\u4e00-\u9fa5]))([A-D]|8|0)(?:[)）]|[.\uFF0E、，,:：_。\s])\s*')
    matches = list(opt_regex.finditer(text))
    
    def matches_key(char, expected):
        if char == expected: return True
        if expected == 'B' and char == '8': return True
        if expected == 'D' and char == '0': return True
        return False

    found_seq = []
    for i_a, m_a in enumerate(matches):
        if matches_key(m_a.group(1), 'A'):
            for i_b in range(i_a + 1, len(matches)):
                m_b = matches[i_b]
                if matches_key(m_b.group(1), 'B'):
                    for i_c in range(i_b + 1, len(matches)):
                        m_c = matches[i_c]
                        if matches_key(m_c.group(1), 'C'):
                            for i_d in range(i_c + 1, len(matches)):
                                m_d = matches[i_d]
                                if matches_key(m_d.group(1), 'D'):
                                    found_seq = [m_a, m_b, m_c, m_d]
                                    break
                            if found_seq: break
                    if found_seq: break
            if found_seq: break
            
    if len(found_seq) == 4:
        m_a, m_b, m_c, m_d = found_seq
        stem = text[:m_a.start()].strip()
        stem = re.sub(r'^\s*\d+\s*[.．、\s]\s*', '', stem)
        
        opt_a = text[m_a.end():m_b.start()].strip()
        opt_b = text[m_b.end():m_c.start()].strip()
        opt_c = text[m_c.end():m_d.start()].strip()
        opt_d = text[m_d.end():].strip()
        
        # In case D had trailing analysis comments, trim at first double newline or teacher note
        opt_d = re.split(r'\n\s*\n|排除[A-D]|选[A-D]{1,4}|【解析】', opt_d)[0].strip()
        
        return stem, {'A': opt_a, 'B': opt_b, 'C': opt_c, 'D': opt_d}
        
    return None, None

# Build typed notes map
hl_combined_map = {}
for q in existing_questions:
    qid = q['id']
    for title, hl, notes in all_notes:
        t = (title or '').strip()
        if re.search(rf'(?<!\d){re.escape(qid)}(?!\d)', t):
            combined = (hl or '').strip()
            if notes:
                # If notes contains options or text, append
                first_part = notes.split('\n\n')[0].strip()
                if first_part and ('A' in first_part or 'D' in first_part or len(first_part) > 10):
                    combined = combined + (" " if combined else "") + first_part
            s, opts = split_stem_and_options(combined)
            if s and opts and all(opts[k] for k in ['A', 'B', 'C', 'D']):
                hl_combined_map[qid] = combined
                break

print(f"Typed questions available in MarginNote: {len(hl_combined_map)} / 68")

# 4. Helper: geometric box parser
def parse_ocr_boxes(boxes_and_texts):
    # Try geometric parsing first
    anchors = {}
    for i, (box, text, score) in enumerate(boxes_and_texts):
        t = text.strip()
        t_clean = re.sub(r'[.．、:：_。\s]', '', t)
        y_mid = (box[0][1] + box[2][1]) / 2
        x_left = box[0][0]
        
        if t_clean in ['A', 'B', '8', 'C', 'D', '0'] or re.match(r'^[A-D|8|0][.．、:：_。\s]', t):
            key = t_clean[0]
            if key == '8': key = 'B'
            if key == '0': key = 'D'
            if key in ['A', 'B', 'C', 'D'] and key not in anchors:
                anchors[key] = (i, y_mid, x_left, t)
                
    if len(anchors) == 4 and (anchors['A'][1] < anchors['B'][1] < anchors['C'][1] < anchors['D'][1]):
        y_A = anchors['A'][1]
        y_B = anchors['B'][1]
        y_C = anchors['C'][1]
        y_D = anchors['D'][1]
        
        div_stem_A = y_A - (y_B - y_A) * 0.4
        div_AB = (y_A + y_B) / 2
        div_BC = (y_B + y_C) / 2
        div_CD = (y_C + y_D) / 2
        
        stem_items = []
        opt_items = {'A': [], 'B': [], 'C': [], 'D': []}
        
        for i, (box, text, score) in enumerate(boxes_and_texts):
            t = text.strip()
            if not t: continue
            y_mid = (box[0][1] + box[2][1]) / 2
            
            if t in ['A', 'B', '8', 'C', 'D', '0', 'A.', 'B.', 'C.', 'D.', 'A．', 'B．', 'C．', 'D．']:
                continue
            t_sub = re.sub(r'^[A-D|8|0][.．、:：_。\s]\s*', '', t).strip()
            if not t_sub: continue
            
            if y_mid < div_stem_A:
                stem_items.append(t)
            elif y_mid < div_AB:
                opt_items['A'].append(t_sub)
            elif y_mid < div_BC:
                opt_items['B'].append(t_sub)
            elif y_mid < div_CD:
                opt_items['C'].append(t_sub)
            else:
                opt_items['D'].append(t_sub)
                
        stem = "".join(stem_items).strip()
        stem = re.sub(r'^\s*\d+\s*[.．、\s]\s*', '', stem)
        opts = {k: " ".join(v).strip() for k, v in opt_items.items()}
        
        if stem and all(opts[k] for k in ['A', 'B', 'C', 'D']):
            return stem, opts, 'geometric'
            
    # Fallback to inline text splitting
    full_text = " ".join([t.strip() for box, t, s in boxes_and_texts if t.strip()])
    stem, opts = split_stem_and_options(full_text)
    if stem and opts and all(opts[k] for k in ['A', 'B', 'C', 'D']):
        return stem, opts, 'inline'
        
    return None, None, 'failed'

# Common OCR typo corrections for standard Political Theory terms
CORRECTIONS = {
    '笫二次': '第二次',
    '笫一次': '第一次',
    '笫三次': '第三次',
    '笫': '第',
    '娈成': '变成',
    '共产觉': '共产党',
    '民主觉派': '民主党派',
    '我臼': '我国',
    '苤本': '基本',
    '脬故': '解放',
    '肘期': '时期',
    '宜言': '宣言',
    '上句': '上旬',
    '改娈': '改变',
    '联合围': '联合国',
}

def clean_ocr_typos(text):
    for bad, good in CORRECTIONS.items():
        text = text.replace(bad, good)
    return text

# Load cached OCR boxes
with open('scratch/cached_ocr_boxes.json', 'r', encoding='utf-8') as f:
    cached_ocr_boxes = json.load(f)

final_questions = []
stats = {'typed': 0, 'geometric': 0, 'inline': 0, 'failed': 0}
failed_list = []

for idx, q in enumerate(existing_questions):
    qid = q['id']
    stem, opts, method = None, None, None
    
    # Priority 1: Typed note in MarginNote
    if qid in hl_combined_map:
        t_stem, t_opts = split_stem_and_options(hl_combined_map[qid])
        if t_stem and t_opts and all(t_opts[k] for k in ['A', 'B', 'C', 'D']):
            stem, opts, method = t_stem, t_opts, 'typed'
            
    # Priority 2: High-res MarginNote PNG OCR
    if not stem:
        if qid in cached_ocr_boxes:
            raw_boxes = cached_ocr_boxes[qid]
            stem, opts, method = parse_ocr_boxes(raw_boxes)
            
    if stem and opts and all(opts[k] for k in ['A', 'B', 'C', 'D']):
        stats[method] += 1
        stem = clean_ocr_typos(stem)
        opts = {k: clean_ocr_typos(v) for k, v in opts.items()}
        
        updated_q = dict(q)
        updated_q['stem'] = stem
        updated_q['options'] = opts
        updated_q['needsReview'] = False
        final_questions.append(updated_q)
        print(f"[{idx+1}/68] [SUCCESS-{method}] {qid}: Stem len={len(stem)}, A len={len(opts['A'])}, D len={len(opts['D'])}")
    else:
        stats['failed'] += 1
        failed_list.append(qid)
        print(f"[{idx+1}/68] [FAILED] {qid}")
        final_questions.append(q)

print("\n================== FINAL EXTRACTION SUMMARY ==================")
print("Total questions:", len(final_questions))
print("Stats:", stats)
print("Failed questions:", failed_list)

# Overwrite data/questions.json
with open('data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(final_questions, f, ensure_ascii=False, indent=2)

print("\nSuccessfully updated data/questions.json!")
