import pymupdf
import re
import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

DOCS = [
    ('政治解题方法一页纸1-4答案.pdf', 1),
    ('政治解题方法一页纸 5-10答案.pdf', 2)
]

os.makedirs('public/images/solve', exist_ok=True)

# Method metadata definitions
METHODS_CONFIG = [
    {
        "id": "absolute",
        "name": "绝对极端说法",
        "mnemonic": "唯一一切与任何，始终没有或只能，必然绝对定为错",
        "keywords": ["唯一", "一切", "任意", "始终", "没有", "时时", "不再", "绝对", "一定", "单纯", "只能"],
        "description": "命题人常用过于武断、绝对化的极端词制造干扰项。在真题中带有此类极端词汇的选项绝大多数为错误选项。"
    },
    {
        "id": "tense",
        "name": "时态问题",
        "mnemonic": "完成时态常有诈，正在进行说完成，早已开始说靠后",
        "keywords": ["已经", "开始", "全面建成", "早已", "尚未", "正在"],
        "description": "主要考完成时态相关：将正在进行的事情说成已完成，或将历史上早已完成的改革/事件移花接木，盯紧'已经'、'开始'。"
    },
    {
        "id": "exaggerate",
        "name": "夸张",
        "mnemonic": "小切口解决大根本，无中生有帽子大，作用夸大是陷阱",
        "keywords": ["根本", "取代", "彻底", "压倒性", "决定性", "引擎", "最"],
        "description": "程度出错、夸大作用。比如把本不属于某事物的地位强加于它，或用某个微观小切口措施声称'彻底根本解决'顽疾。"
    },
    {
        "id": "irrelevant",
        "name": "不合题意",
        "mnemonic": "驴头不对马嘴，说法虽对不对题，答非所问直接切",
        "keywords": ["无关", "不合题意", "目标不一致", "偷换主体", "混淆时段"],
        "description": "选项本身表述或许正确，但与题干主旨、设问角度或时间段完全不相关，或选项动作与题干核心目标南辕北辙。"
    },
    {
        "id": "hedge",
        "name": "对冲命题",
        "mnemonic": "题干向东选项向西，反向对着干必错",
        "keywords": ["方向相反", "对冲", "逆向", "矛盾"],
        "description": "题干给出的主旨方向与选项给出的政策/理论取向完全相反，形成对冲，该选项必错。"
    },
    {
        "id": "foreign",
        "name": "国内上升到国外",
        "mnemonic": "国内内政莫扯外，除非考查成就大，国际地位才上升",
        "keywords": ["国际", "国外", "全球", "人类命运共同体", "世界通用"],
        "description": "题干考查我国国内制度与内政，选项却无端上升到国际层面（通常排除）。特例：考查社会主义伟大建设成就时，提升国际影响力为正确项。"
    },
    {
        "id": "us_related",
        "name": "美国相关",
        "mnemonic": "美帝本质为私利，中美关系多微妙，结伴而不称盟友",
        "keywords": ["美国", "霸权", "自身利益", "微妙", "对话不对抗"],
        "description": "命题人考察美国对外政策或中美关系时，牢记两点：1. 美国对外行为根本上是为了维护自身霸权私利；2. 中美关系微妙复杂，对话而不对抗。"
    },
    {
        "id": "idealism",
        "name": "唯心",
        "mnemonic": "主观臆断想决定，意识作用莫吹大，客观规律不可违",
        "keywords": ["意识决定", "主观联想", "心态决定", "唯心", "主观决定客观"],
        "description": "经典的马原哲学挖坑手法：违背唯物主义，把主观意识的作用无限夸大为决定客观物质世界。"
    },
    {
        "id": "target",
        "name": "盯住目标",
        "mnemonic": "三项解题法，题干核心词，精准连线选项词",
        "keywords": ["盯住目标", "三项解题法", "对应", "核心词"],
        "description": "三项解题法之盯住目标：牢牢锁定题干的关键提问词（如'传播'、'制裁'、'服务'），直接在选项中定位同义复现或高契合词。"
    },
    {
        "id": "others",
        "name": "其他(综合名言墓碑词)",
        "mnemonic": "马恩列原话多抽象，莫当错误盲目排，墓碑词前需三思",
        "keywords": ["名言", "引用", "墓碑词", "观念", "一脉相承", "自发", "自主"],
        "description": "综合命题手法：包含马恩列抽象名言识别、高频墓碑干扰词（自发、自主、一脉相承等），需冷静分析句意逻辑。"
    }
]

