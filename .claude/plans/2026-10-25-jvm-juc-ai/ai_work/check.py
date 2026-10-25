# -*- coding: utf-8 -*-
import os, re, glob, json
VAULT = r"D:\Java\Obisidian笔记"
AI = os.path.join(VAULT, "AI")
DATA = r"D:\Java\data\AI"
notes = ["AI 索引.md", "01-提示词工程.md", "02-大模型RAG开发.md", "03-RAG项目.md", "04-LangChain4J与通义千问.md"]
all_links = set()
problems = []
for n in notes:
    p = os.path.join(AI, n)
    if not os.path.exists(p):
        problems.append(f"MISSING NOTE {n}")
        continue
    txt = open(p, encoding="utf-8").read()
    body = re.sub(r"```.*?```", "", txt, flags=re.S)
    h1 = re.findall(r"(?m)^#\s+\S", body)
    print(f"{n}: H1={len(h1)} chars={len(txt)} lines={txt.count(chr(10))+1}")
    if len(h1) != 1:
        problems.append(f"{n}: H1 count {len(h1)}")
    if "![[" in txt:
        problems.append(f"{n}: uses ![[")
    if re.search(r"!\[[^\]]*\]\((?!file:///)", txt):
        problems.append(f"{n}: relative image link")
    # footers
    if "相关笔记" in txt:
        tail = txt.split("相关笔记")[-1]
        if len(re.sub(r"[\s>📎·\[\]|:：AI 索引0-9\-a-zA-Z一-鿿]", "", tail)) < 1:
            problems.append(f"{n}: empty footer")
        if "[[" not in tail:
            problems.append(f"{n}: footer has no link")
    # wikilinks
    for m in re.findall(r"\[\[([^\]]+)\]\]", txt):
        target = m.split("|")[0].strip()
        all_links.add(target)
    # images
    for m in re.findall(r"!\[[^\]]*\]\((file:///[^)]+)\)", txt):
        path = m.replace("file:///", "").replace("/", "\\")
        if not os.path.exists(path):
            problems.append(f"{n}: missing image {path}")
    # table check: line starting | followed by non-separator
    lines = txt.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and i + 1 < len(lines):
            nxt = lines[i+1].strip()
            if nxt.startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", nxt):
                # only flag if previous line is not a table row
                if i == 0 or not lines[i-1].strip().startswith("|"):
                    problems.append(f"{n}: table header without separator at line {i+1}")

# resolve links
def resolve(t):
    cands = [t]
    if not t.endswith(".md"):
        cands.append(t + ".md")
    for c in cands:
        if os.path.exists(os.path.join(VAULT, c)):
            return True
    # same-folder AI
    for c in cands:
        if os.path.exists(os.path.join(AI, c)):
            return True
    return False
print("\nLinks:")
for t in sorted(all_links):
    ok = resolve(t)
    print(("OK  " if ok else "BAD "), t)
    if not ok:
        problems.append(f"unresolved link {t}")

# images referenced vs files
refs = set()
for n in notes:
    txt = open(os.path.join(AI, n), encoding="utf-8").read()
    for m in re.findall(r"!\[[^\]]*\]\(file:///([^)]+)\)", txt):
        refs.add(os.path.normcase(os.path.normpath(m.replace("/", "\\"))))
files = set(os.path.normcase(os.path.normpath(p)) for p in glob.glob(DATA + r"\**\*.*", recursive=True))
print("\nImages refs", len(refs), "files", len(files))
for f in sorted(files - refs):
    problems.append(f"unreferenced image {f}")
for r in sorted(refs - files):
    problems.append(f"missing image file {r}")

print("\nPROBLEMS", len(problems))
for p in problems:
    print("-", p)

# source files
srcs = ["01提示词工程.pptx","02大模型RAG开发.pptx","03RAG项目.pptx","LangChain4J+通义千问大模型应用开发(志愿填报大师).pptx"]
print("\nSources:", [(s, os.path.exists(os.path.join(AI,s))) for s in srcs])