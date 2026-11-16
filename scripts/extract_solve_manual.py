import fitz
import json
import re
import os

PDF_PATH = "27考研政治一页纸-解题方法手册.pdf"

CHAPTER_MAP = [
    ("ch01", "最基本的立场问题"),
    ("ch02", "墓碑词"),
    ("ch03", "夸张"),
    ("ch04", "唯心"),
    ("ch05", "时态问题"),
    ("ch06", "不合题意"),
    ("ch07", "对冲命题"),
    ("ch08", "时政"),
    ("ch09", "其他题目"),
]

# Map PDF 9 chapters -> existing method IDs in methods.json for backward compatibility
CHAPTER_TO_METHOD_ID = {
    "ch01": ["target"],
    "ch02": ["absolute"],
    "ch03": ["exaggerate"],
    "ch04": ["idealism"],
    "ch05": ["tense"],
    "ch06": ["irrelevant"],
    "ch07": ["hedge"],
    "ch08": ["others"],
    "ch09": ["others"],
}


def get_two_col_blocks(page, header_y=55, footer_y=800):
    """Return text blocks ordered strictly: left column top-to-bottom, then right column top-to-bottom."""
    mid_x = page.rect.width / 2.0
    blocks = page.get_text("blocks")
    left, right = [], []
    for b in blocks:
        x0, y0, x1, y1, txt, bno, btype = b
        if btype != 0:
            continue
        if y1 < header_y or y0 > footer_y:
            continue
        t = txt.strip()
        if not t:
            continue
        if t in ("澄潇宇一页纸", "解题方法手册", "遴选题习题册"):
            continue
        if re.match(r'^澄潇宇一页纸\s*\n\s*(解题方法手册|遴选题习题册)$', t):
            continue
        if x0 < mid_x - 20:
            left.append((y0, x0, t))
        else:
            right.append((y0, x0, t))
    left.sort(key=lambda item: (item[0], item[1]))
    right.sort(key=lambda item: (item[0], item[1]))
    return [item[2] for item in left] + [item[2] for item in right]


def clean_line_joins(lines):
    """Join wrapped Chinese lines cleanly while preserving paragraph breaks."""
    out = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if out and not out[-1].endswith(("。", "？", "！", "：", ":", "；", "）", ")", "”", "\"", "、")) \
           and not re.match(r'^([A-D]\.|[0-9]+[\.、]|•|❌|✅|⚠️|📌|💡|🔥)', s):
            # Join wrapped line
            out[-1] = out[-1] + s
        else:
            out.append(s)
    return "\n".join(out)


