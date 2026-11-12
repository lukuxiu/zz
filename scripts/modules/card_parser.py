import re
import pymupdf
from scripts.modules.color_extractor import process_spans_to_content
from scripts.modules.symbol_mapper import get_symbol_by_hash

# 助记口诀关键词特征
MNEMONIC_TRIGGERS = [
    "口诀", "牢二枢纽", "偷鸡心虚", "虚空鸡头", "威海技师", "三民无主", 
    "只用记住根本", "你干嘛 哎哟", "机器多了", "工人少了", "生孩子", "VS",
    "科比公主", "高质量现任", "金铲铲", "狗屎", "缝衣服", "战斗党", "武弟弟", 
    "是群主", "巴适", "遵君主", "胀气", "事事为"
]

# 排版提示/说明文字黑名单（绝不能作为辨析）
HINT_WORDS = ["已知条件", "红色为所求", "蓝色是已知", "所求"]

# 标签字样黑名单
LABEL_WORDS = ["辨析", "辨析：", "要点：", "助记：", "补充", "正确", "🚩）", "三星", "是2必"]

# 独立条目/序号/书名/标记开头（绝不能与上一行合并）
BULLET_STARTERS = (
    '①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩',
    '✅', '❌', '⚠️', '•', '▲', '⭐', '🚩', '💡', '🎯',
    '⤴️', '⬇️', '⬆️', '➔', '➡️',
    '一、', '二、', '三、', '四、', '五、', '六、',
    '1.', '2.', '3.', '4.', '5.', '6.',
    '《'
)

# 悬挂残片开头（属于上一行尾部被截断的内容，必须与上一行合并）
DANGLING_STARTERS = (
    '%', '‰', '万元', '元', '小时', '天', '年', '月', '日',
    '个', '种', '条', '度', '倍', '）', ')', '”', '’', '、', '，', '。', '；'
)

def should_soft_wrap(curr_text, next_text, curr_max_x, card_rect):
    """
    判断当前行与下一行之间是否为由于卡片物理分栏宽度限制导致的自然软折行（soft wrap）。
    如果是自然折行，则不插入换行符 \\n，确保句子通顺不断句。
    """
    t_curr = curr_text.strip()
    t_next = next_text.strip()
    if not t_curr or not t_next:
        return False

    # 1. 绝不合并：下一行是独立列表项/序号/特殊标记/书名
    if any(t_next.startswith(b) for b in BULLET_STARTERS):
        return False
    if re.match(r'^[（(]?[0-9一二三四五六七八九十]+[）).、]', t_next):
        return False

    # 2. 绝不合并：上一行以句号、问号、叹号、冒号、分号或判断题结论标志（✅❌⚠️）结尾
    if t_curr.endswith(('。', '！', '？', '：', ':', '；', ';', '✅', '❌', '⚠️')):
        return False

    # 3. 必须合并（规则A）：下一行是以百分号、单位、标点开头的悬挂残片
    if any(t_next.startswith(s) for s in DANGLING_STARTERS):
        return True

    # 4. 必须合并（规则B）：上一行以未闭合符号、连接词或箭头结尾（如 ➔、c+v= 等）
    if t_curr.endswith(('(', '（', '+', '=', '÷', '×', '/', '即', '比', '为', '是', '➔', '➡️', '->')):
        return True

    # 5. 必须合并（规则C）：上一行触达卡片右边缘（自然排版折行）
    r_gap = card_rect.x1 - curr_max_x
    if r_gap < 36:
        return True

    return False

def clean_statement_text(text):
    """清洗掉文本中残留的 {{}} 标记及多余符号"""
    if not text:
        return ""
    # 去除 {{}}
    clean = re.sub(r'\{\{([^}]+)\}\}', r'\1', text)
    # 去除首尾的 ✅ ❌ ⚠️ 符号及空白
    clean = re.sub(r'^[✅❌⚠️\s]+', '', clean)
    clean = re.sub(r'[✅❌⚠️\s]+$', '', clean)
    return clean.strip()

