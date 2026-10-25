# JUC 拆分与 PDF 补全报告

日期：2026-10-25

## 结果概览

| 项目 | 结果 |
| --- | --- |
| 新增笔记 | 8 篇（基础 4 + 原理 4） |
| 保留笔记 | `JUC/03-并发编程应用.md`、`JUC/04-并发编程模式.md` |
| 索引 | `JUC/JUC 索引.md` 重写 |
| 删除原笔记 | `JUC/01-并发编程基础.md`、`JUC/02-并发编程原理.md` |
| 源文件 | 4 个 PDF、4 个 docx 均保留在 `JUC/` |

## 拆分结构

| 新文件 | 原内容 |
| --- | --- |
| `JUC/并发编程基础/01-线程基础.md` | 原 1–3 章：概览、进程与线程、Java 线程 |
| `JUC/并发编程基础/02-共享模型-管程.md` | 原第 4 章：管程、synchronized、Monitor、wait/notify、park/unpark、ReentrantLock |
| `JUC/并发编程基础/03-共享模型-内存与无锁.md` | 原 5–6 章：内存模型、可见性/有序性、CAS、原子类 |
| `JUC/并发编程基础/04-共享模型-不可变与工具.md` | 原 7–8 章：不可变、线程池、J.U.C |
| `JUC/并发编程原理/01-CPU与volatile.md` | 指令级并行、CPU 缓存、volatile、final |
| `JUC/并发编程原理/02-synchronized与等待通知.md` | Monitor、synchronized 原理/进阶、wait/notify、join、park/unpark |
| `JUC/并发编程原理/03-AQS与锁.md` | AQS、ReentrantLock、读写锁、Semaphore |
| `JUC/并发编程原理/04-并发容器.md` | ConcurrentHashMap、LinkedBlockingQueue、ConcurrentLinkedQueue |

## PDF 补全

- 原 `01-并发编程基础` 的 27 处“原文此处无正文”已全部替换为 PDF 要点摘要 + 对应笔记链接（原理类指向原理篇，模式类指向 `04-并发编程模式`，应用类指向 `03-并发编程应用`）。
- 原 `02-并发编程原理` 的 1 处“正常流程”占位已补入 Semaphore PROPAGATE 正常流程时序图与图注。
- 顺带补全 `04-并发编程模式` 的“原理之 join”占位（链接更新时一并处理）。
- 修复转换残留代码块：
  - jcstress 说明文字被误放进 `java` 代码块；
  - `o volatile`、`CAS 与 volatile`、`. CAS 与 volatile ● API`、`o final` 等伪代码块改为列表；
  - `LinkedBlockingQueue.put` 被拆成两个代码围栏，已合并；
  - `take` 方法的 `return x; }` 尾块已并回方法；
  - `源码分析 http://...` 代码块改为引用段落；
  - 章节小结中 `o` 粘连的条目已拆成独立列表项。

## 图片

- 原有 84 张图片按新笔记分别复制到 `D:\Java\data\JUC\<笔记名>\`，引用改为 `file:///D:/Java/data/JUC/<笔记名>/...`。
- 新增 PDF 渲染图 2 张：
  - `D:\Java\data\JUC\04-共享模型-不可变与工具\page-149-threadpool.png`（线程池 c=2、m=3 调度示意，原笔记图错配）。
  - `D:\Java\data\JUC\03-AQS与锁\page-079-propagate.png`（Semaphore PROPAGATE 正常流程时序图）。
- 修正错配：无锁效率段误用的线程状态图已移除；拒绝策略 UML 移到拒绝策略列表之后。
- 为线程状态图、线程池图和 PROPAGATE 图补充图注。
- 旧图片目录 `data/JUC/01-并发编程基础`、`data/JUC/02-并发编程原理` 保留，但已不被笔记引用。

## 自检

| 检查项 | 结果 |
| --- | --- |
| 新笔记数量 | 8 |
| 每篇 H1 | 1 |
| 页脚 | 均有，3 条链接 |
| 断链 | 0（全库检查；方法论示例链接除外） |
| 缺失图片 | 0 |
| 未引用新增图 | 0 |
| 重复标题 | 0 |
| 空章节 | 0 |
| 代码围栏 | 全部闭合、均有语言标注 |
| 表格 | 0 处格式错误 |
| 旧笔记链接引用 | 0 |

## 保留的缺失标记

- `JUC/并发编程原理/01-CPU与volatile.md` 的“2. 获取 final 变量的原理”：`并发编程_原理.pdf` 同样只有标题、无正文，保留缺失说明，不臆造。

## 其他改动

- `JUC/03-并发编程应用.md`、`JUC/04-并发编程模式.md`：仅更新页脚链接与 join 占位，不改文件名。
- `JUC/JUC 索引.md`：改为分组表格，覆盖 8 篇子笔记与 03/04；页脚保留 JavaSE JUC 入门、JavaSE、JVM、检索中心。
- `检索/概念索引.md`、`资料整理方法论.md`：更新指向旧 `02-并发编程原理` 的链接。
- 未处理 JVM、AI、面试、微服务模块。