def extract_method_cards(doc):
    """Extract 知识点 001 ~ 073 from pages 9-32 (0-indexed 8..31) with color/row awareness."""
    all_rows = []
    for p_idx in range(8, 33):
        page = doc[p_idx]
        mid_x = page.rect.width / 2.0
        d = page.get_text("dict")
        col_lines = [[], []]
        for b in d["blocks"]:
            if b["type"] != 0:
                continue
            for l in b["lines"]:
                x0, y0, x1, y1 = l["bbox"]
                if y1 < 50 or y0 > 810:
                    continue
                col_idx = 0 if x0 < mid_x - 20 else 1
                spans = []
                for s in l["spans"]:
                    t = s["text"]
                    if t.strip():
                        spans.append((s["color"], s["size"], t))
                if spans:
                    col_lines[col_idx].append((y0, x0, spans))

        for col_idx in (0, 1):
            items = sorted(col_lines[col_idx], key=lambda it: (it[0], it[1]))
            # Merge items on same visual row (abs(y0 - prev_y0) <= 2.2)
            merged_rows = []
            for y0, x0, spans in items:
                if merged_rows and abs(y0 - merged_rows[-1]["y0"]) <= 2.2:
                    merged_rows[-1]["chunks"].append((x0, spans))
                else:
                    merged_rows.append({"y0": y0, "x0": x0, "chunks": [(x0, spans)]})

            stop_page = False
            for r in merged_rows:
                r["chunks"].sort(key=lambda ch: ch[0])
                r_spans = []
                for _, ch_spans in r["chunks"]:
                    r_spans.extend(ch_spans)
                r["spans"] = r_spans
                full_text = "".join(sp[2] for sp in r["spans"]).strip()
                if not full_text or full_text in ("澄潇宇一页纸", "解题方法手册"):
                    continue
                if "C O N T E N T S" in full_text or "遴选题目录" in full_text:
                    stop_page = True
                    break
                # Analyze color semantics
                has_blue = any(((sp[0] & 0xff) > 180 and ((sp[0] >> 16) & 0xff) < 80) for sp in r["spans"])
                has_orange = any((((sp[0] >> 16) & 0xff) > 200 and 50 < ((sp[0] >> 8) & 0xff) < 160) for sp in r["spans"])
                red_words = []
                curr_red = []
                for col, sz, txt in r["spans"]:
                    r_c = (col >> 16) & 0xff
                    g_c = (col >> 8) & 0xff
                    b_c = col & 0xff
                    if r_c > 180 and g_c < 60 and b_c < 60:
                        curr_red.append(txt.strip())
                    else:
                        if curr_red:
                            w = "".join(curr_red).strip()
                            if w and w not in red_words:
                                red_words.append(w)
                            curr_red = []
                if curr_red:
                    w = "".join(curr_red).strip()
                    if w and w not in red_words:
                        red_words.append(w)

                all_rows.append({
                    "page": p_idx + 1,
                    "col": col_idx,
                    "y0": r["y0"],
                    "text": full_text,
                    "has_blue": has_blue,
                    "has_orange": has_orange,
                    "red_words": red_words,
                })
            if stop_page:
                break

    cards = []
    curr = None
    for row in all_rows:
        line = row["text"]
        m = re.match(r'^知识点\s*(\d{3})$', line)
        if m:
            if curr:
                cards.append(curr)
            num = m.group(1)
            curr = {
                "id": f"method-kp-{num}",
                "num": num,
                "page": row["page"],
                "breadcrumb": "",
                "category": "",
                "title": "",
                "rows": [],
            }
            continue
        if curr is None:
            continue
        if not curr["breadcrumb"] and ("›" in line or line in ("高正确率解题思维", "出题老头命题手法", "墓碑词")):
            curr["breadcrumb"] = line
            curr["category"] = line.split("›")[0].strip()
            continue
        if "›" in line and line.startswith(curr["category"]):
            continue
        if not curr["title"]:
            curr["title"] = line
            continue
        curr["rows"].append(row)

    if curr:
        cards.append(curr)

    merged = {}
    for c in cards:
        num = c["num"]
        if num not in merged:
            merged[num] = c
        else:
            merged[num]["rows"].extend(c["rows"])

    result = []
    for num in sorted(merged.keys()):
        c = merged[num]
        # Build structured items by grouping tightly-wrapped lines of same color
        items = []
        for r in c["rows"]:
            txt = r["text"]
            # Extract trailing ref like "2006-4D" or "文2001-25D"
            ref = ""
            m_ref = re.search(r'(文?\d{4}-\d+[A-D]*)$', txt)
            if m_ref:
                ref = m_ref.group(1)
                txt = txt[:m_ref.start()].strip()

            kind = "text"
            if r["has_blue"] or txt.startswith("❌"):
                kind = "wrong"
            elif re.match(r'^(核心|口诀|核心原则|原则|总结)[：:]', txt) or r["has_orange"]:
                kind = "rule"
            elif re.match(r'^(改正|正确|对的|✅)[：:]?', txt):
                kind = "correct"
            elif re.match(r'^(⚠️|注意|避坑|特殊情况|注)[：:]?', txt):
                kind = "note"

            # Join tightly wrapped continuation line if same kind, tight y-gap, no ref on prev
            if items and items[-1]["page"] == r["page"] and items[-1]["col"] == r["col"] \
               and (r["y0"] - items[-1]["y0"]) <= 13.5 \
               and items[-1]["kind"] == kind and not items[-1]["ref"] \
               and not items[-1]["text"].endswith(("。", "？", "！", "：", ":", "）", ")")) \
               and not re.match(r'^([A-D]\.|[0-9]+[\.、]|•|比如|错的|对的|改正|核心|特殊情况|⚠️|❌|✅)', txt):
                items[-1]["text"] += txt
                if ref:
                    items[-1]["ref"] = ref
                for rw in r["red_words"]:
                    if rw not in items[-1]["redWords"]:
                        items[-1]["redWords"].append(rw)
                items[-1]["y0"] = r["y0"]
            else:
                items.append({
                    "kind": kind,
                    "text": txt,
                    "ref": ref,
                    "redWords": r["red_words"],
                    "page": r["page"],
                    "col": r["col"],
                    "y0": r["y0"],
                })

        clean_items = []
        content_lines = []
        for it in items:
            if not it["text"]:
                continue
            clean_items.append({
                "kind": it["kind"],
                "text": it["text"],
                "ref": it["ref"],
                "redWords": it["redWords"],
            })
            line_str = it["text"] + (f" [{it['ref']}]" if it["ref"] else "")
            content_lines.append(line_str)

        result.append({
            "id": c["id"],
            "num": num,
            "page": c["page"],
            "category": c["category"] or "墓碑词",
            "breadcrumb": c["breadcrumb"],
            "title": c["title"],
            "content": "\n".join(content_lines),
            "items": clean_items,
        })
    return result


