# Task Plan: JUC 拆分 + JVM/JUC 补全 + AI/面试 补充

## Goal

按用户新要求处理：

1. 拆分 `JUC/01-并发编程基础.md`（212KB）和 `JUC/02-并发编程原理.md`（143KB）。
2. 用 JVM 原始 PDF 补全 JVM 笔记中的缺失内容。
3. 用 JUC 原始 PDF 补全 JUC 笔记中的缺失内容。
4. 处理 AI 新增 `第三章：LangChain4j.md` 和 `AI/图片和附件/`；AI 内容可按知识储备补充，并标明“补充”。
5. 用面试文件夹中新下载的 9 篇讲义补全现有面试笔记，并处理 `大厂面经(Java方向)`。
6. 不在笔记里写归档路径；归档只作为文件清理动作。
7. 图谱密度问题暂存，等后续补充资料后再统一更新图谱。

## Phases

- [ ] Phase 1：盘点新 PDF / 新笔记 / 新 AI 章节（基础盘点已完成）
- [ ] Phase 2：并行处理 JUC 拆分+PDF补全、JVM PDF补全、AI 章节+补充、面试合并（面试已完成，其余进行中）
- [ ] Phase 3：索引、别名、检索层、交叉链接整合（不更新图谱密度指标）
- [ ] Phase 4：全库验收 + 交付报告

## Decisions

- JUC 拆分为子文件夹：
  - `JUC/并发编程基础/01-线程基础.md`（原 1–3 章）
  - `JUC/并发编程基础/02-共享模型-管程.md`（原 4 章）
  - `JUC/并发编程基础/03-共享模型-内存与无锁.md`（原 5–6 章）
  - `JUC/并发编程基础/04-共享模型-不可变与工具.md`（原 7–8 章）
  - `JUC/并发编程原理/01-CPU与volatile.md`（指令级并行、CPU 缓存、volatile、final）
  - `JUC/并发编程原理/02-synchronized与等待通知.md`（synchronized、wait/notify、join、park/unpark）
  - `JUC/并发编程原理/03-AQS与锁.md`（AQS、ReentrantLock、读写锁、Semaphore）
  - `JUC/并发编程原理/04-并发容器.md`（ConcurrentHashMap、LinkedBlockingQueue、ConcurrentLinkedQueue）
  - 保留 `03-并发编程应用.md`、`04-并发编程模式.md`，更新索引。
- JVM/JUC 补全以原始 PDF 为准；PDF 也没有的内容保留“原文缺失”标记。
- AI 新增 `05-LangChain4j核心.md`；原 02/03/04 的缺口可补充，但必须标注“补充（非原 PPT）”。
- 面试新增 `12-大厂面经.md`；9 篇新讲义用于补全现有专题，不重复整篇。
- 不在笔记中写 `D:\Java\source_archive` 路径。
- 暂不更新图谱健康度指标；等后续资料补齐后再统一做。

## Constraints

- 不处理 `微服务` 的 ES02/BM25 遗留问题。
- 不处理 MySQL 抽查、imgur 外链、标题过长。
- 源 PDF/docx/pptx 在验收前不删除；归档动作只清理原始新讲义，笔记不写归档路径。
- 每个模块完成后自检：H1、页脚、断链、缺图、重复标题、空章节、代码围栏。

## Status

**Currently in Phase 2** — 面试已完成并自检；等待 JUC、JVM、AI 完成。