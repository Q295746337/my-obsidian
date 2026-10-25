---
aliases:
  - AI
  - 大模型
  - LLM
---

# AI 大模型应用开发索引

本模块整理自 4 份课程 PPT，共 352 页，覆盖提示词工程、RAG 原理与 LangChain 开发、RAG 项目实战、LangChain4J + 通义千问。

## 笔记列表

| 笔记 | 主题 | 一句话摘要 |
| --- | --- | --- |
| [[01-提示词工程]] | 通义千问接入、OpenAI SDK、Prompt 技巧、金融文本三大任务 | 从 API-KEY 配置到 Zero-shot/Few-shot 提示词实战，打牢大模型调用与提示词设计基础 |
| [[02-大模型RAG开发]] | RAG 原理、向量与余弦相似度、LangChain 组件、文档入库与检索 | 用 LangChain 串起 Models/Prompts/Chains/Memory/Loaders/VectorStore，理解 RAG 全链路 |
| [[03-RAG项目]] | 服装商品智能客服的项目结构、离线入库、在线问答 | 以文件职责和流程图还原一个基于 Chroma 的 RAG 项目骨架 |
| [[04-LangChain4J与通义千问]] | Java 接入大模型、AiServices、会话记忆、RAG、Tools | 用 LangChain4J + Spring Boot 开发志愿填报助手，覆盖记忆、知识库和函数调用 |

## 建议学习顺序

1. [[01-提示词工程]]：先会调用模型、理解角色和提示词。
2. [[02-大模型RAG开发]]：理解 RAG 原理和 LangChain 组件。
3. [[03-RAG项目]]：看一个完整项目的文件结构和离线/在线流程。
4. [[04-LangChain4J与通义千问]]：把同样的能力落到 Java/Spring Boot 技术栈。

## 模块要点

- **提示词是基础**：清晰的指令、角色、分隔符、步骤、示例、参考文本，能显著改善输出。
- **RAG 的核心是检索 + 生成**：离线建库，在线检索，检索结果与问题一起组装 Prompt。
- **向量检索依赖嵌入模型和相似度算法**：维度、分块大小、top-k、相似度阈值都会影响效果。
- **Java 侧用 LangChain4J**：AiServices 声明接口，配合会话记忆、RAG 检索器和 Tools 完成复杂应用。
- **图片说明**：本模块图片统一存放在 `D:\Java\data\AI\`，正文使用 `file:///` 绝对路径引用。

## 来源

- `AI/01提示词工程.pptx`（96 页）
- `AI/02大模型RAG开发.pptx`（114 页）
- `AI/03RAG项目.pptx`（10 页）
- `AI/LangChain4J+通义千问大模型应用开发(志愿填报大师).pptx`（132 页）

---

> 📎 **相关笔记**：[[JavaSE/JavaSE 索引|JavaSE]] · [[检索/检索中心|检索中心]]