def extract_tombstone_index(doc):
    """Extract 120+ tombstone keyword -> 知识点序号 mappings from page 71 (index 70)."""
    page = doc[70]
    words = page.get_text("words")  # (x0, y0, x1, y1, word, block_no, line_no, word_no)
    # 3 columns on page 71: x ~ [40..200], [210..380], [390..560]
    cols = [[], [], []]
    for w in words:
        x0, y0, x1, y1, txt, *_ = w
        if y0 < 95 or y0 > 740:
            continue
        if x0 < 205:
            cols[0].append((y0, x0, txt))
        elif x0 < 385:
            cols[1].append((y0, x0, txt))
        else:
            cols[2].append((y0, x0, txt))

    entries = []
    for col in cols:
        col.sort(key=lambda item: (round(item[0] / 3), item[1]))
        # Group by y-line
        lines = []
        last_y = None
        for y0, x0, txt in col:
            if last_y is None or abs(y0 - last_y) > 4:
                lines.append([])
                last_y = y0
            lines[-1].append((x0, txt))
        for line_items in lines:
            line_items.sort(key=lambda t: t[0])
            line_str = " ".join(t[1] for t in line_items).strip()
            if line_str in ("关键词", "知识点序号", "关键词 知识点序号"):
                continue
            m = re.match(r'^[•·]?\s*(.+?)\s+(\d{3})$', line_str)
            if m:
                kw = m.group(1).strip()
                kp_num = m.group(2).strip()
                entries.append({"word": kw, "kpNum": kp_num})
    return entries


def extract_answer_key(doc):
    """Extract 001~133 answer key from page 61 (index 60)."""
    txt = doc[60].get_text("text")
    ans_map = {}
    for m in re.finditer(r'(\d{3})\s+([A-D]{1,4})', txt):
        ans_map[m.group(1)] = list(m.group(2))
    return ans_map


def extract_explanations(doc):
    """Extract 逐题解析 from pages 63-70 (index 62..69)."""
    all_lines = []
    for p_idx in range(62, 70):
        blocks = get_two_col_blocks(doc[p_idx], header_y=50, footer_y=810)
        for b in blocks:
            for line in b.splitlines():
                ls = line.strip()
                if ls and not ls.startswith("EXPLANATIONS") and ls != "逐题解析" and "逐题解析 / 续" not in ls:
                    all_lines.append(ls)

    exps = {}
    curr_no = None
    curr_ans = None
    curr_yn = ""
    curr_lines = []

    for line in all_lines:
        m = re.match(r'^习题(\d{3})\s*·\s*([A-D]+)$', line)
        if m:
            if curr_no:
                exps[curr_no] = {
                    "answer": list(curr_ans),
                    "yearNo": curr_yn,
                    "tip": "\n".join(curr_lines).strip()
                }
            curr_no = m.group(1)
            curr_ans = m.group(2)
            curr_yn = ""
            curr_lines = []
            continue
        if curr_no and not curr_yn and re.match(r'^\d{4}-\d+$', line):
            curr_yn = line
            continue
        if curr_no:
            curr_lines.append(line)

    if curr_no:
        exps[curr_no] = {
            "answer": list(curr_ans),
            "yearNo": curr_yn,
            "tip": "\n".join(curr_lines).strip()
        }
    return exps


