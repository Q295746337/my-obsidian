---
aliases:
  - JUC
  - 并发编程
  - 多线程
---

# JUC 知识体系

> JUC 系列按“基础 → 原理 → 应用 → 模式”组织；基础与原理各拆为 4 篇，便于按主题复习。

| 分组 | 子笔记 | 内容 |
| --- | --- | --- |
| 并发编程基础 | [[JUC/并发编程基础/01-线程基础\|01-线程基础]] | 概览、进程与线程、Java 线程（创建、API、状态、join、interrupt 等）。 |
| 并发编程基础 | [[JUC/并发编程基础/02-共享模型-管程\|02-共享模型-管程]] | synchronized、线程安全分析、Monitor、wait/notify、park/unpark、ReentrantLock。 |
| 并发编程基础 | [[JUC/并发编程基础/03-共享模型-内存与无锁\|03-共享模型-内存与无锁]] | Java 内存模型、可见性、有序性、happens-before、CAS、原子类、LongAdder。 |
| 并发编程基础 | [[JUC/并发编程基础/04-共享模型-不可变与工具\|04-共享模型-不可变与工具]] | 不可变设计、享元、线程池、J.U.C 并发工具与并发容器。 |
| 并发编程原理 | [[JUC/并发编程原理/01-CPU与volatile\|01-CPU与volatile]] | 指令级并行、CPU 缓存结构、volatile 与 final 原理。 |
| 并发编程原理 | [[JUC/并发编程原理/02-synchronized与等待通知\|02-synchronized与等待通知]] | synchronized 原理与锁升级、wait/notify、join、park/unpark。 |
| 并发编程原理 | [[JUC/并发编程原理/03-AQS与锁\|03-AQS与锁]] | AQS、ReentrantLock、读写锁、Semaphore 原理。 |
| 并发编程原理 | [[JUC/并发编程原理/04-并发容器\|04-并发容器]] | ConcurrentHashMap、LinkedBlockingQueue、ConcurrentLinkedQueue。 |
| 应用 | [[JUC/03-并发编程应用\|03-并发编程应用]] | 效率、限流、互斥、同步/异步、缓存一致性、分治、统筹与定时任务。 |
| 模式 | [[JUC/04-并发编程模式\|04-并发编程模式]] | 保护性暂停、Balking、顺序控制、生产者/消费者、工作线程、两阶段终止、单例与享元。 |

---

> 📎 **相关笔记**：[[JavaSE/12-多线程/12-JUC并发|JavaSE JUC 入门]] · [[JavaSE/JavaSE 索引|JavaSE]] · [[JVM/JVM 索引|JVM]] · [[检索/检索中心|检索中心]]
