# RAG 实战项目：服装商品智能客服

> 来源：`AI/03RAG项目.pptx`（10 页，含多页动画重复）。原 PPT 只讲项目需求、代码文件职责和离线/在线流程，没有给出完整源码；本笔记只整理 PPT 明确出现的内容，未补写实现细节。
>
> 原理前置：[[02-大模型RAG开发]]；Java 版实现思路：[[04-LangChain4J与通义千问]]，其讲义级深化版为 [[05-LangChain4j核心]]。

## 1. 项目目标

项目以“某东商品衣服”为例，用衣服属性构建本地知识库：

- 使用者可以自由更新本地知识。
- 用户问题的答案基于本地知识生成。
- 通过 RAG 把“本地知识检索”和“大模型生成”结合起来，降低幻觉、补充私有知识。

项目名称在 PPT 中为“RAG 实战项目”，演示界面标题为“服装商品智能客服”。

## 2. RAG 回顾

RAG 即检索、增强和生成，分为两条线：

- **离线处理**：向私有知识库（向量存储）持续添加私有知识文档。
  - 添加来自模型训练完成时间之后的“未来知识”。
  - 添加模型未覆盖的私有知识。
  - 为模型提供参考资料，规避“一本正经地胡说八道”。
- **在线处理**：用户提问后，先基于私有知识库检索参考资料，再组装新的提示词询问大模型，获取结果。

## 3. 项目整体思路

PPT 第 3 页给出的离线/在线流程：

| 流程 | 步骤 |
| --- | --- |
| 离线 | 本地知识文件 → 加载和读取 → 文本切分 → 向量数据库 |
| 在线 | Query 向量化 → 向量匹配 → Prompt 工程 → 提交 LLM 生成答案 |