def extract_questions_from_pdf(doc, ans_key, exps):
    """Extract all 133 遴选题 from pages 35-60 (index 34..59)."""
    all_lines = []
    for p_idx in range(34, 60):
        blocks = get_two_col_blocks(doc[p_idx], header_y=50, footer_y=810)
        for b in blocks:
            for line in b.splitlines():
                ls = line.strip()
                if ls:
                    all_lines.append((p_idx + 1, ls))

    questions = []
    curr_ch_idx = -1
    curr_q = None
    curr_opt = None

    chapter_names = [c[1] for c in CHAPTER_MAP]

    i = 0
    while i < len(all_lines):
        page_no, line = all_lines[i]
        if line.startswith("CHAPTER "):
            m_ch = re.match(r'^CHAPTER\s*(\d{2})', line)
            if m_ch:
                curr_ch_idx = int(m_ch.group(1)) - 1
            i += 1
            continue
        if re.match(r'^\d{2}\s*道习题$', line) or "/ 续" in line or line in chapter_names:
            i += 1
            continue

        m_q = re.match(r'^习题(\d{3})$', line)
        if m_q:
            if curr_q:
                questions.append(curr_q)
            ex_no = m_q.group(1)
            ch_id, ch_name = CHAPTER_MAP[curr_ch_idx] if 0 <= curr_ch_idx < len(CHAPTER_MAP) else ("ch09", "其他题目")
            curr_q = {
                "exerciseNo": ex_no,
                "chapterId": ch_id,
                "chapterName": ch_name,
                "type": "single",
                "year": "",
                "no": "",
                "stemLines": [],
                "options": {},
                "page": page_no,
            }
            curr_opt = None
            i += 1
            continue

        if curr_q is None:
            i += 1
            continue

        # Check type + year-no line e.g. "单选 2025-7" or "多选 米六2-18"
        m_meta = re.match(r'^(单选|多选)\s+(.+)$', line)
        if m_meta and not curr_q["year"] and not curr_q.get("sourceLabel") and not curr_q["stemLines"]:
            curr_q["type"] = "single" if m_meta.group(1) == "单选" else "multi"
            rest = m_meta.group(2).strip()
            m_yn = re.match(r'^(\d{4})-(\d+)$', rest)
            if m_yn:
                curr_q["year"] = int(m_yn.group(1))
                curr_q["no"] = int(m_yn.group(2))
            else:
                curr_q["sourceLabel"] = rest
                curr_q["year"] = 2026
                curr_q["no"] = int(curr_q["exerciseNo"])
            i += 1
            continue

        # Check option line e.g. "A." or "A. 创立..."
        m_opt_inline = re.match(r'^([A-D])\.\s*(.*)$', line)
        if m_opt_inline:
            curr_opt = m_opt_inline.group(1)
            txt = m_opt_inline.group(2).strip()
            curr_q["options"][curr_opt] = [txt] if txt else []
            i += 1
            continue

        if curr_opt:
            curr_q["options"][curr_opt].append(line)
        else:
            curr_q["stemLines"].append(line)
        i += 1

    if curr_q:
        questions.append(curr_q)

    # Finalize questions
    final_qs = []
    for q in questions:
        ex_no = q["exerciseNo"]
        stem = "".join(q["stemLines"]).strip()
        opts = {}
        for k in ["A", "B", "C", "D"]:
            if k in q["options"]:
                opts[k] = "".join(q["options"][k]).strip()
        ans = exps.get(ex_no, {}).get("answer") or ans_key.get(ex_no, [])
        tip = exps.get(ex_no, {}).get("tip", "")
        final_qs.append({
            "id": f"{q['year']}.{q['no']}" if q["year"] else f"ex{ex_no}",
            "exerciseNo": ex_no,
            "year": q["year"],
            "no": q["no"],
            "type": q["type"],
            "chapterId": q["chapterId"],
            "chapterName": q["chapterName"],
            "methods": CHAPTER_TO_METHOD_ID.get(q["chapterId"], ["others"]),
            "stem": stem,
            "options": opts,
            "answer": ans,
            "tip": tip,
            "source": "27版解题方法手册",
        })
    return final_qs


