import os
import re
import json
import easyocr
import sys

sys.stdout.reconfigure(encoding='utf-8')

reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)

def parse_ocr_lines_to_question(lines):
    # lines is a list of strings
    full_text = "\n".join(lines)
    
    stem_lines = []
    options = {'A': '', 'B': '', 'C': '', 'D': ''}
    current_opt = None
    
    # Regex to detect option start
    # e.g., A. A、 A_ A: (A) A
    opt_start_pattern = re.compile(r'^[\[\(（【]?([A-D])[\]\)）】\.\、\:\_\s\-]+(.*)$')
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        m = opt_start_pattern.match(line_clean)
        if m:
            current_opt = m.group(1).upper()
            opt_rest = m.group(2).strip()
            options[current_opt] = opt_rest
        elif current_opt:
            options[current_opt] += " " + line_clean
        else:
            stem_lines.append(line_clean)
            
    stem = "".join(stem_lines).strip()
    
    # Clean up options
    for k in ['A', 'B', 'C', 'D']:
        options[k] = options[k].strip()
        
    return stem, options

def main():
    img_dir = 'public/images/solve'
    images = sorted([f for f in os.listdir(img_dir) if f.endswith('.png')])
    print(f"Total images to OCR: {len(images)}")
    
    ocr_results = {}
    for idx, img_file in enumerate(images):
        qid = img_file.replace('.png', '')
        img_path = os.path.join(img_dir, img_file)
        
        try:
            raw_lines = reader.readtext(img_path, detail=0)
            stem, options = parse_ocr_lines_to_question(raw_lines)
            
            # Check completeness
            has_all_opts = all(bool(options[k]) for k in ['A', 'B', 'C', 'D'])
            has_stem = len(stem) > 5
            needs_review = not (has_all_opts and has_stem)
            
            ocr_results[qid] = {
                'stem': stem,
                'options': options,
                'raw_lines': raw_lines,
                'needsReview': needs_review
            }
            status_char = "OK" if not needs_review else "REVIEW"
            print(f"[{idx+1}/{len(images)}] {qid} -> {status_char} (stem len: {len(stem)}, opts: {[k for k in ['A','B','C','D'] if options[k]]})")
        except Exception as e:
            print(f"[{idx+1}/{len(images)}] {qid} -> ERROR: {e}")
            ocr_results[qid] = {
                'stem': '',
                'options': {'A': '', 'B': '', 'C': '', 'D': ''},
                'raw_lines': [],
                'needsReview': True
            }
            
    with open('data/raw_ocr_questions.json', 'w', encoding='utf-8') as f:
        json.dump(ocr_results, f, ensure_ascii=False, indent=2)
    print("Done OCR! Saved to data/raw_ocr_questions.json")

if __name__ == '__main__':
    main()
