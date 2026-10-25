# JVM 笔记 PDF 补全报告

日期：2026-10-25
范围：仅 `JVM/` 下 5 篇笔记与 JVM 索引，未改动 JUC、AI、面试、微服务。

## 一、补全的章节

### 00-引言
- 修正图片归位：“常见的 JVM”改用维基百科 JVM 对比表（`image-002.jpeg`）。
- 补全“学习路线”：JVM 整体架构图（`image-001.jpeg`）+ 图中四段主线（类加载、内存结构、执行引擎、本地方法接口）。
- 补入原文两个超链接：维基百科 JVM 对比页、JVM 架构参考资料。

### 01-内存结构
- 原始 PDF 与 docx 中 4.2、5.6、5.7 均为空（仅有标题），保留“原文缺失”标记，未臆造。

### 02-垃圾回收
- 补全 G1 `7) Remark`：`pre-write barrier + satb_mark_queue` 与 SATB 示意图（新增 `page-018.png`）。
- 5.3 代码残片在 PDF 中同样只有 `static Map map =`、`软`、`弱`，保留“原文缺失”标记并注明 PDF 一致。

### 03-类加载与字节码技术
- 1：补入 `ClassFile` 结构；1.4 补全 ACC_FINAL/ACC_SUPER/ACC_ENUM 含义；1.5 补全 FieldType 的 C/F/J/L/[/S 类型。
- 2.1：补入构造方法与 main 方法原始字节码，清理被误包进代码块的说明文字。
- 2.2：补齐 `javap -v` 头部与常量池 #1–#13。
- 2.4：补入 i++ 示例完整字节码（含 LineNumberTable/LocalVariableTable）。
- 2.5：补入 Demo3_3 源码与完整 goto 字节码。
- 2.6：补齐 do-while 字节码缺失的 `bipush 10` / `if_icmplt 2`。
- 2.7：补答案 0（源文档注释）与字节码解释。
- 2.8：补 `<cinit>` 字节码、Demo3_8_2 源码。
- 2.9：补 Demo3_9 源码。
- 2.11：补 multi-catch 的 Exception table。
- 2.12：补“finally 对返回值影响”的字节码与答案 10。
- 3.6：补 switch 字符串两份转换后代码；3.7 补 switch 枚举转换代码；3.9 补 try-with-resources 转换代码。
- 4.2：补魔数被修改后的 `ClassFormatError` 运行输出。
- 4.3：补 Load3 验证代码。
- 5.2：补扩展类加载器运行输出（`ext G init` / ExtClassLoader）。
- 5.4：补 `ServiceLoader.LazyIterator.nextService()` 源码。
- 6.1：补 JMH `Benchmark1` 源码与内联/禁用内联两组测试结果表，整理 JMH 依赖 XML。
- 5.5 自定义类加载器：PDF 与 docx 均无示例代码，保留“原文缺失”标记。

### 04-内存模型
- 1.2：补 i++/i-- 字节码。
- 2.3：补可见性示例字节码。
- 3.1：补 jcstress 压测输出；原文“638 次”与输出 1,729/1,652 不一致，已加注保留原文。
- 4.1：补 Unsafe + CAS 完整示例（TestCAS/DataContainer）。
- 4.3：补 AtomicInteger 改写示例。
- 1.1：PDF 与 docx 均只有问题描述、无示例代码，保留“原文缺失”标记。

## 二、索引
- 更新 `JVM/JVM 索引.md`：00 去掉“学习路线缺失”，补“整体架构与学习路线”；02 注明含 Remark；04 补“原子类”。

## 三、自检结果
- H1：5 篇笔记 + 索引均恰好 1 个。
- 页脚：全部非空，保留模块链接。
- 断链：0（含索引表内转义 `\|`）。
- 缺图：0；未引用图：0；JVM 附件 62 张 = 引用 62 条。
- 新增图片：1 张（`D:/Java/data/JVM/02-垃圾回收/page-018.png`），已引用。
- 重复标题：0；空叶子章节：0。
- 代码围栏：全部成对且有语言标注。
- 未写入 `D:\Java\source_archive` 路径；源 PDF/docx 未移动、未删除。
- 临时渲染目录 `D:/Java/data/JVM/_tmp` 已清理。