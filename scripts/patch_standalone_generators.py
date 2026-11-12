# -*- coding: utf-8 -*-
"""
更新并增强单文件发布版生成脚本：
1. 解除手机端缩放限制 (minimum-scale=1.0, maximum-scale=5.0, user-scalable=yes)
2. 内嵌全部 39 种原书趣味小图 (Base64) 确保离线渲染
3. 在 CardViewerComponent 中以行内小图 + 描述 tooltip 渲染 {直升机}、{鸡}、{国旗} 等符号
4. 挖空/遮挡模式下保留图标作线索，不挖空
"""

import os
import re

# 1. 趣味小图精确MD5与描述定义
SYMBOL_MAP_JS = """
    // 39种原书趣味小图精确MD5哈希与描述映射表
    const SYMBOL_MAP = {
      '直升机': { hash: '0516485bd1dce29f34fa082d19c8a898', desc: '牢二枢纽直升机' },
      '鸡': { hash: '5a9490a12d44beb9e7746e1a94426828', desc: '偷鸡心虚虚空鸡' },
      '俄国国旗': { hash: 'e380284efa1fbd56310cd5f8f4fcfe1d', desc: '十月革命俄国国旗' },
      '人像': { hash: '168dcc0bc57d714b82bfe6874f43e862', desc: '历史人物图标' },
      '帽子人物': { hash: '40aaf32abfc71ea9500e34c32d8d20e5', desc: '国际寡妇助记' },
      '生子': { hash: '6cb1e12616262e72dadbc1257ec66830', desc: '生孩子助记' },
      '机器多了': { hash: '940abc17f526e6beac695add820827ae', desc: '技术构成机器多' },
      '工人少了': { hash: 'fdf97e4e7d1a6bea4fd877d0e40d31c7', desc: '有机构成工人少' },
      '威海技师': { hash: '7057fa3e3ce5ecba32cac43eb4565e73', desc: '威海技师洋务' },
      '工农革命旗': { hash: '5f2f87becb22c2ab56431d205ab73ab3', desc: '秋收起义旗帜' },
      '民主政权标': { hash: '87dd47b6f4ca93850f0130dc659c77a0', desc: '赞成抗日民主' },
      '著作:书标': { hash: '99386d902eb6272b3c82bc3a6e1e022f', desc: '毛泽东著作标志' },
      '著作:飞标': { hash: '12d6fc3c71073f73b549fd983c0c7f88', desc: '论联合政府标志' },
      '著作:章标': { hash: 'cd54f7c7ed776f063a883f04b9aa270a', desc: '毛泽东著作奖章' },
      '高质量发展标': { hash: '5b175efae41e61ff41f9a7e91b6e8ccb', desc: '高质量发展' },
      '全面依法治国标': { hash: '34df7d1a3b49696a8c06d78d0079121c', desc: '全面依法治国' },
      '变动标': { hash: 'b7e1a94be66a6858d0f7db1457cc7ce0', desc: '构成变动' },
      '发展标': { hash: 'e4fa63d9756f3f7ae302ec676fabf054', desc: '继续发展' }
    };

    function getSymbolInfo(name, cardSymbols) {
      if (SYMBOL_MAP[name]) return SYMBOL_MAP[name];
      if (cardSymbols) {
        const found = cardSymbols.find(s => s.char === '{' + name + '}' || s.char === name);
        if (found) return found;
      }
      return null;
    }
"""

SYMBOL_CSS = """
    .symbol-chip {
      display: inline-flex; align-items: center; gap: 3px; background: #fef08a; border: 1px solid #facc15; color: #854d0e;
      font-size: 0.85em; font-weight: 700; padding: 1px 6px; border-radius: 4px; margin: 0 3px; vertical-align: middle;
      cursor: pointer; user-select: none; transition: transform 0.15s, background-color 0.15s;
    }
    .symbol-chip:hover { background: #fde047; transform: scale(1.05); }
    .symbol-icon-img { width: 1.25em; height: 1.25em; vertical-align: -0.22em; object-fit: contain; display: inline-block; }
    .symbol-caption { font-size: 0.88em; }
"""

