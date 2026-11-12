import json
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.dirname(__file__))

# 1. Load OCR data
raw_ocr = json.load(open('data/raw_ocr_questions.json', encoding='utf-8'))

# 2. Load extracted question metadata from build_solve_dataset
from build_solve_dataset import extract_all_questions_and_images, METHOD_QIDS

questions_meta = extract_all_questions_and_images()

final_questions = []
review_list = []

for qid in sorted(questions_meta.keys()):
    meta = questions_meta[qid]
    ocr_info = raw_ocr.get(qid, {'stem': '', 'options': {'A': '', 'B': '', 'C': '', 'D': ''}, 'raw_lines': []})
    
    raw_lines = ocr_info.get('raw_lines', [])
    
    # Smart option extraction from raw_lines if options are empty
    opts = ocr_info.get('options', {'A': '', 'B': '', 'C': '', 'D': ''})
    stem = ocr_info.get('stem', '')
    
    # If options were not parsed by standard A. B. C. D. regex,
    # check if we can cleanly extract them from raw_lines
    if not any(opts.values()) and len(raw_lines) >= 5:
        # Check if last 4 lines look like options
        # A, B, C, D
        candidate_opts = raw_lines[-4:]
        stem_cand = "".join(raw_lines[:-4]).strip()
        opts = {
            'A': candidate_opts[0].strip(),
            'B': candidate_opts[1].strip(),
            'C': candidate_opts[2].strip(),
            'D': candidate_opts[3].strip()
        }
        stem = stem_cand
        
    has_all_opts = all(len(opts[k].strip()) >= 2 for k in ['A', 'B', 'C', 'D'])
    has_stem = len(stem.strip()) >= 8
    has_answer = len(meta['answer']) > 0
    
    # Clean up broken / non-ascii heavy OCR
    def is_mostly_garbled(s):
        if not s: return True
        # Check ratio of unrecognized / symbol characters
        symbols = len(re.findall(r'[\?\ufffd\<\>\[\]\|\_\+\*\\\/\{\}]', s))
        return (symbols / max(1, len(s))) > 0.35

    needs_review = (not has_all_opts) or (not has_stem) or (not has_answer) or is_mostly_garbled(stem) or any(is_mostly_garbled(opts[k]) for k in ['A','B','C','D'])
    
    # Special known answers
    ans = meta['answer']
    if qid == '2020.31':
        # 2020 No.31 is ABCD (legal rights boundaries)
        needs_review = True
    elif qid == '2021.33':
        needs_review = True
    elif qid == '2022.4':
        # 2022 No.4 is single choice, answer in tip says ACD? Wait!
        # In 2022.4 let's check tip
        if meta['type'] == 'single' and len(ans) > 1:
            needs_review = True

    record = {
        "id": qid,
        "year": meta['year'],
        "no": meta['no'],
        "type": meta['type'],
        "stem": stem if not is_mostly_garbled(stem) else "",
        "options": {
            "A": opts['A'] if not is_mostly_garbled(opts['A']) else "",
            "B": opts['B'] if not is_mostly_garbled(opts['B']) else "",
            "C": opts['C'] if not is_mostly_garbled(opts['C']) else "",
            "D": opts['D'] if not is_mostly_garbled(opts['D']) else ""
        },
        "answer": ans,
        "methods": meta['methods'],
        "tip": meta['tip'],
        "image": f"images/solve/{qid}.png",
        "needsReview": needs_review
    }
    
    final_questions.append(record)
    
    if needs_review:
        reasons = []
        if not has_answer: reasons.append("答案需核对")
        if not has_stem or is_mostly_garbled(stem): reasons.append("题干OCR不全")
        if not has_all_opts or any(is_mostly_garbled(opts[k]) for k in ['A','B','C','D']): reasons.append("选项OCR不全")
        review_list.append({
            'id': qid,
            'type': meta['type'],
            'methods': meta['methods'],
            'tip': meta['tip'],
            'answer': ans,
            'reasons': reasons,
            'image': f"public/images/solve/{qid}.png"
        })

# Write data/questions.json
with open('data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(final_questions, f, ensure_ascii=False, indent=2)

print(f"Total questions written: {len(final_questions)}")
print(f"Needs review count: {len(review_list)} / {len(final_questions)}")
print(f"Fully clean OCR count: {len(final_questions) - len(review_list)}")

# Generate docs/question-review-list.md
md_lines = [
    "# 政治解题方法一页纸 · 题库待人工校对清单 (question-review-list.md)",
    "",
    f"> 本清单由自动化解析脚本基于两份一页纸 PDF 思维导图生成，共收录真题 **{len(final_questions)}** 道。",
    f"> 严格遵循：**不编造、不臆测政治试题**。凡是 PDF 缩略图字体过小、手写批注遮挡或 OCR 识别残缺的题干、选项与答案，均打上 `needsReview: true` 标记并在前端显示「真迹切图对照」，供人工对照核对。",
    "",
    f"## 统计概况",
    f"- **总题数**: {len(final_questions)} 题",
    f"- **待核对题数**: {len(review_list)} 题",
    f"- **解析完好题数**: {len(final_questions) - len(review_list)} 题",
    "",
    "---",
    "",
    "## 待核对清单明细",
    "",
    "| 题号 | 类型 | 所属解题手法 | 参考答案 | 一页纸名师破题批注 | 待核验原因 | 对应思维导图真迹切图 |",
    "|---|---|---|---|---|---|---|"
]

for item in review_list:
    methods_str = ", ".join(item['methods'])
    ans_str = "".join(item['answer']) if item['answer'] else "*(待核验)*"
    tip_esc = item['tip'].replace("\n", "<br/>")
    reasons_str = "、".join(item['reasons'])
    img_link = f"[{item['id']}.png](file:///{os.path.abspath(item['image']).replace(chr(92), '/')})"
    md_lines.append(f"| **{item['id']}** | {item['type']} | {methods_str} | {ans_str} | {tip_esc} | {reasons_str} | {img_link} |")

md_lines.append("")
md_lines.append("---")
md_lines.append("## 说明与说明指引")
md_lines.append("1. 所有题目均已在 `public/images/solve/` 中保存了原版 PDF 300 DPI 裁切大图。")
md_lines.append("2. 在刷题页面与错题本中，即使用户遇到标为 `needsReview` 的题目，系统也会将「原图真迹」同屏高亮呈现，不影响刷题与解题技巧学习。")

with open('docs/question-review-list.md', 'w', encoding='utf-8') as f:
    f.write("\n".join(md_lines))

print("Saved docs/question-review-list.md successfully!")
