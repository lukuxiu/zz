import pymupdf
import re

# 页面排除范围
HEADER_Y_MAX = 60.0
FOOTER_Y_MIN = 790.0

def extract_page_layout(page, pno):
    """
    分析指定页面的版面布局：
    1. 提取宽幅章节栏
    2. 提取卡片主体矩形与标题栏矩形
    3. 将文字和图片归属到卡片
    """
    w, h = page.rect.width, page.rect.height
    drawings = page.get_drawings()
    
    # 1. 查找宽幅栏 (横跨双栏, w > 400)
    wide_bars = []
    card_bodies = []
    title_bars = []
    
    for d in drawings:
        r = d.get("rect")
        fill = d.get("fill")
        color = d.get("color")
        if not r:
            continue
        rw, rh = r.width, r.height
        
        # 排除页眉页脚内的装饰线
        if r.y1 < HEADER_Y_MAX or r.y0 > FOOTER_Y_MIN:
            continue
            
        # 宽幅栏
        if rw > 400 and rh < 65:
            wide_bars.append({
                "rect": pymupdf.Rect(r),
                "fill": fill,
                "bbox": [r.x0, r.y0, r.x1, r.y1]
            })
        # 标准卡片主体：宽约 230-265，白底
        elif 230 <= rw <= 265 and rh >= 35:
            if fill and all(c > 0.98 for c in fill):
                card_bodies.append({
                    "rect": pymupdf.Rect(r),
                    "bbox": [r.x0, r.y0, r.x1, r.y1],
                    "width": rw,
                    "height": rh
                })
            # 浅米色标题栏
            elif fill and 0.90 < fill[0] < 0.99 and 0.85 < fill[1] < 0.98 and 0.80 < fill[2] < 0.95 and 15 <= rh <= 60:
                title_bars.append({
                    "rect": pymupdf.Rect(r),
                    "bbox": [r.x0, r.y0, r.x1, r.y1],
                    "width": rw,
                    "height": rh
                })
        # 会议大观等可能的满幅或特殊卡片
        elif rw > 450 and rh > 65:
            card_bodies.append({
                "rect": pymupdf.Rect(r),
                "bbox": [r.x0, r.y0, r.x1, r.y1],
                "width": rw,
                "height": rh
            })

    # P18 特殊处理：P18 包含史纲脉络大图（drawings中可能没有标准圆角矩形或尺寸特殊）
    if pno == 18 and len(card_bodies) < 4:
        # P18 史纲大图卡片位于 y 约 120-420 区域
        # 检查是否已包含
        has_big = any(cb["rect"].y0 < 200 and cb["rect"].height > 150 for cb in card_bodies)
        if not has_big:
            card_bodies.append({
                "rect": pymupdf.Rect(39.0, 115.0, 556.0, 425.0),
                "bbox": [39.0, 115.0, 556.0, 425.0],
                "width": 517.0,
                "height": 310.0
            })

    # 双栏排序规则：左栏 (x0 < 300) 自上而下，右栏 (x0 >= 300) 自上而下
    left_cards = [c for c in card_bodies if c["rect"].x0 < 300]
    right_cards = [c for c in card_bodies if c["rect"].x0 >= 300]
    
    left_cards.sort(key=lambda c: c["rect"].y0)
    right_cards.sort(key=lambda c: c["rect"].y0)
    
    sorted_cards = left_cards + right_cards

    # 匹配每个卡片与其标题栏
    for c in sorted_cards:
        c_rect = c["rect"]
        # 寻找落入卡片顶部的标题栏 (y0 在卡片 y0 附近，或相交)
        matched_bar = None
        for tb in title_bars:
            tb_rect = tb["rect"]
            if abs(tb_rect.x0 - c_rect.x0) < 15 and abs(tb_rect.y0 - c_rect.y0) < 10:
                matched_bar = tb
                break
        c["title_bar"] = matched_bar

    return {
        "wide_bars": wide_bars,
        "cards": sorted_cards
    }