def parse_card_content(page, card_rect, pno, book_pno, current_hierarchy, doc):
    """
    解析单张卡片的内容、标题、符号、关键词、口诀与辨析
    """
    cr = card_rect
    w, h = page.rect.width, page.rect.height
    
    # 1. 获取卡片范围内的图片
    page_images = page.get_image_info(xrefs=True)
    card_images = []
    for img in page_images:
        ibox = pymupdf.Rect(img.get("bbox", []))
        center = pymupdf.Point((ibox.x0 + ibox.x1) / 2, (ibox.y0 + ibox.y1) / 2)
        if cr.contains(center) or (cr.intersects(ibox) and ibox.y0 >= cr.y0 - 2 and ibox.y1 <= cr.y1 + 4):
            xref = img.get("xref")
            if xref:
                try:
                    b_img = doc.extract_image(xref)
                    sym_info = get_symbol_by_hash(b_img.get("image", b""))
                    card_images.append({
                        "bbox": [ibox.x0, ibox.y0, ibox.x1, ibox.y1],
                        "symbol": sym_info
                    })
                except Exception:
                    pass

    # 2. 提取卡片内的文字行和spans
    text_dict = page.get_text("dict")
    card_lines = []
    for b in text_dict.get("blocks", []):
        if "lines" in b:
            for l in b["lines"]:
                lr = pymupdf.Rect(l["bbox"])
                line_center = pymupdf.Point((lr.x0 + lr.x1) / 2, (lr.y0 + lr.y1) / 2)
                if cr.contains(line_center) or (cr.intersects(lr) and lr.y0 >= cr.y0 - 2 and lr.y1 <= cr.y1 + 4 and lr.x0 >= cr.x0 - 5 and lr.x1 <= cr.x1 + 5):
                    card_lines.append(l)

    card_lines.sort(key=lambda l: (l["bbox"][1], l["bbox"][0]))

    # 3. 区分标题栏与正文
    title = ""
    source_id = ""
    title_spans = []
    body_lines = []

    for l in card_lines:
        line_y = l["bbox"][1]
        is_title_line = (line_y < cr.y0 + 38)
        if is_title_line:
            for s in l["spans"]:
                t = s["text"]
                m = re.search(r'知识点\s*(\d+)', t)
                if m:
                    source_id = m.group(1).zfill(3)
                if "知识点" not in t:
                    title += t
                title_spans.append(s)
        else:
            body_lines.append(l)

    title = title.strip()
    if not title and title_spans:
        title = "".join(s["text"] for s in title_spans if "知识点" not in s["text"]).strip()

    # 4. 图文混合流组织：按垂直视觉行合并水平片段与嵌入图片
    visual_rows = []
    for l in body_lines:
        y = l["bbox"][1]
        found_row = None
        for r in visual_rows:
            if abs(r["y"] - y) < 3.5:
                found_row = r
                break
        if found_row:
            found_row["spans"].extend(l["spans"])
            found_row["bbox"][2] = max(found_row["bbox"][2], l["bbox"][2])
        else:
            visual_rows.append({
                "y": y,
                "bbox": list(l["bbox"]),
                "spans": list(l["spans"])
            })

    visual_rows.sort(key=lambda r: r["y"])

    ordered_spans = []
    symbols_used = []
    used_img_indices = set()

    row_data = []
    for r in visual_rows:
        row_y = r["y"]
        row_items = []

        for s in r["spans"]:
            row_items.append({"type": "span", "x": s["bbox"][0], "x1": s["bbox"][2], "data": s, "text": s["text"]})

        for idx, img in enumerate(card_images):
            if idx not in used_img_indices and abs(img["bbox"][1] - row_y) < 7:
                sym = img["symbol"]
                symbols_used.append(sym)
                row_items.append({
                    "type": "image",
                    "x": img["bbox"][0],
                    "x1": img["bbox"][2],
                    "text": sym["char"],
                    "data": {
                        "text": f"{sym['char']}",
                        "color": 0x000000,
                        "font": "symbol",
                        "size": 9.0,
                        "bbox": img["bbox"]
                    }
                })
                used_img_indices.add(idx)

        row_items.sort(key=lambda it: it["x"])
        row_text = "".join(it["text"] for it in row_items)
        row_max_x = max([it["x1"] for it in row_items], default=r["bbox"][2])
        row_data.append({
            "items": row_items,
            "text": row_text,
            "max_x": row_max_x,
            "bbox": r["bbox"]
        })

    for i in range(len(row_data)):
        for it in row_data[i]["items"]:
            ordered_spans.append(it["data"])

        # 智能自然折行判断：若与下一行属于同一语义连贯句，则不强制插入换行符
        if i < len(row_data) - 1:
            curr_row = row_data[i]
            next_row = row_data[i + 1]
            if should_soft_wrap(curr_row["text"], next_row["text"], curr_row["max_x"], card_rect):
                pass
            else:
                ordered_spans.append({
                    "text": "\n",
                    "color": 0x000000,
                    "font": "plain",
                    "size": 9.0,
                    "bbox": curr_row["bbox"]
                })
        else:
            ordered_spans.append({
                "text": "\n",
                "color": 0x000000,
                "font": "plain",
                "size": 9.0,
                "bbox": row_data[i]["bbox"]
            })

    for idx, img in enumerate(card_images):
        if idx not in used_img_indices:
            sym = img["symbol"]
            symbols_used.append(sym)
            ordered_spans.append({
                "text": f"{sym['char']}\n",
                "color": 0x000000,
                "font": "symbol",
                "size": 9.0,
                "bbox": img["bbox"]
            })

    # 5. 颜色处理与关键词标记
    content_res = process_spans_to_content(ordered_spans)
    content = content_res["content"]
    keywords = content_res["keywords"]
    content_html = content_res["contentHtml"]
    raw_text = content_res["rawText"]

    # 6. 口诀与助记提取（清洗大括号）
    mnemonics = []
    lines = content.splitlines()
    for ln in lines:
        ln_s = ln.strip()
        if not ln_s:
            continue
        # 检查是否匹配口诀特征
        is_mne = any(trig in ln_s for trig in MNEMONIC_TRIGGERS) or "{直升机}" in ln_s or "{鸡}" in ln_s or "{威海技师}" in ln_s or "{俄国国旗}" in ln_s or "{生子}" in ln_s
        if is_mne:
            clean_mne = clean_statement_text(ln_s)
            if clean_mne:
                mnemonics.append({
                    "text": clean_mne,
                    "reviewStatus": "verified"
                })

    # 7. 辨析 (distinctions) 严格抽取与清洗
    distinctions = []
    # 匹配由 [✅❌⚠️] 引导的候选句
    for m in re.finditer(r'([✅❌⚠️])\s*([^✅❌⚠️\n\r；]+)', content):
        sym = m.group(1)
        raw_stmt = m.group(2).strip()
        clean_stmt = clean_statement_text(raw_stmt)
        
        # 过滤判断：
        # A. 长度必须 >= 5
        if len(clean_stmt) < 5:
            continue
        # B. 排除纯标签词
        if clean_stmt in LABEL_WORDS or any(clean_stmt.startswith(lbl) and len(clean_stmt) <= len(lbl) + 2 for lbl in LABEL_WORDS):
            continue
        # C. 排除排版做题说明
        if any(hw in clean_stmt for hw in HINT_WORDS):
            continue
        # D. 排除口诀助记词（避免误报）
        if any(mw in clean_stmt or clean_stmt in mw for mw in MNEMONIC_TRIGGERS):
            continue

        verdict = "correct" if sym == "✅" else ("wrong" if sym == "❌" else None)
        distinctions.append({
            "statement": clean_stmt,
            "verdict": verdict,
            "sourceSymbol": sym,
            "reviewStatus": "verified" if verdict is not None else "needs-review"
        })

    # 8. 审核状态
    review_status = "needs-review"
    review_notes = []
    if not source_id:
        review_notes.append("缺失原书编号")
    if not title:
        review_notes.append("缺失卡片标题")
    if not content:
        review_notes.append("正文为空")

    return {
        "sourceId": source_id,
        "title": title,
        "rawText": raw_text,
        "content": content,
        "contentHtml": content_html,
        "keywords": keywords,
        "mnemonics": mnemonics,
        "distinctions": distinctions,
        "symbols": symbols_used,
        "sourceRegion": [round(x, 1) for x in [cr.x0, cr.y0, cr.x1, cr.y1]],
        "reviewStatus": review_status,
        "reviewNotes": review_notes
    }
