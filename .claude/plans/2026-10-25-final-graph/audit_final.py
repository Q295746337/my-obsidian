import os
import re
from collections import defaultdict, Counter

V = r'D:\Java\Obisidian笔记'
SEP = chr(92)
SCOPE = ['JavaSE','JavaWeb','MySQL','Redis','SSM框架','SpringBoot2','JVM','JUC','AI','微服务','面试','八股文','黑马点评']

def rel(p):
    return os.path.relpath(p, V).replace(SEP, '/')

mds = []
allmds = []
for mod in SCOPE + ['检索']:
    for root, dirs, fs in os.walk(os.path.join(V, mod)):
        for f in fs:
            if f.endswith('.md'):
                r = rel(os.path.join(root, f))
                allmds.append(r)
                if mod != '检索':
                    mds.append(r)
mds = sorted(mds)
allmds = sorted(allmds)

stems = {m[:-3] for m in allmds}
by_name = defaultdict(list)
for m in allmds:
    by_name[os.path.basename(m)[:-3]].append(m[:-3])

def resolve(t):
    if t in stems:
        return t
    c = by_name.get(t.split('/')[-1])
    return c[0] if c else None

issues = defaultdict(list)
for m in allmds:
    t = open(os.path.join(V, m), encoding='utf-8').read()
    lines = t.splitlines()
    fence = None
    hd = []
    outside = []
    code_langs = []
    for i, l in enumerate(lines, 1):
        fm = re.match(r'^\s*(`{3,4}|~{3,4})\s*([^\s`]*)', l)
        if fm:
            tok = fm.group(1)
            if fence is None:
                fence = tok
                code_langs.append(fm.group(2).strip())
            elif l.strip().startswith(fence):
                fence = None
            continue
        if fence:
            continue
        hm = re.match(r'^(#{1,6})\s+(.+)$', l)
        if hm:
            hd.append((i, len(hm.group(1)), hm.group(2).strip(), l))
        if re.match(r'^\s*(create\s+table|insert\s+into|select\s+|alter\s+table|constraint\s+|varchar\s*\(|id\s+int|name\s+varchar)', l, re.I):
            outside.append((i, l.strip()[:60]))
    if fence:
        issues['unclosed_fence'].append(m)
    h1 = [h for h in hd if h[1] == 1]
    if not h1:
        issues['no_h1'].append(m)
    if len(h1) > 1:
        issues['multi_h1'].append(m)
    if any(re.search(r'\[\[', h[3]) for h in hd):
        issues['wikilink_in_heading'].append(m)
    seen = Counter(h[2] for h in hd if h[1] >= 2)
    for k, v in seen.items():
        if v > 1:
            issues['dup_heading'].append((m, k, v))
    fm = re.search(r'相关笔记\*{0,2}[：:]\s*(.*)', t)
    if fm and '[[' not in fm.group(1):
        issues['empty_footer'].append(m)
    for raw in re.findall(r'\[\[([^\]]+)\]\]', t):
        link = raw.replace(SEP + '|', '|')
        target = link.split('|')[0].split('#')[0].strip()
        if target and not resolve(target):
            issues['broken'].append((m, target))
    for u in re.findall(r'!\[[^\]]*\]\((file:///[^)]+)\)', t) + re.findall(r'<img[^>]+src="(file:///[^"]+)"', t):
        q = os.path.normcase(os.path.abspath(u.replace('file:///', '').replace('/', os.sep)))
        if not os.path.exists(q):
            issues['missing_img'].append((m, u))
    if re.search(r'!\[\[', t):
        issues['embed_img'].append(m)
    if re.search(r'\]\(\.\./', t):
        issues['rel_img'].append(m)
    if re.search(r'<font|</font>', t, re.I):
        issues['font_tag'].append(m)
    if re.search('​|﻿|\xa0', t):
        issues['zero_width'].append(m)
    if outside:
        issues['code_outside'].append((m, len(outside)))
    for lang in code_langs:
        if not lang:
            issues['code_no_lang'].append(m)

def cols(l):
    return l.replace(SEP + '|', '').count('|') - 1

for m in allmds:
    lines = open(os.path.join(V, m), encoding='utf-8').read().splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith('|') and i + 1 < len(lines) and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i + 1]):
            n = cols(lines[i])
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith('|'):
                if cols(lines[j]) != n:
                    issues['table_cols'].append((m, j + 1, n, cols(lines[j])))
                j += 1
            i = j
            continue
        i += 1

