#!/bin/bash
while IFS=$'\t' read -r rel out; do
  [ -z "$rel" ] && continue
  img="D:/Java/Obisidian笔记/.claude/plans/2026-10-25-jvm-juc-ai/ai_work/images/$rel"
  o="D:/Java/Obisidian笔记/.claude/plans/2026-10-25-jvm-juc-ai/ai_work/vision/$out.txt"
  if [ -s "$o" ]; then continue; fi
  QWEN_MODEL=qwen3-vl-plus python "C:/Users/29574/.claude/skills/vision/vision.py" --provider qwen "$img" "描述这张图，列出图中全部文字和关键信息。如果是代码、终端输出、SQL、表格，请尽量完整转写；如果是架构图/流程图/时序图，请说明各节点和数据流向。不要补充图外知识。" > "$o" 2>&1
  echo "DONE $out"
done < vlist.txt