![服装商品智能客服界面](file:///D:/Java/data/AI/03-RAG项目/slide-005-img-01.png)

图 3-1 项目演示界面：用户输入“体重170斤，尺码推荐”，客服基于知识库回答（PPT 第 5 页）

## 4. 代码文件职责

PPT 第 4 页列出项目主要文件：

| 文件 | 职责 |
| --- | --- |
| `app_file_upload.py` | 知识库更新主程序（Streamlit） |
| `app_qa.py` | 项目主程序（Streamlit），启动对话 Web 页面 |
| `config_data.py` | 配置文件 |
| `file_history_store.py` | 长期会话记忆存储服务 |
| `knowledge_base.py` | 知识库更新服务 |
| `rag.py` | RAG 核心服务 |
| `vector_stores.py` | 向量存储服务 |

## 5. 离线流程：知识库更新

![离线流程](file:///D:/Java/data/AI/03-RAG项目/slide-007-img-02.png)

图 3-2 文件上传、MD5 校验、文本切分并写入 Chroma 的离线流程（PPT 第 7 页）

按图中标注，离线流程的关键对象和调用关系是：

1. `app_file_upload.py` 使用 Streamlit 开发 Web 上传页面。
2. `st.file_uploader()` 接收上传文件，`uploader_file.get_value()` 取得文件内容。
3. 调用 `KnowledgeBaseService` 实例的 `upload_by_str(self, data, filename)`。
4. `KnowledgeBaseService` 内部：
   - `get_string_md5(str)`：计算内容 MD5。
   - `check_md5()`：校验是否已处理过，避免重复入库。
   - `save_md5()`：保存 MD5 记录，图中对应 `md5.text`。
   - `self.chroma`：Chroma 向量库。
   - `self.splitter`：文本分割器。
5. 处理后的文本片段写入 Chroma 向量库。

> 这张图能说明“为什么要 MD5”：上传同一份知识文件时，先按内容摘要判断是否已经入库，避免向量库重复膨胀。

## 6. 在线流程：问答

![在线流程](file:///D:/Java/data/AI/03-RAG项目/slide-010-img-01.png)

图 3-3 在线问答的检索器、提示词模板、聊天模型与执行链（PPT 第 10 页）

按图中标注，在线流程的核心对象是：

| 对象/方法 | 作用 |
| --- | --- |
| `app_qa.py` | Streamlit 聊天页面入口 |
| `def get_retriever` | 返回检索器，用于加入链 |
| `self.vector_service` | 向量存储服务，连接 Chroma 向量库 |
| `self.prompt_template` | 提示词模板 |
| `self.chat_model` | 聊天模型 |
| `self.chain` | 由检索器、提示词模板、聊天模型组合而成的执行链 |
| `def __get_chain()` | 获得执行链 |
| `streamlit 聊天UI` | 通过 `invoke` 调用 `self.chain` |
| `def add_messages` / `def messages` / `def clear` | 会话消息的添加、读取、清除 |

数据流可以概括为：

```text
用户问题
  → Chroma 向量库检索相关片段（get_retriever / vector_service）
  → 问题 + 参考片段填入 prompt_template
  → chat_model 生成回答
  → self.chain 通过 invoke 返回给 Streamlit 聊天 UI
```

会话历史由 `file_history_store.py` 负责长期存储，消息管理接口为 `add_messages`、`messages`、`clear`。

## 7. 补充：项目结构与关键代码骨架（非原 PPT）

> 补充（非原 PPT）：原 PPT 只有 10 页，未提供源码。下面按 PPT 中的文件职责和流程图补写一套最小可运行骨架，类名和方法名尽量沿用 PPT；它不是课程源码，实际项目需按自己的配置调整。

### 7.1 推荐目录结构

```text
rag_project/
├─ app_file_upload.py        # 知识库更新页（Streamlit）
├─ app_qa.py                 # 在线问答页（Streamlit）
├─ config_data.py            # 配置：模型、路径、切分参数
├─ file_history_store.py     # 会话历史持久化
├─ knowledge_base.py         # 离线入库服务
├─ rag.py                    # 在线 RAG 链
├─ vector_stores.py          # Chroma 向量库服务
├─ data/                     # 原始知识文件
├─ chroma_db/                # Chroma 持久化目录
├─ md5.text                  # 已入库文件摘要
└─ requirements.txt
```

### 7.2 配置：config_data.py

```python
import os

from dotenv import load_dotenv

load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
CHAT_MODEL = "qwen-plus"
EMBEDDING_MODEL = "text-embedding-v3"
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "knowledge"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
TOP_K = 3
SCORE_THRESHOLD = 0.5
MD5_FILE = "./md5.text"
```

### 7.3 向量库服务：vector_stores.py

```python
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings

from config_data import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    TOP_K,
    SCORE_THRESHOLD,
)


class VectorStoreService:
    def __init__(self):
        self.embedding = DashScopeEmbeddings(model=EMBEDDING_MODEL)
        self.store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embedding,
            persist_directory=CHROMA_DIR,
        )

    def add_documents(self, documents):
        self.store.add_documents(documents)

    def get_retriever(self):
        return self.store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": TOP_K, "score_threshold": SCORE_THRESHOLD},
        )
```

### 7.4 离线入库：knowledge_base.py

```python
import hashlib
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config_data import CHUNK_OVERLAP, CHUNK_SIZE, MD5_FILE


class KnowledgeBaseService:
    def __init__(self, vector_service):
        self.vector_service = vector_service
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""],
        )

    def _load_md5(self) -> set[str]:
        path = Path(MD5_FILE)
        if not path.exists():
            return set()
        return set(path.read_text(encoding="utf-8").splitlines())

    def _save_md5(self, md5: str) -> None:
        with open(MD5_FILE, "a", encoding="utf-8") as f:
            f.write(md5 + "\n")

    def upload_by_str(self, data: str, filename: str) -> bool:
        md5 = hashlib.md5(data.encode("utf-8")).hexdigest()
        if md5 in self._load_md5():
            return False

        doc = Document(page_content=data, metadata={"source": filename})
        chunks = self.splitter.split_documents([doc])
        self.vector_service.add_documents(chunks)
        self._save_md5(md5)
        return True
```

### 7.5 会话历史：file_history_store.py

```python
import json
import os

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict


class FileChatMessageHistory(BaseChatMessageHistory):
    session_id: str
    storage_path: str

    def __init__(
        self,
        session_id: str,
        storage_path: str = "./chat_history",
        **kwargs,
    ):
        super().__init__(
            session_id=session_id,
            storage_path=storage_path,
            **kwargs,
        )
        os.makedirs(self.storage_path, exist_ok=True)

    @property
    def file_path(self) -> str:
        return os.path.join(self.storage_path, f"{self.session_id}.json")

    @property
    def messages(self) -> list[BaseMessage]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return messages_from_dict(json.load(f))
        except FileNotFoundError:
            return []

    def add_messages(self, messages) -> None:
        all_messages = list(self.messages) + list(messages)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(
                [message_to_dict(m) for m in all_messages],
                f,
                ensure_ascii=False,
            )

    def clear(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([], f)
```

### 7.6 在线 RAG 链：rag.py

```python
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory

from config_data import CHAT_MODEL
from file_history_store import FileChatMessageHistory


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


class RagService:
    def __init__(self, vector_service):
        self.vector_service = vector_service
        self.chat_model = ChatTongyi(model=CHAT_MODEL)
        self.history_store = {}

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "你是服装商品智能客服。只依据参考资料回答；资料不足时明确说明。"),
            MessagesPlaceholder("chat_history"),
            ("human", "参考资料：\n{context}\n\n问题：{input}"),
        ])

        self.chain = self._build_chain()

    def _get_history(self, session_id: str):
        if session_id not in self.history_store:
            self.history_store[session_id] = FileChatMessageHistory(session_id)
        return self.history_store[session_id]

    def _build_chain(self):
        retriever = self.vector_service.get_retriever()
        base_chain = (
            RunnablePassthrough.assign(
                context=lambda x: format_docs(retriever.invoke(x["input"]))
            )
            | self.prompt
            | self.chat_model
            | StrOutputParser()
        )
        return RunnableWithMessageHistory(
            base_chain,
            self._get_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    def stream(self, question: str, session_id: str):
        return self.chain.stream(
            {"input": question},
            config={"configurable": {"session_id": session_id}},
        )
```

### 7.7 Streamlit 页面入口

`app_qa.py`：

```python
import streamlit as st

from rag import RagService
from vector_stores import VectorStoreService

vector_service = VectorStoreService()
rag_service = RagService(vector_service)

st.title("服装商品智能客服")

if "session_id" not in st.session_state:
    st.session_state.session_id = "default"

for message in st.session_state.get("messages", []):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question := st.chat_input("请输入问题"):
    st.session_state.setdefault("messages", []).append(
        {"role": "user", "content": question}
    )
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        answer = ""
        for chunk in rag_service.stream(question, st.session_state.session_id):
            answer += chunk
            placeholder.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
```

`app_file_upload.py`：

```python
import streamlit as st

from knowledge_base import KnowledgeBaseService
from vector_stores import VectorStoreService

st.title("知识库更新")

vector_service = VectorStoreService()
kb_service = KnowledgeBaseService(vector_service)

uploaded = st.file_uploader("上传知识文件", type=["txt", "md"])
if uploaded and st.button("开始入库"):
    data = uploaded.getvalue().decode("utf-8")
    changed = kb_service.upload_by_str(data, uploaded.name)
    st.success("入库完成" if changed else "文件已存在，跳过重复入库")
```

### 7.8 运行顺序与依赖

```bash
pip install streamlit langchain langchain-community langchain-chroma langchain-text-splitters dashscope chromadb python-dotenv
streamlit run app_qa.py
```

1. 配置 `DASHSCOPE_API_KEY`。
2. 启动 `app_file_upload.py`，上传知识文件，完成切分、向量化和入库。
3. 启动 `app_qa.py`，进行在线问答。
4. 更新知识时重新上传；MD5 相同会被跳过。

本节是骨架代码。真实项目还需要处理：文件编码、PDF/Word 解析、异常处理、Chroma 集合迁移、多用户 session_id、top-k 与阈值调参。

## 8. 关键设计点

### 8.1 为什么离线、在线分开

- 离线做重活：文档加载、切分、向量化、入库，可以批量执行。
- 在线只做检索和生成，响应更快。
- 知识更新只影响离线流程，不必重新训练模型。

### 8.2 为什么要 MD5 校验

- 以内容摘要判断文件是否已经处理过。
- 避免同一份知识重复写入向量库，造成检索结果重复、存储浪费。
- `md5.text` 保存已处理文件的摘要记录。

### 8.3 为什么要文本切分

- 整篇文档太长，直接向量化会丢失细节，也不适合放入提示词。
- 切成 chunk 后，检索可以精确定位到相关段落。
- 切分器由 `KnowledgeBaseService` 的 `self.splitter` 提供。

### 8.4 会话记忆

- `file_history_store.py` 负责长期会话记忆。
- 在线流程通过 `add_messages`、`messages`、`clear` 管理历史消息。
- 这样刷新页面或重启服务后，仍能恢复之前的对话。

## 9. 项目运行思路（基于现有流程图）

PPT 没有给出启动命令和完整配置，只能确定以下运行顺序：

1. 准备本地衣服知识文件（如尺码、颜色、材质等说明）。
2. 启动 `app_file_upload.py`，上传知识文件，完成切分、向量化并写入 Chroma。
3. 启动 `app_qa.py`，打开 Streamlit 对话页面。
4. 用户提问，系统检索本地知识并调用大模型回答。
5. 需要更新知识时，重新执行上传流程；MD5 校验会跳过重复文件。

> 待确认：PPT 未提供依赖安装、环境变量、Chroma 持久化目录、模型名称等配置细节，实际运行需结合 `config_data.py` 和课程代码。

## 10. 面试题与答案要点

### 10.1 这个项目的离线流程和在线流程分别做什么？

- 离线：加载本地知识文件 → 文本切分 → 向量化 → 写入 Chroma；用 MD5 避免重复入库。
- 在线：用户提问 → 检索 Chroma → 拼接提示词 → 调用大模型 → 返回答案；同时管理会话历史。

### 10.2 为什么用向量数据库而不是关键词检索？

- 向量检索按语义相似度匹配，能处理同义表达和自然语言问法。
- 关键词检索依赖字面匹配，用户换个说法就可能检索不到。
- 课程项目用 Chroma 作为轻量向量库，适合快速搭建。

### 10.3 如何避免重复上传导致知识库膨胀？

- 对文件内容计算 MD5。
- 用 `md5.text` 记录已处理的摘要。
- 上传前先 `check_md5()`，已存在则跳过，未存在才 `save_md5()` 并入库。

### 10.4 会话记忆为什么要单独做？

- 大模型本身无状态，不会自动记住上一轮对话。
- 要把历史消息和新问题一起发给模型。
- `file_history_store.py` 把会话持久化，避免服务重启后记忆丢失。

## 11. 易错点与缺口

- PPT 只有 10 页且多页是动画重复，**没有完整源码**；第 7 节的骨架是按流程图补写，不是课程源码。
- 上传流程中 MD5 校验与向量入库的先后顺序，补充代码按“先检查 MD5 → 入库 → 记录 MD5”实现，实际以课程源码为准。
- `app_file_upload.py` 和 `app_qa.py` 都是 Streamlit 应用，注意端口和启动方式不要冲突。
- 知识文件更新后，要确认 Chroma 持久化目录和 MD5 记录同步更新。
- 在线链中检索器的 `top_k`、相似度阈值等参数 PPT 未给出，骨架中给了默认值，需按实际数据调参。

---

> 📎 **相关笔记**：[[05-LangChain4j核心]] · [[02-大模型RAG开发]] · [[AI/AI 索引|AI 索引]]
