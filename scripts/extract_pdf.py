import os
import sys
sys.path.append('.')
import json
import re
from collections import defaultdict, Counter
import pymupdf

from scripts.modules.layout import extract_page_layout
from scripts.modules.card_parser import parse_card_content
from scripts.modules.cropper import crop_card_image

# 页面范围：PDF 第11至35页 (0-based 10 to 34)
START_PAGE = 10
END_PAGE = 35

def main():
    pdf_path = "27考研政治一页纸-知识点手册.pdf"
    if not os.path.exists(pdf_path):
        # 寻找当前目录下以.pdf结尾的文件
        cands = [f for f in os.listdir('.') if f.endswith('.pdf')]
        if cands:
            pdf_path = cands[0]
        else:
            raise FileNotFoundError("PDF file not found!")

    print(f"[1/4] Opening PDF: {pdf_path}")
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    print(f"Total pages in doc: {total_pages}, Processing pages: 11 to {END_PAGE}")

    # 目录准备
    os.makedirs("data", exist_ok=True)
    os.makedirs("public/source", exist_ok=True)

    records = []
    
    # 状态追踪：学科、章节、小节
    current_subject = "马原"
    current_chapter = "马原"
    current_section = "基本知识"

    # 用于重复编号追踪
    source_id_counts = defaultdict(int)

    # 逐页提取
    print("[2/4] Parsing layout and cards page by page...")
    for pno in range(START_PAGE, END_PAGE):
        page_pdf = pno + 1
        book_page = page_pdf - 6 # 11页对应书页05
        page = doc[pno]
        
        # 提取版面
        layout = extract_page_layout(page, page_pdf)
        wide_bars = layout["wide_bars"]
        cards = layout["cards"]

        # 更新章节大标题
        text_dict = page.get_text("dict")
        for b in text_dict.get("blocks", []):
            if "lines" in b:
                for line in b["lines"]:
                    lbox = line["bbox"]
                    line_text = "".join(s["text"] for s in line["spans"]).strip()
                    if not line_text:
                        continue
                    # 检查是否落在宽幅栏内
                    is_in_wide = any(wb["bbox"][1] - 5 <= lbox[1] <= wb["bbox"][3] + 5 for wb in wide_bars)
                    if is_in_wide or (lbox[1] < 110 and any(kw in line_text for kw in ["马原", "政经", "史纲", "毛", "思修", "当代", "其他"])):
                        if "马原" in line_text:
                            current_subject = "马原"
                            current_chapter = "马原"
                        elif "政经" in line_text:
                            current_subject = "政经"
                            current_chapter = "政经"
                        elif "史纲" in line_text:
                            current_subject = "史纲"
                            current_chapter = "史纲"
                        elif "其他" in line_text:
                            current_subject = "其他"
                            current_chapter = "其他"
                        
                        # 小节标题更新
                        if any(sec in line_text for sec in ["基本知识", "资本主义及垄断", "计算", "国际", "早期", "大革命", "土地革命", "抗日战争", "解放战争", "建国后", "重要专题", "三大辨析", "会议大观"]):
                            for sec in ["基本知识", "资本主义及垄断", "计算", "国际", "早期", "大革命", "土地革命", "抗日战争", "解放战争", "建国后", "重要专题", "三大辨析", "会议大观"]:
                                if sec in line_text:
                                    current_section = sec
                                    break

        # 遍历每张卡片
        for c in cards:
            card_data = parse_card_content(
                page=page,
                card_rect=c["rect"],
                pno=page_pdf,
                book_pno=book_page,
                current_hierarchy=(current_subject, current_chapter, current_section),
                doc=doc
            )
            
            sid = card_data["sourceId"]
            if not sid:
                # 针对 P18 史纲大图特例：知识点编号为 037（史纲整体脉络）
                if page_pdf == 18 and "史纲" in card_data["title"]:
                    sid = "037"
                    card_data["sourceId"] = "037"
                else:
                    # 容错自动推断或待核验
                    sid = "unknown"
                    card_data["reviewStatus"] = "extraction-error"
                    card_data["reviewNotes"].append("未能识别到原书知识点编号")

            source_id_counts[sid] += 1
            idx_num = source_id_counts[sid]
            record_id = f"kp-{sid}-{idx_num:02d}"

            # 区域方位
            region_col = "left" if c["rect"].x0 < 300 else "right"
            region_row = "top" if c["rect"].y0 < 300 else ("mid" if c["rect"].y0 < 550 else "bottom")
            region_name = f"{region_col}-{region_row}"

            # 裁切图片
            crop_filename = f"{record_id}.png"
            crop_path = os.path.join("public", "source", crop_filename)
            crop_card_image(page, c["bbox"], crop_path, dpi=200)

            # 组装完整知识点记录
            record = {
                "id": record_id,
                "sourceId": sid,
                "subject": current_subject,
                "chapter": current_chapter,
                "section": current_section,
                "title": card_data["title"],
                "rawText": card_data["rawText"],
                "content": card_data["content"],
                "contentHtml": card_data["contentHtml"],
                "keywords": card_data["keywords"],
                "mnemonics": card_data["mnemonics"],
                "distinctions": card_data["distinctions"],
                "symbols": card_data["symbols"],
                "sourcePage": [page_pdf],
                "bookPage": [book_page],
                "occurrences": [
                    {
                        "sourcePage": page_pdf,
                        "bookPage": book_page,
                        "region": region_name,
                        "bbox": card_data["sourceRegion"]
                    }
                ],
                "sourceRegion": card_data["sourceRegion"],
                "sourceImages": [f"source/{crop_filename}"],
                "reviewStatus": card_data["reviewStatus"],
                "reviewNotes": card_data["reviewNotes"]
            }

            # 如果存在口诀或辨析，增加相应提示
            if card_data["distinctions"]:
                record["reviewNotes"].append(f"包含{len(card_data['distinctions'])}条辨析")
            if card_data["mnemonics"]:
                record["reviewNotes"].append(f"包含{len(card_data['mnemonics'])}条口诀")
            if idx_num > 1:
                record["reviewNotes"].append(f"原书编号重复（第{idx_num}次出现）")

            records.append(record)

    print(f"[3/4] Extracted {len(records)} knowledge point cards.")

    # 4. 生成知识库 JSON
    knowledge_base = {
        "version": 1,
        "source": {
            "filename": "27考研政治一页纸-知识点手册.pdf",
            "author": "澄潇宇",
            "totalPages": total_pages,
            "contentPageRange": [11, END_PAGE],
            "bookPageRange": [5, END_PAGE - 6]
        },
        "stats": {
            "totalCards": len(records),
            "uniqueSourceIds": len([k for k in source_id_counts if k != "unknown"]),
            "duplicateSourceIds": len([k for k, v in source_id_counts.items() if v > 1 and k != "unknown"]),
            "needsReviewCount": sum(1 for r in records if r["reviewStatus"] == "needs-review"),
            "verifiedCount": sum(1 for r in records if r["reviewStatus"] == "verified"),
            "errorCount": sum(1 for r in records if r["reviewStatus"] == "extraction-error")
        },
        "records": records
    }

    output_json = "data/knowledge.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)

    print(f"[4/4] Knowledge base written to {output_json} successfully!")
    print(f"Summary: {knowledge_base['stats']}")

if __name__ == "__main__":
    main()
