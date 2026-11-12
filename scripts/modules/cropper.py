import os
import pymupdf

def crop_card_image(page, bbox, output_path, dpi=200):
    """
    根据卡片 bbox [x0, y0, x1, y1] 从页面渲染并裁切高清卡片原图
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 增加微小内边距保护，防止裁切到边框线条，同时避免包含相邻卡片
    x0, y0, x1, y1 = bbox
    clip_rect = pymupdf.Rect(max(0, x0 - 1.5), max(0, y0 - 1.5), min(page.rect.width, x1 + 1.5), min(page.rect.height, y1 + 1.5))
    
    # 高清渲染 (dpi=200 保证清晰度且文件大小适中)
    pix = page.get_pixmap(dpi=dpi, clip=clip_rect)
    pix.save(output_path)
    
    # 检查图片有效性
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        raise RuntimeError(f"Failed to generate crop image: {output_path}")
        
    return output_path
