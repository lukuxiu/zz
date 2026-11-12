# -*- coding: utf-8 -*-
"""
将 Markji 考研政治一页纸题库中的 1,061 条关联真题与模拟题映射到 122 张考点卡片中。
"""

import json
import re

with open('data/knowledge.json', 'r', encoding='utf-8') as f:
    local_data = json.load(f)
local_cards = local_data['records']

with open('scratch/markji_workbench.json', 'r', encoding='utf-8') as f:
    mj_data = json.load(f)

mj_questions = mj_data['questions']
mj_points = []
for part in mj_data.get('parts', []):
    for theme in part.get('themes', []):
        for pt in theme.get('points', []):
            mj_points.append(pt)
mj_by_prompt = {pt['prompt'].strip(): pt for pt in mj_points}

def sort_key(q):
    src = q.get('sourceType', '')
    label = q.get('label', '')
    if src == '真题':
        ym = re.search(r'\d{4}', label)
        year = int(ym.group(0)) if ym else 0
        nm = re.search(r'[-－](\d+)$', label)
        num = int(nm.group(1)) if nm else 0
        return (0, year, num, label)
    else:
        publishers = ['肖', '徐', '腿', '米', '新东方', '苏一', '余峰']
        pub_idx = 99
        for idx, p in enumerate(publishers):
            if label.startswith(p):
                pub_idx = idx
                break
        sm = re.search(r'\d+', label)
        set_num = int(sm.group(0)) if sm else 0
        nm = re.search(r'[-－](\d+)$', label)
        num = int(nm.group(1)) if nm else 0
        return (1, pub_idx, set_num, num, label)

total_rel_q = 0
for c in local_cards:
    title = c['title'].strip()
    match = mj_by_prompt.get(title)
    if not match:
        for p in mj_points:
            if title in p['prompt'] or p['prompt'] in title:
                match = p
                break
    
    rel_qs = []
    if match and match.get('questionIds'):
        for qid in match['questionIds']:
            q = mj_questions.get(qid)
            if q and q.get('stem') and q.get('options') and q.get('answer'):
                rel_qs.append({
                    'id': qid,
                    'label': q.get('displayLabel') or q.get('label'),
                    'sourceType': q.get('sourceType'),
                    'kind': q.get('kind'),
                    'stem': q.get('stem'),
                    'options': q.get('options'),
                    'answer': q.get('answer'),
                    'explanation': q.get('explanation')
                })
    
    rel_qs.sort(key=sort_key)
    c['relatedQuestions'] = rel_qs
    total_rel_q += len(rel_qs)

print(f"Total related questions across 122 cards: {total_rel_q}")

# Save to data/knowledge.json
with open('data/knowledge.json', 'w', encoding='utf-8') as f:
    json.dump(local_data, f, ensure_ascii=False, indent=2)
print("Updated data/knowledge.json")

# Save to public/data/knowledge.json
with open('public/data/knowledge.json', 'w', encoding='utf-8') as f:
    json.dump(local_data, f, ensure_ascii=False, indent=2)
print("Updated public/data/knowledge.json")
