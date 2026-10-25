# AI 模块整理报告（2026-10-25）

## 1. 产出文件

| 文件 | 动作 | 说明 |
| --- | --- | --- |
| `AI/05-LangChain4j核心.md` | 新建 | 由第三章讲义重组，8 个知识主线 + 面试题 + 易错点 |
| `AI/AI 索引.md` | 更新 | 5 篇笔记、学习顺序、摘要、来源 |
| `AI/01-提示词工程.md` | 增补链接 | 增加 04/05 的后续链接，页脚收敛到 3 条 |
| `AI/02-大模型RAG开发.md` | 补全 + 链接 | 在 RunnablePassthrough 截断处补完整检索链 |
| `AI/03-RAG项目.md` | 补全 + 链接 | 新增项目结构与离线/在线代码骨架 |
| `AI/04-LangChain4J与通义千问.md` | 补全 + 链接 | 新增 Tools/Function Calling 完整实现要点 |

## 2. 05 笔记结构

1. 为什么需要 LangChain4j
2. 快速入门（依赖、模型、调用、日志）
3. Spring Boot 整合
4. AiServices（编程式、声明式、属性表）
5. 流式调用
6. 消息注解（SystemMessage、UserMessage、@V）
7. 会话记忆（原理、ChatMemory、隔离、Redis 持久化）
8. RAG 知识库（原理、向量/余弦、存储、检索、核心 API、收尾、常见坑）
9. Tools 工具调用
10. 核心 API 与配置速查
11. 面试题与答案要点
12. 易错点

第三章原有的 3.8 Tools 保留为精简版，完整建表/实体/Mapper/Service 放在 04 的补充章节，避免两篇重复。

## 3. 图片处理

- 源文件 43 处图片引用，43 个文件全部一一对应。
- A/B 档保留 29 张：6 个流程 GIF + 23 张 PNG（架构、时序、向量、余弦、RAG 流程、分割、会话记忆、Function Calling、关键 UI 与日志截图）。
- C 档跳过 14 张：Logo（image 33）、创建项目截图（2/22）、资源/项目结构截图（7/10/13/16/21/26/30/34）、安装文档截图（27/36）、重复浏览器截图（28）。
- 保留图片已复制到 `D:\Java\data\AI\05-LangChain4j核心\`，重命名为语义化文件名，正文统一用 `file:///D:/Java/data/AI/05-LangChain4j核心/...` 引用。
- 29 张保留图全部被 05 引用，0 未引用、0 缺图。

## 4. 现有笔记补充

### 02-大模型RAG开发

新增 `### 13.1 补充：RunnablePassthrough 与完整检索链（非原 PPT）`：

- 字典分发与 `RunnablePassthrough.assign` 两种写法。
- 完整的 `retriever | format_docs` + Prompt + Model + StrOutputParser 检索链。
- 链上类型流转表、`stream` 用法、来源回传、空检索处理。
- 说明原 PPT 的 `reference_text` 拼接会多出一个 `]`，建议改用 `"\n\n".join(...)`。

### 03-RAG项目

新增 `## 7. 补充：项目结构与关键代码骨架（非原 PPT）`，后续章节顺延：

- 推荐目录结构。
- `config_data.py`、`vector_stores.py`、`knowledge_base.py`、`file_history_store.py`、`rag.py`。
- `app_qa.py` / `app_file_upload.py` 两个 Streamlit 入口。
- 运行顺序、依赖、真实项目还需处理的边界。
- 修正 `FileChatMessageHistory` 的 Pydantic 初始化写法，避免直接给 BaseModel 赋未声明属性。

### 04-LangChain4J与通义千问

新增 `### 7.5 补充：Tools / Function Calling 完整实现要点（非原 PPT）`：

- `reservation` 建表 SQL、实体、Mapper、Service。
- 完整 `ReservationTool`（6 个 `@P` 参数 + 查询工具）。
- 最终 `@AiService` 装配与 Controller。
- Function Calling 5 步执行细节、工程要点表（描述、校验、幂等、序列化、安全、多工具、可选参数）、测试建议。
- 建库名与 7.2 节数据源统一为 `gk`，并说明与讲义 `volunteer` 的取舍。

所有非 PPT 内容均使用 `补充（非原 PPT）` 标注。

## 5. 索引与链接

- 索引更新为 5 篇笔记，加入 05，学习顺序调整为 01 → 02 → 03 → 04 → 05。
- 05 正文链接 01/02/03/04；01–04 均增加 05 链接。
- 索引页脚保留 `[[JavaSE/JavaSE 索引|JavaSE]]` 与 `[[检索/检索中心|检索中心]]`。
- 删除 01–04 原有的空 `相关笔记` 章节，页脚统一 3 条链接。

## 6. 归档

- `AI/第三章：LangChain4j.md` → `D:\Java\source_archive\AI_原始资料_20261025\`
- `AI/图片和附件/`（43 个文件，含 6 个 GIF）→ `D:\Java\source_archive\AI_原始资料_20261025\图片和附件\`
- 源 PPTX 保留在 `AI/`。
- 笔记中未写入归档路径，也未残留 `图片和附件` / 源 md 路径引用。

## 7. 自检结果

对 6 个 md（01–05 + 索引）逐项检查，全部通过：

- 每篇 1 个 H1。
- 页脚非空，均含“相关笔记”。
- 0 断裂 wikilink（含跨模块 JavaSE/检索中心）。
- 0 缺图；05 的 29 张图片全部存在。
- 0 未引用新增图。
- 0 重复标题、0 空章节。
- 代码围栏成对，所有开围栏均标注语言。
- 表格分隔行合法，代码块内的 `|` 未误判为表格。
- 未触碰 AI 以外模块。

## 8. 其他说明

- 修正讲义中余弦相似度例子的分子/分母口误：`V=(1,2)`、`U=(2,1)` 的分子为 4、分母为 5，结果 0.8。
- 补充说明余弦相似度完整范围为 `[-1,1]`，课程“0~1”仅适用于第一象限例子。
- 05 保留第三章 Tools 知识，但完整工程实现放在 04，形成“05 讲 API、04 讲项目落地”的分工。