---
aliases:
  - AI
  - 大模型
  - LLM
---

# AI 大模型应用开发索引

本模块整理自 4 份课程 PPT 和 1 份第三章讲义，覆盖提示词工程、RAG 原理与 LangChain 开发、RAG 项目实战、LangChain4J + 通义千问，以及 LangChain4j 核心 API 与完整实现。

## 笔记列表

| 笔记 | 主题 | 一句话摘要 |
| --- | --- | --- |
| [[01-提示词工程]] | 通义千问接入、OpenAI SDK、Prompt 技巧、金融文本三大任务 | 从 API-KEY 配置到 Zero-shot/Few-shot 提示词实战，打牢大模型调用与提示词设计基础 |
| [[02-大模型RAG开发]] | RAG 原理、向量与余弦相似度、LangChain 组件、文档入库与检索 | 用 LangChain 串起 Models/Prompts/Chains/Memory/Loaders/VectorStore，理解 RAG 全链路 |
| [[03-RAG项目]] | 服装商品智能客服的项目结构、离线入库、在线问答 | 以文件职责、流程图和代码骨架还原一个基于 Chroma 的 RAG 项目 |
| [[04-LangChain4J与通义千问]] | Java 接入大模型、AiServices、会话记忆、RAG、Tools | 用 LangChain4J + Spring Boot 开发志愿填报助手，覆盖记忆、知识库和函数调用 |
| [[05-LangChain4j核心]] | LangChain4j 快速入门、Spring 整合、AiServices、流式调用、会话记忆、RAG、Tools、核心 API | 按第三章讲义系统整理 LangChain4j 的配置、代码与 API，是 04 的讲义深化版 |

## 建议学习顺序

1. [[01-提示词工程]]：先会调用模型、理解角色和提示词。
2. [[02-大模型RAG开发]]：理解 RAG 原理和 LangChain 组件。
3. [[03-RAG项目]]：看一个完整项目的文件结构、离线/在线流程和代码骨架。
4. [[04-LangChain4J与通义千问]]：把同样的能力落到 Java/Spring Boot 技术栈，先建立项目全景。
5. [[05-LangChain4j核心]]：再按讲义逐项掌握 AiServices、记忆、RAG 和 Tools 的完整实现。

## 模块要点

- **提示词是基础**：清晰的指令、角色、分隔符、步骤、示例、参考文本，能显著改善输出。
- **RAG 的核心是检索 + 生成**：离线建库，在线检索，检索结果与问题一起组装 Prompt。
- **向量检索依赖嵌入模型和相似度算法**：维度、分块大小、top-k、相似度阈值都会影响效果；入库和检索必须使用同一个嵌入模型。
- **Java 侧用 LangChain4J**：AiServices 声明接口，配合会话记忆、RAG 检索器和 Tools 完成复杂应用；记忆可用 `ChatMemoryProvider` 隔离、用 `ChatMemoryStore` 持久化。
- **从 PPT 到代码**：04 偏项目主线，05 偏讲义级配置和 API 细节，两篇配合阅读。
- **图片说明**：本模块图片统一存放在 `D:\Java\data\AI\`，正文使用 `file:///` 绝对路径引用。

## 来源

- `AI/01提示词工程.pptx`（96 页）
- `AI/02大模型RAG开发.pptx`（114 页）
- `AI/03RAG项目.pptx`（10 页）
- `AI/LangChain4J+通义千问大模型应用开发(志愿填报大师).pptx`（132 页）
- 课程第三章讲义《LangChain4j》

---

> 📎 **相关笔记**：[[JavaSE/JavaSE 索引|JavaSE]] · [[黑马点评/黑马点评 索引|黑马点评]] · [[检索/检索中心|检索中心]]
