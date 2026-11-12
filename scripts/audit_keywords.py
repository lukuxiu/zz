import json, re, sys
from collections import Counter
k = json.load(open('data/knowledge.json', encoding='utf8'))['records']
o = open('reports/kwaudit.txt', 'w', encoding='utf8')
SP = re.compile(r'<span class="keyword" style="color:(#\w+);[^>]*>(.*?)</span>')
tot = single = adjtot = 0
bad = []
for x in k:
    h = x['contentHtml']
    sp = SP.findall(h)
    tot += len(sp)
    s = sum(1 for c, w in sp if len(w) == 1)
    single += s
    adj = len(re.findall(r'</span><span class="keyword" style="color:(#\w+);[^>]*>[^<]*</span><span class="keyword" style="color:\1', h))
    # also same-colour spans separated by <=1 char
    near = len(re.findall(r'color:(#\w+);[^>]*>[^<]*</span>.{0,1}<span class="keyword" style="color:\1', h))
    adjtot += near
    if s >= 3 or near:
        bad.append((x['id'], x['title'], len(sp), s, near))
print('cards', len(k), 'spans', tot, 'single-char', single, 'near-same-colour', adjtot, 'flagged cards', len(bad), file=o)
for b in bad[:60]:
    print(b, file=o)
print('--- samples (content)', file=o)
for x in k[:8]:
    print(x['id'], x['title'], '|', x['content'].replace('\n', ' / ')[:220], file=o)
print('--- symbols', file=o)
c = Counter((s['type'], s['char'], s['desc']) for x in k for s in x['symbols'])
print(c.most_common(45), file=o)
print('cards without symbols', sum(1 for x in k if not x['symbols']), file=o)
print('--- kp-003 all', file=o)
for x in k:
    if x['sourceId'] == '003':
        print(x['id'], x['title'], x['content'].replace('\n', ' / '), file=o)
