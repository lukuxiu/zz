import re

# 关键词重点颜色集合
KEYWORD_COLORS = {
    0x9fff,    # 青蓝色重点
    0x2000ff,  # 深蓝色重点
    0xff0000,  # 红色核心重点
    0xff6000,  # 橙色重点
    0x275bd1,  # 天蓝重点
    0xd16056,  # 红褐色重点
    0x40ff,    # 亮青紫
    0xdc7705,  # 橙黄
    0x8000ff,  # 紫色重点
    0x6783cf,  # 浅蓝紫
    0xff00bf,  # 洋红
    0xeb9e27,  # 明黄
    0xdf00ff,  # 粉紫
    0x20ff00,  # 亮绿
    0x36b59d   # 青色
}

# 弱化文字颜色（绝对禁止作为重点关键词）
MUTED_COLORS = {
    0xaaaaaa
}

# 标点集合（截断关键词边界）
PUNCTUATION = set("，。！？；：、‘’“”\"'()（）《》【】—…")

def process_spans_to_content(spans):
    """
    遍历有序文本spans，提取：
    1. content: 带有 {{关键词}} 标记的完整文本
    2. keywords: 重点词对象列表 [{word, color, colorHex}]
    3. contentHtml: 带有 span class 的富文本结构
    4. rawText: 纯文本拼接
    """
    raw_text = ""
    content_parts = []
    html_parts = []
    keywords = []

    # 先将相邻相同颜色且均为重点色的span进行初步合并，但不跨越换行和标点
    for s in spans:
        text = s.get("text", "")
        if not text:
            continue
        raw_text += text
        color = s.get("color", 0)
        color_hex = f"#{color:06x}" if isinstance(color, int) else str(color)

        if color in MUTED_COLORS:
            # 弱化文字：绝不标记为重点，只在html中添加muted类
            content_parts.append(text)
            html_parts.append(f'<span class="muted-text" style="color:#aaaaaa;opacity:0.75;">{text}</span>')
        elif color in KEYWORD_COLORS:
            # 重点彩色词：按标点符号分割，保证标点不被包进关键词
            segments = []
            cur = ""
            for ch in text:
                if ch in PUNCTUATION or ch.isspace():
                    if cur:
                        segments.append((True, cur))
                        cur = ""
                    segments.append((False, ch))
                else:
                    cur += ch
            if cur:
                segments.append((True, cur))

            for is_kw, seg in segments:
                if is_kw and seg.strip():
                    content_parts.append(f"{{{{{seg}}}}}")
                    html_parts.append(f'<span class="keyword" style="color:{color_hex};font-weight:bold;">{seg}</span>')
                    keywords.append({
                        "word": seg,
                        "color": color_hex,
                        "colorInt": color
                    })
                else:
                    content_parts.append(seg)
                    html_parts.append(seg)
        else:
            # 普通文字（0x555555, 0x5d5d5d, 0x000000 等）
            content_parts.append(text)
            html_parts.append(text)

    content = "".join(content_parts)
    content_html = "".join(html_parts)

    return {
        "rawText": raw_text.strip(),
        "content": content.strip(),
        "contentHtml": f"<p>{content_html.strip()}</p>",
        "keywords": keywords
    }
