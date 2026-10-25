import json, re
items=json.load(open('.tmp_baguwen/items.json',encoding='utf-8'))
tbls=[it for it in items if it['type']=='tbl']

def flat(rows):
    return ' | '.join(sum(rows,[]))

def is_code_table(rows):
    if not rows: return (False,None)
    allcells=[c.strip() for r in rows for c in r]
    text=' '.join(allcells)
    lang=None
    for L in ['Java','SQL','YAML','Plain Text','C']:
        if any(c.strip().lower()==L.lower() for c in allcells[:6]):
            lang='java' if L=='Java' else ('sql' if L=='SQL' else ('yaml' if L=='YAML' else ('text' if L=='Plain Text' else 'c')))
            break
    # embedded numbered code in 2nd col
    # sequential line numbers in first col
    first=[r[0].strip() for r in rows if r]
    nums=[]
    for x in first:
        if re.fullmatch(r'\d+',x): nums.append(int(x))
    seq = len(nums)>=3 and nums[:len(nums)]==list(range(1,len(nums)+1))
    if lang and (seq or len(rows)<=3 or any(len(r)>=2 and re.search(r'\b(public|private|class|import|select|update|insert|@\w+|//|;)', ' '.join(r[1:])) for r in rows[1:])):
        return (True,lang)
    if seq and len(nums)>=3 and len(nums)>=len(rows)-1-1:
        return (True,'java')
    # table with language header and multi-line numbered code in one cell
    if lang and len(rows)<=3 and any(re.search(r'\b\d+\s{2,}', c) for c in allcells):
        return (True,lang)
    return (False,None)

for n,t in enumerate(tbls):
    rows=t['rows']
    code,lang=is_code_table(rows)
    r=len(rows); c=max(len(x) for x in rows) if rows else 0
    print(f'{n:03d} {r}x{c} code={code} lang={lang} :: {flat(rows)[:90]}')
