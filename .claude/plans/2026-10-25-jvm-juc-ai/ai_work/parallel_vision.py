# -*- coding: utf-8 -*-
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
BASE = r"D:\Java\Obisidian笔记\.claude\plans\2026-10-25-jvm-juc-ai\ai_work"
VISION = r"C:\Users\29574\.claude\skills\vision\vision.py"
PROMPT = "描述这张图，列出图中全部文字和关键信息。如果是代码、终端输出、SQL、表格，请尽量完整转写；如果是架构图/流程图/时序图，请说明各节点和数据流向。不要补充图外知识。"

jobs = []
with open(os.path.join(BASE, "vlist.txt"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        rel, out = line.split("\t")
        img = os.path.join(BASE, "images", rel)
        dst = os.path.join(BASE, "vision", out + ".txt")
        if os.path.exists(dst) and os.path.getsize(dst) > 0:
            continue
        jobs.append((img, dst, out))

def work(job):
    img, dst, out = job
    env = dict(os.environ, QWEN_MODEL="qwen3-vl-plus")
    with open(dst, "w", encoding="utf-8") as f:
        p = subprocess.run([sys.executable, VISION, "--provider", "qwen", img, PROMPT],
                           stdout=f, stderr=subprocess.STDOUT, env=env, timeout=300)
    return out, p.returncode

print("jobs", len(jobs), flush=True)
with ThreadPoolExecutor(max_workers=4) as ex:
    futs = [ex.submit(work, j) for j in jobs]
    for fu in as_completed(futs):
        try:
            print("DONE", fu.result(), flush=True)
        except Exception as e:
            print("FAIL", e, flush=True)