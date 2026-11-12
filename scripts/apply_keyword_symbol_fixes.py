import json, re, shutil, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

# 1. Symbol Mapping definition
from scripts.modules.symbol_mapper import EXACT_SYMBOL_MAP

SYMBOL_MAP = {}
for h, info in EXACT_SYMBOL_MAP.items():
    ch = info['char']
    if ch.startswith('{') and ch.endswith('}'):
        clean_name = ch[1:-1]
        SYMBOL_MAP[clean_name] = {
            'hash': h,
            'desc': info['desc'],
            'type': info['type']
        }

# 2. Card-specific overrides from handoff suggestions
card_overrides = {
    'kp-002-01': [
        ('{{科}}{{学性与革}}{{命}}{{性的统一}}（{{科}}{{命}}）', '{{科学性}}与{{革命性}}的统一（{{科}}{{命}}）'),
        ('“{{彳亍}}”', '“{{彳亍}}”（行）')
    ],
    'kp-003-01': [
        ('{{政治法律思}}{{想}}', '{{政治法律思想}}')
    ],
    'kp-005-01': [
        ('{{劳}}{{动}}{{二}}{{重性理论}}', '{{劳动二重性理论}}')
    ],
    'kp-010-01': [
        ('{{价}}{{值}}{{寓}}{{于使用价值之中}}', '{{价值}}寓于{{使用价值}}之中'),
        ('{{必}}{{然性}}{{寓}}{{于偶然性之中}}', '{{必然性}}寓于{{偶然性}}之中'),
        ('{{斗}}{{争性}}{{寓}}{{于同一性之中}}', '{{斗争性}}寓于{{同一性}}之中'),
        ('{{绝}}{{对性}}{{寓}}{{于相对性质中}}', '{{绝对性}}寓于{{相对性}}之中'),
        ('{{普}}{{遍性}}{{寓}}{{于特殊性之中}}', '{{普遍性}}寓于{{特殊性}}之中'),
        ('{{共}}{{性}}{{寓}}{{于个性之中}}', '{{共性}}寓于{{个性}}之中'),
    ],
    'kp-044-01': [
        ('{{批}}判{{孔}}学，是为了给中国{{发}}展{{资}}本主义扫清障碍，{{但}}{{没彻底否定孔学的历史作用}}',
         '批判孔学，是为了给中国发展资本主义扫清障碍，{{但没彻底否定孔学的历史作用}}'),
        ('{{社}}{{会主义}}', '{{社会主义}}')
    ],
    'kp-054-01': [
        ('{{发}}{{端于}}{{南}}{{昌起义}}', '{{发端于南昌起义}}'),
        ('{{奠}}{{基}}{{于三}}{{湾}}{{改编}}', '{{奠基于三湾改编}}'),
        ('{{定}}{{型于}}{{古}}{{田会议}}', '{{定型于古田会议}}')
    ],
    'kp-067-01': [
        ('方{{法}}：\n{{说}}{{服教育}} {{典型示范和国家帮助}}', '方法：\n{{说服教育}}、{{典型示范和国家帮助}}'),
        ('{{方}}{{针}}：\n{{积极}}{{领导}} {{稳}}{{步前进}}', '方针：\n{{积极领导}}、{{稳步前进}}')
    ]
}

def merge_adjacent_braces(text):
    prev = ""
    curr = text
    while curr != prev:
        prev = curr
        curr = re.sub(r'\{\{([^{}\n]+)\}\}\{\{([^{}\n]+)\}\}', r'{{\1\2}}', curr)
    return curr

# Read knowledge.json
with open('data/knowledge.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

records = data['records']
modified_count = 0
diff_log = []

for r in records:
    cid = r['id']
    old_content = r['content']
    new_content = old_content
    
    # 1. Apply overrides
    if cid in card_overrides:
        for target, repl in card_overrides[cid]:
            if target in new_content:
                new_content = new_content.replace(target, repl)
            else:
                print(f"Notice: target not in {cid}: {target}")
                
    # 2. Merge adjacent braces
    new_content = merge_adjacent_braces(new_content)
    
    # 3. Add mnemonic for kp-002-01 if empty
    if cid == 'kp-002-01' and not r.get('mnemonics'):
        r['mnemonics'] = [{'text': '科学性与革命性的统一（科命）'}]

    # Update fields if changed or if symbols need rendering in contentHtml
    has_symbols = bool(re.search(r'(?<!\{)\{([^{}\n]+)\}(?!\})', new_content))
    if new_content != old_content or has_symbols or '<img' not in r.get('contentHtml', ''):
        modified_count += 1
        diff_log.append((cid, r['title'], old_content, new_content))
        r['content'] = new_content
        
        # Build color lookup from old keywords
        color_map = {}
        for kw in r.get('keywords', []):
            color_map[kw['word']] = kw['color']
            
        # Re-extract keywords
        cloze_words = re.findall(r'\{\{([^{}]+)\}\}', new_content)
        new_keywords = []
        for w in cloze_words:
            c = color_map.get(w)
            if not c:
                for old_w, old_c in color_map.items():
                    if old_w in w or w in old_w:
                        c = old_c
                        break
            if not c:
                c = '#2000ff'
            c_int = int(c.lstrip('#'), 16) if c.startswith('#') and len(c) == 7 else 2097407
            new_keywords.append({'word': w, 'color': c, 'colorInt': c_int})
            
        r['keywords'] = new_keywords
        
        # Rebuild contentHtml:
        # First split into lines to maintain newline structure
        lines = new_content.split('\n')
        html_lines = []
        for line in lines:
            line_html = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            # Replace keywords
            def replace_kw(m):
                word = m.group(1)
                color = color_map.get(word, '#2000ff')
                return f'<span class="keyword" style="color:{color};font-weight:bold;">{word}</span>'
            line_html = re.sub(r'\{\{([^{}]+)\}\}', replace_kw, line_html)
            
            # Replace symbols like {直升机}
            def replace_sym(m):
                sym_name = m.group(1)
                if sym_name in SYMBOL_MAP:
                    s_info = SYMBOL_MAP[sym_name]
                    return f'<span class="symbol-sticker" title="{s_info["desc"]}"><img src="/symbols/{s_info["hash"]}.png" alt="{s_info["desc"]}" class="symbol-sticker-img" /></span>'
                return m.group(0)
            line_html = re.sub(r'(?<!\{)\{([^{}\n]+)\}(?!\})', replace_sym, line_html)
            html_lines.append(line_html)
            
        r['contentHtml'] = '<p>' + '\n'.join(html_lines) + '</p>'
        
        # Rebuild rawText
        # Strip {{ }} and replace {symbol} with [symbol]
        raw = re.sub(r'\{\{([^{}]+)\}\}', r'\1', new_content)
        raw = re.sub(r'(?<!\{)\{([^{}\n]+)\}(?!\})', r'[\1]', raw)
        r['rawText'] = raw

print(f"Processed records. Total updated cards: {modified_count}")

# Write back to data/knowledge.json
with open('data/knowledge.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Successfully written to data/knowledge.json")

# Also sync to public/data/knowledge.json
shutil.copyfile('data/knowledge.json', 'public/data/knowledge.json')
print("Successfully synced to public/data/knowledge.json")
