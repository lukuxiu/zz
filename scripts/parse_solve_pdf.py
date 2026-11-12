import pymupdf
import re
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

def analyze_pdf(pdf_path):
    doc = pymupdf.open(pdf_path)
    page = doc[0]
    
    # 1. Text blocks
    blocks = page.get_text('blocks')
    
    # 2. Images with bbox
    img_infos = [info for info in page.get_image_info() if info['width'] > 300]
    
    # Find all question blocks
    q_blocks = []
    for b in blocks:
        t = b[4].strip()
        m = re.match(r'^(20\d\d\.\d+)', t)
        if m:
            qid = m.group(1)
            q_blocks.append({
                'id': qid,
                'bbox': b[:4],
                'text': t
            })
            
    print(f"File {pdf_path}: found {len(q_blocks)} question blocks, {len(img_infos)} large images")
    
    # Pair each question with closest image below it
    pairs = []
    for q in q_blocks:
        qx0, qy0, qx1, qy1 = q['bbox']
        # Find image whose x is close to qx0, and y0 is right after qy1 (within ~60pt)
        cand_imgs = []
        for img in img_infos:
            ix0, iy0, ix1, iy1 = img['bbox']
            # x overlap or proximity
            x_dist = abs(ix0 - qx0)
            y_diff = iy0 - qy1
            if x_dist < 60 and -20 < y_diff < 80:
                cand_imgs.append((y_diff, x_dist, img))
        cand_imgs.sort(key=lambda x: (x[0], x[1]))
        best_img = cand_imgs[0][2] if cand_imgs else None
        
        # Also find explanation text block below or next to the image
        # If best_img found, look for text blocks below best_img
        exp_text = []
        target_y = best_img['bbox'][3] if best_img else qy1
        target_x = qx0
        for b in blocks:
            bx0, by0, bx1, by1 = b[:4]
            bt = b[4].strip()
            if re.match(r'^20\d\d\.\d+', bt):
                continue
            # Check if this block is right below the image / question
            if abs(bx0 - target_x) < 70 and 0 <= (by0 - target_y) < 60:
                exp_text.append(bt)
                
        pairs.append({
            'id': q['id'],
            'q_bbox': q['bbox'],
            'has_img': best_img is not None,
            'img_bbox': best_img['bbox'] if best_img else None,
            'img_num': best_img['number'] if best_img else None,
            'explanation': '\n'.join(exp_text)
        })
        
    return pairs

p1 = analyze_pdf('政治解题方法一页纸1-4答案.pdf')
p2 = analyze_pdf('政治解题方法一页纸 5-10答案.pdf')

print("P1 matched:", sum(1 for p in p1 if p['has_img']), "/", len(p1))
print("P2 matched:", sum(1 for p in p2 if p['has_img']), "/", len(p2))

# Check any unmatched
for p in p1 + p2:
    if not p['has_img']:
        print("Unmatched question img:", p['id'], p['q_bbox'])