# Method to question IDs mapping from docs/solve-method-plan.md
METHOD_QIDS = {
    "absolute": ["2020.31", "2020.18", "2021.3", "2021.4", "2022.2", "2023.22", "2023.26", "2023.30", "2024.22", "2023.31", "2024.18"],
    "tense": ["2018.26", "2020.22", "2021.2", "2021.23", "2024.16", "2019.29", "2023.9", "2021.27"],
    "exaggerate": ["2010.18", "2021.33", "2022.22", "2023.24", "2022.18", "2024.26", "2024.33", "2020.29", "2023.17"],
    "irrelevant": ["2024.12", "2022.29", "2021.22", "2020.28", "2024.28", "2021.24", "2021.25", "2022.17", "2020.19", "2022.8"],
    "hedge": ["2022.21", "2022.25", "2024.30", "2023.33", "2022.33"],
    "foreign": ["2017.32", "2019.22", "2019.25", "2019.30", "2021.31", "2021.29"],
    "us_related": ["2020.16", "2022.33"],
    "idealism": ["2022.20", "2020.17", "2024.1", "2022.19", "2024.17"],
    "target": ["2022.16", "2022.8", "2024.13", "2021.16"],
    "others": ["2018.20", "2022.4", "2020.26", "2022.12", "2024.21", "2024.25", "2020.27", "2016.14", "2024.14", "2023.25"]
}

print("Methods configured:", len(METHODS_CONFIG))
all_mapped_qids = set()
for qlist in METHOD_QIDS.values():
    all_mapped_qids.update(qlist)
print("Total unique question IDs in plan:", len(all_mapped_qids))

def extract_all_questions_and_images():
    results = {}
    
    for pdf_name, doc_idx in DOCS:
        doc = pymupdf.open(pdf_name)
        page = doc[0]
        blocks = page.get_text('blocks')
        img_infos = [info for info in page.get_image_info() if info['width'] > 300]
        
        # Sort question blocks
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
                
        for q in q_blocks:
            qid = q['id']
            qx0, qy0, qx1, qy1 = q['bbox']
            
            # Find image(s) right below question block
            # For 2020.29 there are 2 images (stem + options)
            cand_imgs = []
            for img in img_infos:
                ix0, iy0, ix1, iy1 = img['bbox']
                x_dist = abs(ix0 - qx0)
                y_diff = iy0 - qy1
                if x_dist < 60 and -20 < y_diff < 120:
                    cand_imgs.append((y_diff, x_dist, img))
            cand_imgs.sort(key=lambda x: x[0])
            
            # If 2020.29, take top 2 images
            matched_imgs = []
            if qid == '2020.29' and len(cand_imgs) >= 2:
                matched_imgs = [cand_imgs[0][2], cand_imgs[1][2]]
            elif cand_imgs:
                matched_imgs = [cand_imgs[0][2]]
                
            # Compute union bbox of images to crop high-res pixmap
            if matched_imgs:
                ux0 = min(img['bbox'][0] for img in matched_imgs)
                uy0 = min(img['bbox'][1] for img in matched_imgs)
                ux1 = max(img['bbox'][2] for img in matched_imgs)
                uy1 = max(img['bbox'][3] for img in matched_imgs)
                
                # Render crisp image at 300 DPI
                clip = pymupdf.Rect(ux0, uy0, ux1, uy1)
                pix = page.get_pixmap(clip=clip, dpi=300)
                out_path = f"public/images/solve/{qid}.png"
                pix.save(out_path)
                image_rel_path = f"images/solve/{qid}.png"
            else:
                image_rel_path = ""
                
            # Extract teacher's tip/explanation below image
            target_y = uy1 if matched_imgs else qy1
            target_x = qx0
            exp_lines = []
            for b in blocks:
                bx0, by0, bx1, by1 = b[:4]
                bt = b[4].strip()
                if re.match(r'^20\d\d\.\d+', bt):
                    continue
                # Block directly below the image
                if abs(bx0 - target_x) < 70 and 0 <= (by0 - target_y) < 70:
                    exp_lines.append(bt)
            
            tip_raw = "\n".join(exp_lines).strip()
            
            # Parse answer from tip_raw
            # Patterns: "选D", "选AB", "选ABD", "选BCD", "排除BD选AC", "排除C选ABD", "选B", "ABCD"
            answer = []
            # Check for patterns
            ans_m = re.search(r'(?:选|all in\s*)([A-D]{1,4})', tip_raw)
            if ans_m:
                answer = list(ans_m.group(1))
            elif "ABCD" in tip_raw:
                answer = ["A", "B", "C", "D"]
            elif "排除C" in tip_raw and "ABD" in tip_raw:
                answer = ["A", "B", "D"]
                
            # Question type: 1~16 is single, 17~33 is multi
            year_str, no_str = qid.split('.')
            year = int(year_str)
            no = int(no_str)
            q_type = "single" if no <= 16 else "multi"
            
            # Map methods
            q_methods = []
            for mid, qids in METHOD_QIDS.items():
                if qid in qids:
                    q_methods.append(mid)
            if not q_methods:
                q_methods = ["others"]
                
            results[qid] = {
                'id': qid,
                'year': year,
                'no': no,
                'type': q_type,
                'methods': q_methods,
                'tip': tip_raw,
                'answer': answer,
                'image': image_rel_path
            }
            
    return results

questions_meta = extract_all_questions_and_images()
print("Questions extracted:", len(questions_meta))
answered_count = sum(1 for q in questions_meta.values() if q['answer'])
print(f"Answers parsed from tips: {answered_count} / {len(questions_meta)}")
for qid, q in sorted(questions_meta.items()):
    if not q['answer']:
        print(f"Missing answer in tip for {qid}: {repr(q['tip'])}")