for m in allmds:
    lines = open(os.path.join(V, m), encoding='utf-8').read().splitlines()
    fence = None
    hd = []
    for i, l in enumerate(lines):
        fm = re.match(r'^\s*(`{3,4}|~{3,4})', l)
        if fm:
            if fence is None:
                fence = fm.group(1)
            elif l.strip().startswith(fence):
                fence = None
            continue
        if fence:
            continue
        hm = re.match(r'^(#{1,6})\s+', l)
        if hm:
            hd.append((i, len(hm.group(1))))
    for i, lvl in hd:
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j >= len(lines):
            issues['empty_section'].append((m, lines[i][:60]))
            continue
        nm = re.match(r'^(#{1,6})\s+', lines[j])
        if nm and len(nm.group(1)) <= lvl:
            issues['empty_section'].append((m, lines[i][:60]))

alias = defaultdict(list)
for m in mds:
    t = open(os.path.join(V, m), encoding='utf-8').read()
    fm = re.match(r'^---\n(.*?)\n---', t, re.S)
    if not fm:
        continue
    am = re.search(r'(?m)^aliases:\s*\n((?:\s+-\s+.*\n?)*)', fm.group(1))
    if am:
        for a in re.findall(r'-\s+(.+)', am.group(1)):
            alias[a.strip()].append(m[:-3])
dupalias = {k: v for k, v in alias.items() if len(v) > 1}

edges = []
for n in mds:
    stem = n[:-3]
    isidx = '索引' in os.path.basename(stem)
    t = open(os.path.join(V, n), encoding='utf-8').read()
    for line in t.splitlines():
        for raw in re.findall(r'\[\[([^\]]+)\]\]', line):
            link = raw.replace(SEP + '|', '|')
            target = link.split('|')[0].split('#')[0].strip()
            r = resolve(target) if target else None
            if not r:
                continue
            kind = 'index' if isidx else ('footer' if '相关笔记' in line else 'semantic')
            edges.append((stem, r, kind))

def und(es):
    s = set()
    for a, b, k in es:
        if a != b:
            s.add((min(a, b), max(a, b), k))
    return s

all_u = und(edges)
sem_u = und([e for e in edges if e[2] == 'semantic'])
foot_u = und([e for e in edges if e[2] == 'footer'])
idx_u = und([e for e in edges if e[2] == 'index'])
pairs = set((min(a, b), max(a, b)) for a, b, k in edges if a != b)

def comps(eset, nodes):
    adj = defaultdict(set)
    for a, b, k in eset:
        adj[a].add(b)
        adj[b].add(a)
    seen = set()
    c = 0
    for n in nodes:
        if n in seen:
            continue
        c += 1
        stack = [n]
        seen.add(n)
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
    return c

stems_list = [n[:-3] for n in mds]
out = Counter()
indeg = Counter()
for a, b, k in edges:
    if k != 'semantic' or a == b:
        continue
    out[a] += 1
    indeg[b] += 1
nonidx = [s for s in stems_list if '索引' not in os.path.basename(s)]
iso = [s for s in nonidx if out[s] == 0 and indeg[s] == 0]
noout = [s for s in nonidx if out[s] == 0]
cross = [(a, b) for a, b, k in sem_u if a.split('/')[0] != b.split('/')[0]]

print('MANAGED', len(mds), 'ALL', len(allmds))
for k in ['no_h1', 'multi_h1', 'wikilink_in_heading', 'empty_footer', 'broken', 'missing_img', 'embed_img', 'rel_img', 'font_tag', 'zero_width', 'unclosed_fence', 'code_no_lang', 'empty_section', 'dup_heading', 'code_outside', 'table_cols']:
    v = issues[k]
    print(f'{k}: {len(v)}', v[:5] if v else '')
print('alias_duplicates', len(dupalias), list(dupalias.items())[:5])
print('metrics notes', len(mds), 'pairs', len(pairs), 'semantic', len(sem_u), 'footer', len(foot_u), 'index', len(idx_u), 'all', len(all_u))
print('semantic_ratio', round(len(sem_u) / len(pairs) * 100, 1) if pairs else 0, 'components_all', comps(all_u, stems_list), 'components_sem', comps(sem_u, stems_list), 'isolated', len(iso), 'noout', len(noout), 'cross', len(cross))

unc = []
for m in mds:
    stem = m[:-3]
    if '索引' in os.path.basename(stem):
        continue
    mod = stem.split('/')[0]
    idx = os.path.join(V, mod, mod + ' 索引.md')
    if not os.path.exists(idx):
        unc.append((stem, 'NO_INDEX'))
        continue
    it = open(idx, encoding='utf-8').read()
    base = os.path.basename(stem)
    if f'[[{stem}' not in it and f'[[{base}' not in it:
        unc.append((stem, 'NOT_LINKED'))
print('index_uncovered', len(unc), unc[:10])