def main():
    doc = fitz.open(PDF_PATH)
    cards = extract_method_cards(doc)
    tombstones = extract_tombstone_index(doc)
    ans_key = extract_answer_key(doc)
    exps = extract_explanations(doc)
    pdf_qs = extract_questions_from_pdf(doc, ans_key, exps)

    print(f"Extracted method cards: {len(cards)} (expected 73)")
    print(f"Extracted tombstone index entries: {len(tombstones)}")
    print(f"Extracted answer key: {len(ans_key)}, explanations: {len(exps)}")
    print(f"Extracted PDF questions: {len(pdf_qs)}")

    # Check if any question has missing stem, options != 4, or empty answer
    issues = []
    for q in pdf_qs:
        if not q["stem"] or len(q["options"]) != 4 or not q["answer"]:
            issues.append((q["exerciseNo"], len(q["stem"]), list(q["options"].keys()), q["answer"]))
    print(f"PDF questions with structural issues: {len(issues)}")
    for iss in issues[:10]:
        print("  Issue:", iss)

    # Save method_cards.json and tombstone_index.json
    with open("data/method_cards.json", "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    with open("data/tombstone_index.json", "w", encoding="utf-8") as f:
        json.dump(tombstones, f, ensure_ascii=False, indent=2)

    # Merge with existing data/questions.json
    with open("data/questions.json", "r", encoding="utf-8") as f:
        old_qs = json.load(f)

    old_by_yn = {f"{q['year']}-{q['no']}": q for q in old_qs if q.get("year") and q.get("no")}
    merged_qs = []
    seen_yn = set()

    for pq in pdf_qs:
        yn = f"{pq['year']}-{pq['no']}"
        if yn in old_by_yn:
            oq = old_by_yn[yn]
            # Preserve existing rich fields if available
            if oq.get("identKeywords"):
                pq["identKeywords"] = oq["identKeywords"]
            if oq.get("trapOptions"):
                pq["trapOptions"] = oq["trapOptions"]
            if oq.get("trapReason"):
                pq["trapReason"] = oq["trapReason"]
            if oq.get("methods"):
                pq["methods"] = oq["methods"]
            if not pq["tip"] and oq.get("tip"):
                pq["tip"] = oq["tip"]
            pq["id"] = oq["id"]  # keep existing id so user solveRecords stay intact!
        seen_yn.add(yn)
        merged_qs.append(pq)

    # Also keep the non-overlapping questions from old_qs under their mapped chapter
    METHOD_TO_CHAPTER = {
        "target": ("ch01", "最基本的立场问题"),
        "absolute": ("ch02", "墓碑词"),
        "exaggerate": ("ch03", "夸张"),
        "idealism": ("ch04", "唯心"),
        "tense": ("ch05", "时态问题"),
        "irrelevant": ("ch06", "不合题意"),
        "hedge": ("ch07", "对冲命题"),
        "foreign": ("ch06", "不合题意"),
        "us_related": ("ch08", "时政"),
    }
    extra_count = 0
    for oq in old_qs:
        yn = f"{oq.get('year','')}-{oq.get('no','')}"
        if yn not in seen_yn:
            m0 = (oq.get("methods") or ["others"])[0]
            ch_id, ch_name = METHOD_TO_CHAPTER.get(m0, ("ch09", "其他题目"))
            oq_copy = dict(oq)
            oq_copy["chapterId"] = ch_id
            oq_copy["chapterName"] = ch_name
            oq_copy["source"] = oq_copy.get("source", "历年真题补充")
            merged_qs.append(oq_copy)
            extra_count += 1

    # Ensure unique IDs & compute tombstoneHits for each question
    used_ids = set()
    # Sort tombstones longest-first for clean matching
    ts_sorted = sorted(tombstones, key=lambda x: len(x["word"]), reverse=True)
    for q in merged_qs:
        if q["id"] in used_ids:
            q["id"] = f"{q['id']}_ex{q.get('exerciseNo', len(used_ids))}"
        used_ids.add(q["id"])
        opts_text = " ".join(q.get("options", {}).values())
        hits = []
        seen_words = set()
        for t in ts_sorted:
            w = t["word"]
            if w not in seen_words and w in opts_text:
                hits.append({"word": w, "kpNum": t["kpNum"]})
                seen_words.add(w)
        q["tombstoneHits"] = hits

    # Sync methods.json questionIds so every question is tracked
    with open("data/methods.json", "r", encoding="utf-8") as f:
        methods_data = json.load(f)
    m_map = {m["id"]: set() for m in methods_data}
    for q in merged_qs:
        for mid in (q.get("methods") or ["others"]):
            if mid in m_map:
                m_map[mid].add(q["id"])
    for m in methods_data:
        m["questionIds"] = sorted(m_map[m["id"]])
    with open("data/methods.json", "w", encoding="utf-8") as f:
        json.dump(methods_data, f, ensure_ascii=False, indent=2)

    print(f"Merged questions total: {len(merged_qs)} (PDF={len(pdf_qs)}, extra preserved={extra_count})")
    with open("data/questions.json", "w", encoding="utf-8") as f:
        json.dump(merged_qs, f, ensure_ascii=False, indent=2)
    print("Saved data/method_cards.json, data/tombstone_index.json, data/methods.json, data/questions.json")


if __name__ == "__main__":
    main()