def patch_file(filepath, is_lite=False):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 解除缩放限制
    content = content.replace(
        'content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover"',
        'content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=5.0, user-scalable=yes, viewport-fit=cover"'
    )

    # 2. 注入 symbols 嵌入逻辑
    if "public/symbols/*.*" not in content:
        embed_symbols_code = """
import base64
import glob

print("Embedding symbols into standalone HTML...")
image_b64_map = {}
for p in glob.glob("public/symbols/*.*"):
    rel = os.path.relpath(p, "public").replace("\\\\", "/")
    ext = "jpeg" if p.lower().endswith((".jpg", ".jpeg")) else "png"
    with open(p, "rb") as img_f:
        image_b64_map[rel] = f"data:image/{ext};base64," + base64.b64encode(img_f.read()).decode("ascii")
images_json_str = json.dumps(image_b64_map, ensure_ascii=False)
"""
        content = re.sub(r'(records_json_str = json\.dumps\(.*?\))', r'\1' + embed_symbols_code, content, count=1)
        if ".replace(\"__ALL_IMAGES_JSON__\", images_json_str)" not in content:
            content = content.replace(
                '.replace("__ALL_MINDSETS_JSON__", mindsets_json_str)',
                '.replace("__ALL_MINDSETS_JSON__", mindsets_json_str)\n    .replace("__ALL_IMAGES_JSON__", images_json_str)'
            )

    # 3. 增强 CSS
    if ".symbol-icon-img" not in content:
        content = re.sub(r'\.symbol-chip\s*\{[^}]*\}', SYMBOL_CSS.strip(), content)

    # 4. 注入全局 resolveImageUrl 与 SYMBOL_MAP
    if "const ALL_EMBEDDED_IMAGES = __ALL_IMAGES_JSON__;" not in content:
        js_head = """
    const ALL_EMBEDDED_IMAGES = __ALL_IMAGES_JSON__;
    function resolveImageUrl(imgRelPath) {
      if (!imgRelPath) return '';
      const cleanKey = imgRelPath.replace(/^[\\\\/]+/, '').replace(/^public[\\\\/]+/, '');
      if (ALL_EMBEDDED_IMAGES && ALL_EMBEDDED_IMAGES[cleanKey]) {
        return ALL_EMBEDDED_IMAGES[cleanKey];
      }
      return cleanKey;
    }
""" + SYMBOL_MAP_JS
        content = content.replace("const ALL_CARDS = __ALL_CARDS_JSON__;", js_head + "\n    const ALL_CARDS = __ALL_CARDS_JSON__;")

    # 5. 更新 parseMnemonicParts 与 parsedSegments
    old_parse_mnemonic = """        function parseMnemonicParts(text) {
          if (!text) return [];
          const parts = [];
          const regex = /\\{([^}]+)\\}/g;
          let lastIdx = 0;
          let match;
          while ((match = regex.exec(text)) !== null) {
            if (match.index > lastIdx) {
              parts.push({ type: 'text', text: text.substring(lastIdx, match.index) });
            }
            parts.push({ type: 'symbol', text: match[1] });
            lastIdx = regex.lastIndex;
          }
          if (lastIdx < text.length) {
            parts.push({ type: 'text', text: text.substring(lastIdx) });
          }
          return parts;
        }"""

    new_parse_mnemonic = """        function parseMnemonicParts(text) {
          if (!text) return [];
          const parts = [];
          const regex = /\\{([^}]+)\\}/g;
          let lastIdx = 0;
          let match;
          while ((match = regex.exec(text)) !== null) {
            if (match.index > lastIdx) {
              parts.push({ type: 'text', text: text.substring(lastIdx, match.index) });
            }
            const sName = match[1];
            const sInfo = getSymbolInfo(sName, props.card ? props.card.symbols : null);
            parts.push({
              type: 'symbol',
              text: sName,
              hash: sInfo ? sInfo.hash : null,
              desc: sInfo ? sInfo.desc : sName
            });
            lastIdx = regex.lastIndex;
          }
          if (lastIdx < text.length) {
            parts.push({ type: 'text', text: text.substring(lastIdx) });
          }
          return parts;
        }"""

    if old_parse_mnemonic in content:
        content = content.replace(old_parse_mnemonic, new_parse_mnemonic)

    # 6. 更新 parsedSegments 识别行内趣味小图
    old_parsed_segments = """        const parsedSegments = computed(() => {
          if (!props.card || !props.card.content) return [];
          const content = props.card.content;
          const segments = [];
          const regex = /\\{\\{([^}]+)\\}\\}/g;
          let lastIndex = 0;
          let match;
          let idx = 0;

          const colorMap = new Map();
          if (props.card.keywords) {
            props.card.keywords.forEach(k => colorMap.set(k.word, k.color));
          }

          while ((match = regex.exec(content)) !== null) {
            if (match.index > lastIndex) {
              const txt = content.substring(lastIndex, match.index);
              segments.push({ id: 'p-' + idx++, type: 'plain', text: txt });
            }
            const kw = match[1];
            const segId = 'kw-' + idx++;
            const shouldCloze = props.mode === 'keyword' || (props.mode === 'random' && idx % 2 === 0);
            segments.push({
              id: segId,
              type: 'keyword',
              text: kw,
              color: colorMap.get(kw) || '#2e6297',
              shouldCloze: shouldCloze,
              revealed: revealedSet.value.has(segId)
            });
            lastIndex = regex.lastIndex;
          }

          if (lastIndex < content.length) {
            segments.push({ id: 'p-' + idx++, type: 'plain', text: content.substring(lastIndex) });
          }
          return segments;
        });"""

    new_parsed_segments = """        const parsedSegments = computed(() => {
          if (!props.card || !props.card.content) return [];
          const content = props.card.content;
          const segments = [];
          const regex = /\\{\\{([^}]+)\\}\\}/g;
          let lastIndex = 0;
          let match;
          let idx = 0;

          const colorMap = new Map();
          if (props.card.keywords) {
            props.card.keywords.forEach(k => colorMap.set(k.word, k.color));
          }

          function addNonKw(txt) {
            const symRegex = /\\{([^{}\\n]+)\\}/g;
            let lastSym = 0;
            let sMatch;
            while ((sMatch = symRegex.exec(txt)) !== null) {
              if (sMatch.index > lastSym) {
                segments.push({ id: 'p-' + idx++, type: 'plain', text: txt.substring(lastSym, sMatch.index) });
              }
              const sName = sMatch[1];
              const sInfo = getSymbolInfo(sName, props.card ? props.card.symbols : null);
              if (sInfo) {
                segments.push({
                  id: 'sym-' + idx++,
                  type: 'symbol',
                  name: sName,
                  hash: sInfo.hash,
                  desc: sInfo.desc,
                  shouldCloze: false
                });
              } else {
                segments.push({ id: 'p-' + idx++, type: 'plain', text: sMatch[0] });
              }
              lastSym = symRegex.lastIndex;
            }
            if (lastSym < txt.length) {
              segments.push({ id: 'p-' + idx++, type: 'plain', text: txt.substring(lastSym) });
            }
          }

          while ((match = regex.exec(content)) !== null) {
            if (match.index > lastIndex) {
              addNonKw(content.substring(lastIndex, match.index));
            }
            const kw = match[1];
            const segId = 'kw-' + idx++;
            const shouldCloze = props.mode === 'keyword' || (props.mode === 'random' && idx % 2 === 0);
            segments.push({
              id: segId,
              type: 'keyword',
              text: kw,
              color: colorMap.get(kw) || '#2e6297',
              shouldCloze: shouldCloze,
              revealed: revealedSet.value.has(segId)
            });
            lastIndex = regex.lastIndex;
          }

          if (lastIndex < content.length) {
            addNonKw(content.substring(lastIndex));
          }
          return segments;
        });"""

    if old_parsed_segments in content:
        content = content.replace(old_parsed_segments, new_parsed_segments)

    # 7. 更新 template 中的渲染
    old_tmpl_kw = """                <span v-if="seg.type === 'keyword'"
                  :class="[seg.shouldCloze ? (revealedSet.has(seg.id) ? 'cloze-revealed' : 'cloze-hidden') : 'keyword-highlight']"
                  :style="(!seg.shouldCloze || revealedSet.has(seg.id)) ? { color: seg.color, '--kw-color': seg.color } : {}"
                  @click="toggleSeg(seg)">
                  {{ seg.text }}
                </span>
                <span v-else>{{ seg.text }}</span>"""

    new_tmpl_kw = """                <span v-if="seg.type === 'keyword'"
                  :class="[seg.shouldCloze ? (revealedSet.has(seg.id) ? 'cloze-revealed' : 'cloze-hidden') : 'keyword-highlight']"
                  :style="(!seg.shouldCloze || revealedSet.has(seg.id)) ? { color: seg.color, '--kw-color': seg.color } : {}"
                  @click="toggleSeg(seg)">
                  {{ seg.text }}
                </span>
                <span v-else-if="seg.type === 'symbol'" class="symbol-chip" :title="seg.desc">
                  <img v-if="seg.hash" :src="resolveImageUrl('symbols/' + seg.hash + '.png')" :alt="seg.name" class="symbol-icon-img" />
                  <span class="symbol-caption">{{ seg.name }}</span>
                </span>
                <span v-else>{{ seg.text }}</span>"""

    if old_tmpl_kw in content:
        content = content.replace(old_tmpl_kw, new_tmpl_kw)

    old_tmpl_mne = """                  <template v-for="(part, pIdx) in parseMnemonicParts(m.text)" :key="pIdx">
                    <span v-if="part.type === 'symbol'" class="symbol-chip">{{ part.text }}</span>
                    <span v-else>{{ part.text }}</span>
                  </template>"""

    new_tmpl_mne = """                  <template v-for="(part, pIdx) in parseMnemonicParts(m.text)" :key="pIdx">
                    <span v-if="part.type === 'symbol'" class="symbol-chip" :title="part.desc">
                      <img v-if="part.hash" :src="resolveImageUrl('symbols/' + part.hash + '.png')" :alt="part.text" class="symbol-icon-img" />
                      <span class="symbol-caption">{{ part.text }}</span>
                    </span>
                    <span v-else>{{ part.text }}</span>
                  </template>"""

    if old_tmpl_mne in content:
        content = content.replace(old_tmpl_mne, new_tmpl_mne)

    # 8. setup return 包含 resolveImageUrl
    if "return { fullRevealed, revealedSet, parsedSegments, cleanDistinctions, cleanMnemonics, parseMnemonicParts, toggleSeg, revealAll, hideAll" in content:
        content = content.replace(
            "return { fullRevealed, revealedSet, parsedSegments, cleanDistinctions, cleanMnemonics, parseMnemonicParts, toggleSeg, revealAll, hideAll",
            "return { fullRevealed, revealedSet, parsedSegments, cleanDistinctions, cleanMnemonics, parseMnemonicParts, resolveImageUrl, toggleSeg, revealAll, hideAll"
        )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {filepath} successfully.")

patch_file('scripts/generate_standalone_html.py', is_lite=False)
patch_file('scripts/generate_standalone_lite_html.py', is_lite=True)
