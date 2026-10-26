---
aliases:
  - RAG
  - LangChain
  - 向量数据库
---

# 大模型 RAG 开发（LangChain 篇）

> 来源：`AI/02大模型RAG开发.pptx`（114 页）。本笔记按“RAG 原理 → 向量与相似度 → LangChain 组件 → 文档入库 → 检索生成”的主线整理。原 PPT 在 `RunnablePassthrough` 处结束，尚未给出完整的检索链代码，相关缺口在文末标注。
>
> 前置：[[01-提示词工程]]；完整项目落地：[[03-RAG项目]]；Java 技术栈的同类实现：[[04-LangChain4J与通义千问]]，其讲义级深化版为 [[05-LangChain4j核心]]。

## 1. RAG 要解决什么问题

通用基础大模型存在四类问题：

1. **领域知识缺乏**：训练数据主要来自公开互联网和开源数据集，覆盖不到企业内部或高度专业化的知识。
2. **知识过时**：模型训练完成后不会自动更新知识，信息有截止时间。
3. **幻觉**：模型会生成看似合理但实际错误的内容。
4. **数据安全**：直接依赖云端通用模型，企业私有数据存在安全顾虑。

![RAG 的四大问题与对应能力](file:///D:/Java/data/AI/02-大模型RAG开发/slide-002-img-01.png)

图 2-1 RAG 用“领域知识与私有数据、实时数据、减少不确定性、增强数据安全”对应解决四大问题（PPT 第 2 页）

RAG（Retrieval-Augmented Generation，检索增强生成）为大模型提供从特定数据源检索到的信息，用来修正和补充生成的答案。课程给出的公式是：

```text
RAG = 检索技术 + LLM 提示
```

核心价值：

- 解决知识时效性：接入最新文档，让输出“与时俱进”。
- 降低幻觉：回答基于检索到的事实资料，而不是纯靠模型记忆。
- 无需重新训练模型：相比微调，只需更新知识库，成本更低、效率更高。

## 2. RAG 标准流程

RAG 分为三个核心阶段：

| 阶段 | 主要动作 |
| --- | --- |
| 索引（Indexing） | 加载多种来源、多种格式的文档 → 提取文本 → 切分为 chunk → 向量化（embedding）→ 存入向量数据库 |
| 检索（Retrieval） | 用户 query 向量化 → 在向量库中做相似度匹配 → 返回 top-k 相关文本块 |
| 生成（Generation） | 检索结果与原始问题一起组装成 Prompt → 输入 LLM → 生成有上下文依据的回答 |

![RAG 标准流程](file:///D:/Java/data/AI/02-大模型RAG开发/slide-003-img-02.png)

图 2-2 RAG 的索引、检索、生成三阶段（PPT 第 3 页）

从工程视角还可以分成两条线：

- **离线准备线**：文档/私有知识加载 → 分割 → 向量化 → 向量数据库。
- **在线服务线**：用户提问 → 检索环节 → Prompt 融合 → 大模型回答。

![RAG 离线与在线两条线](file:///D:/Java/data/AI/02-大模型RAG开发/slide-004-img-01.png)

图 2-3 离线构建向量库、在线检索并生成回答（PPT 第 4 页）

## 3. 向量与相似度

### 3.1 向量是什么

向量（Vector）可以理解为文本的“数学身份证”：把一段文字的语义信息转换成一串固定长度的数字列表，让计算机能计算文本之间的语义相似度。

- 离线：知识/信息 → 向量嵌入 → 存入向量库。
- 在线：用户提问 → 向量嵌入 → 在向量库中匹配。

向量嵌入一般由文本嵌入模型完成，例如 `text-embedding-v1`。维度表示模型用多少个抽象语义特征描述文本：

- 维度越多，语义特征记录得越细，匹配通常越精准。
- 维度越多，计算、存储和匹配的压力越大。
- 需要在精度和性能之间平衡；课程认为 1536 维是比较实用的选择。

### 3.2 余弦相似度

余弦相似度衡量两个向量方向的接近程度，撇除向量长度的影响：

```text
cos(θ) = (A · B) / (||A|| × ||B||)
```

其中：

- 点积 `A · B`：同维度乘积之和。
- 模长 `||A||`：各维平方和再开根号。

课程例子：

- `A = [0.5, 0.5]`，`B = [0.7, 0.7]`：同向不同长，余弦相似度为 `1.0`。
- `A` 与 `C = [0.7, 0.5]`：约 `0.986`。
- `A` 与 `D = [-0.6, -0.5]`：约 `-0.996`，方向相反。

余弦相似度越大，向量方向越接近，文本语义通常越相似。

## 4. 向量数据库选型

课程给出了一张向量数据库/混合搜索数据库的对比表：

| 数据库名称 | 开源/商业 | 主要语言 | 核心特点 | 部署方式 | 混合搜索 | 适用场景 |
| --- | --- | --- | --- | --- | --- | --- |
| Weaviate | 开源 | Go | AI 原生，多模态支持 | 云/Docker/K8s/嵌入式 | 支持 | 复杂 RAG 应用 |
| Qdrant | 开源 | Rust | 高性能，稀疏向量支持 | 云/Docker | 支持 | 大规模向量搜索 |
| Milvus | 开源 | Go/C++ | 专为向量搜索优化 | 云/Docker/K8s | 支持 | 大规模 AI 应用 |
| MyScale | 商业 | - | SQL 兼容，高性能 | 云/自托管 | 支持 | SQL 开发者 |
| pgvector | 开源 | C | PostgreSQL 扩展 | 任何 PostgreSQL 环境 | 支持 | PostgreSQL 用户 |
| pgvector-rs | 开源 | Rust | 高维向量支持 | PostgreSQL 扩展 | 支持 | 需要高维搜索 |
| Chroma | 开源 | Python | 轻量级，易用 | 云/本地 | 支持 | 快速原型开发 |
| OpenSearch | 开源 | Java | 搜索分析一体化 | 云/自托管 | 支持 | 企业搜索应用 |
| TiDB Vector | 商业 | Go | 统一数据管理 | 云/Serverless/专享 | 支持 | 分布式 AI 应用 |
| Elasticsearch | 商业 | Java | 成熟搜索引擎 | 云/自托管 | 支持 | 企业级搜索 |

> 表中内容按 PPT 第 5 页图片转写；实际选型还应结合团队技术栈、数据规模、运维成本和是否已有数据库生态。

## 5. LangChain 入门

### 5.1 LangChain 是什么

LangChain 由 Harrison Chase 于 2022 年 10 月创建，是围绕 LLM 建立的开发框架。它本身不开发 LLM，而是为各种 LLM 提供统一接口，把相关组件“链接”在一起，降低复杂 LLM 应用的开发难度。

六个主要功能：

| 组件 | 作用 |
| --- | --- |
| Prompts | 优化提示词（提示词工程） |
| Models | 调用各类模型 |
| History / Memory | 管理会话历史记录 |
| Indexes | 管理和分析各类文档 |
| Chains | 构建功能的执行链条 |
| Agent | 构建智能体 |

### 5.2 安装

```bash
pip install langchain langchain-community langchain-ollama langchain-chroma dashscope chromadb bs4 jq
```

| 包 | 作用 |
| --- | --- |
| `langchain` | 核心包 |
| `langchain-community` | 社区支持包，提供更多第三方模型调用（阿里云千问需要） |
| `langchain-ollama` | Ollama 支持包，调用本地模型 |
| `langchain-chroma` | ChromaDB 支持包 |
| `dashscope` | 阿里云通义千问 Python SDK |
| `chromadb` | 轻量向量数据库 |
| `bs4` | BeautifulSoup4，协助解析 HTML 文档 |

## 6. Models：三类模型

LangChain 把模型分为三类：

| 类型 | 输入/输出 | 典型用途 |
| --- | --- | --- |
| LLMs（大语言模型） | 文本 → 文本 | 文本生成 |
| Chat Models（聊天模型） | 消息列表 → 消息 | 多轮对话 |
| Embeddings Models（嵌入模型） | 文本 → 向量 | 文本向量化、语义检索 |

### 6.1 大语言模型

阿里云通义：

```python
from langchain_community.llms.tongyi import Tongyi

llm = Tongyi(model='qwen-max')
res = llm.invoke("帮我讲个笑话吧")
print(res)
```

Ollama 本地模型：

```python
from langchain_ollama import OllamaLLM

model = OllamaLLM(model="qwen3:4b")
res = model.invoke(input="你是谁呀能做什么？")
print(res)
```

### 6.2 invoke 与 stream

| 方法 | 行为 |
| --- | --- |
| `invoke` | 一次返回完整结果 |
| `stream` | 逐段返回，流式输出 |

```python
from langchain_community.llms.tongyi import Tongyi

model = Tongyi(model="qwen-max")  # qwen3-max 是聊天模型，qwen-max 是大语言模型
res = model.stream(input="你是谁呀能做什么？")

for chunk in res:
    print(chunk, end="", flush=True)
```

这两个方法是新版 LangChain（1.0 之后）基于 `Runnable` 接口的通用核心方法，提示词模板、链、检索器、工具调用等大多支持。

### 6.3 聊天模型与消息类型

| LangChain 消息类 | 对应 OpenAI 角色 | 说明 |
| --- | --- | --- |
| `SystemMessage` | `system` | 指定模型所处环境、背景、角色和规则 |
| `HumanMessage` | `user` | 用户输入 |
| `AIMessage` | `assistant` | AI 的回答，也可由开发者预先设定 |

```python
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

chat = ChatTongyi(model="qwen3-max")

messages = [
    SystemMessage(content="你是一名来自边塞的诗人"),
    HumanMessage(content="给我写一首唐诗"),
    AIMessage(content="锄禾日当午，汗滴禾下土，谁知盘中餐，粒粒皆辛苦。"),
    HumanMessage(content="给予你上一首的格式，再来一首"),
]

for chunk in chat.stream(input=messages):
    print(chunk.content, end="", flush=True)
```

消息也可以用二元组简写：

```python
messages = [
    ("system", "你是一个边塞诗人。"),
    ("human", "写一首唐诗"),
    ("ai", "锄禾日当午，汗滴禾下土，谁知盘中餐，粒粒皆辛苦。"),
    ("human", "按照你上一个回复的格式，再写一首唐诗。"),
]
```

简写的优势是少导包、写法简单；由于是动态转换，简写形式还支持运行时填充 `{变量}` 占位，后续提示词模板会用到。

### 6.4 嵌入模型

```python
from langchain_community.embeddings import DashScopeEmbeddings

embed = DashScopeEmbeddings()  # 默认使用 text-embedding-v1
print(embed.embed_query("我喜欢你"))
print(embed.embed_documents(['我喜欢你', '我稀饭你', '晚上吃啥']))
```

本地 Ollama：

```python
from langchain_ollama import OllamaEmbeddings

embed = OllamaEmbeddings(model="qwen3-embedding")
print(embed.embed_query("我喜欢你"))
print(embed.embed_documents(['我喜欢你', '我稀饭你', '晚上吃啥']))
```

三类模型的导入与调用方式汇总（PPT 第 41 页）：

| 方式 | LLMs 大语言模型 | 聊天模型 | 文本嵌入模型 |
| --- | --- | --- | --- |
| 阿里云千问 | `from langchain_community.llms.tongyi import Tongyi` | `from langchain_community.chat_models.tongyi import ChatTongyi` | `from langchain_community.embeddings import DashScopeEmbeddings` |
| Ollama 本地模型 | `from langchain_ollama import OllamaLLM` | `from langchain_ollama import ChatOllama` | `from langchain_ollama import OllamaEmbeddings` |
| 方法 | `invoke` 批量 / `stream` 流式 | `invoke` 批量 / `stream` 流式 | `embed_query` 单次 / `embed_documents` 批量 |

## 7. Prompts：提示词模板

### 7.1 PromptTemplate（Zero-shot）

```python
from langchain_core.prompts import PromptTemplate
from langchain_community.llms.tongyi import Tongyi

prompt_template = PromptTemplate.from_template(
    "我的邻居姓{lastname}, 刚生了{gender}, 帮忙起名字，请简略回答。"
)

# 方式一：format 生成提示词文本
prompt_text = prompt_template.format(lastname="张", gender="女儿")
model = Tongyi(model="qwen-max")
res = model.invoke(input=prompt_text)
print(res)

# 方式二：基于链的写法
chain = prompt_template | model
res = chain.invoke(input={"lastname": "曹", "gender": "女儿"})
print(res)
```

模板的价值：

- 大型工程中更容易做标准化模板。
- 支持 LangChain 的链式调用（Runnable 接口）。
- 比手动拼接字符串更易维护。

### 7.2 FewShotPromptTemplate

核心参数：

| 参数 | 含义 |
| --- | --- |
| `examples` | 示例数据，list 内套字典 |
| `example_prompt` | 示例数据的提示词模板 |
| `prefix` | 组装提示词时，示例数据前的内容 |
| `suffix` | 组装提示词时，示例数据后的内容 |
| `input_variables` | 需要注入的变量列表 |

```python
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_community.chat_models.tongyi import ChatTongyi

example_template = PromptTemplate(
    input_variables=['word', 'antonym'],
    template="word: {word}, antonym: {antonym}",
)

example_data = [
    {"word": "大", "antonym": "小"},
    {"word": "上", "antonym": "下"},
]

few_shot_prompt = FewShotPromptTemplate(
    examples=example_data,
    example_prompt=example_template,
    prefix="给出给定词的反义词，有如下示例：",
    suffix="基于示例告诉我：{input_word}的反义词是？",
    input_variables=['input_word'],
)

prompt_text = few_shot_prompt.invoke(input={"input_word": "左"}).to_string()
print(prompt_text)

model = ChatTongyi(model="qwen3-max")
for chunk in model.stream(input=prompt_text):
    print(chunk.content, end="", flush=True)
```

### 7.3 ChatPromptTemplate 与 MessagesPlaceholder

`ChatPromptTemplate` 支持注入任意数量的历史会话消息；`from_messages` 可以接入一个消息 list，而 `PromptTemplate.from_template` 只能接入一条消息。

历史会话是动态增长的，使用 `MessagesPlaceholder` 占位：

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

chat_template = ChatPromptTemplate.from_messages([
    ("system", "........"),
    ("ai", "........"),
    MessagesPlaceholder("history"),
    ("human", "........"),
])

history_data = [
    ("human", "..."),
    ("ai", "..."),
    ("human", "..."),
    ("ai", "..."),
]

prompt_value = chat_template.invoke({"history": history_data})
```

> 必须用 `invoke` 注入 `history`；`format` 无法处理 `MessagesPlaceholder`。

### 7.4 format 与 invoke 的区别

| 区别 | format | invoke |
| --- | --- | --- |
| 功能 | 纯字符串替换，解析占位符生成提示词 | Runnable 接口标准方法，解析占位符生成提示词 |
| 返回值 | 字符串 | `PromptValue` 类对象 |
| 传参 | `.format(k=v, k=v, ...)` | `.invoke({"k": v, "k": v, ...})` |
| 解析 | 支持解析 `{}` 占位符 | 支持解析 `{}` 占位符和 `MessagesPlaceholder` 结构化占位符 |

## 8. Chains：把组件串起来

### 8.1 链的原理

“上一个组件的输出作为下一个组件的输入”是 LangChain 链（尤其是 `|` 管道链）的核心。示例：

```python
chain = chat_prompt_template | model
```

- `|` 本质是 `__or__` 运算符重载。
- 能入链的组件必须是 `Runnable` 子类；`Callable`、`Mapping` 子类也可以加入。
- 得到的 `chain` 是 `RunnableSerializable`（`Runnable` 子类），可用 `invoke` 或 `stream` 触发整条链。

![Runnable 继承关系](file:///D:/Java/data/AI/02-大模型RAG开发/slide-060-img-01.png)

图 2-4 LangChain 各组件的 Runnable 继承关系（PPT 第 60 页）

![链的执行流程](file:///D:/Java/data/AI/02-大模型RAG开发/slide-061-img-01.png)

图 2-5 `chat_prompt_template | model` 的输入输出流转（PPT 第 61 页）

```python
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.base import RunnableSerializable

chat_prompt_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个边塞诗人，可以作诗。"),
    MessagesPlaceholder("history"),
    ("human", "请再来一首唐诗，无需额外输出"),
])

history_data = [
    ("human", "你来写一个唐诗"),
    ("ai", "床前明月光，疑是地上霜，举头望明月，低头思故乡"),
    ("human", "好诗再来一个"),
    ("ai", "锄禾日当午，汗滴禾下锄，谁知盘中餐，粒粒皆辛苦"),
]

model = ChatTongyi(model="qwen3-max")
chain: RunnableSerializable = chat_prompt_template | model
print(type(chain))

res = chain.invoke({"history": history_data})
print(res.content)

for chunk in chain.stream({"history": history_data}):
    print(chunk.content, end="", flush=True)
```

### 8.2 `|` 运算符重载

`a | b` 本质调用 `a.__or__(b)`。自定义 `__or__` 可以让 `a | b | c` 收集成一个序列对象：

```python
class Test(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Test({self.name})"

    def __or__(self, other):
        return MySequence(self, other)


class MySequence(object):
    def __init__(self, *args):
        self.sequence = []
        for arg in args:
            self.sequence.append(arg)

    def __or__(self, other):
        self.sequence.append(other)
        return self

    def run(self):
        for arg in self.sequence:
            print(arg)


if __name__ == "__main__":
    a = Test("a")
    b = Test("b")
    c = Test("c")

    d = a | b | c
    d.run()
    print(type(d))
```

### 8.3 StrOutputParser

问题代码：

```python
chain = prompt | model | model
res = chain.invoke({"lastname": "张", "gender": "女儿"})
```

运行报错：

```text
ValueError: Invalid input type <class 'langchain_core.messages.ai.AIMessage'>. Must be a PromptValue, str, or list of BaseMessages.
```

原因：`prompt` 输出 `PromptValue`，模型输出 `AIMessage`；而 `ChatTongyi.invoke` 的输入类型是：

```python
LanguageModelInput = PromptValue | str | Sequence[MessageLikeRepresentation]
```

`AIMessage` 不能直接作为下一个模型的输入，需要类型转换：

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
chain = prompt | model | parser | model
```

`StrOutputParser` 把 `AIMessage` 转成字符串，且本身是 `Runnable` 子类，可以加入链。

### 8.4 JsonOutputParser 与多模型链

如果第二个提示词模板需要字典输入，`StrOutputParser` 不够，应使用 `JsonOutputParser`：

```python
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models.tongyi import ChatTongyi

str_parser = StrOutputParser()
json_parser = JsonOutputParser()
model = ChatTongyi(model="qwen3-max")

first_prompt = PromptTemplate.from_template(
    "我邻居姓：{lastname}，刚生了{gender}，请起名，并封装到JSON格式返回给我，"
    "要求key是name，value就是起的名字。请严格遵守格式要求"
)
second_prompt = PromptTemplate.from_template("姓名{name}，请帮我解析含义。")

chain = first_prompt | model | json_parser | second_prompt | model | str_parser

res: str = chain.invoke({"lastname": "张", "gender": "女儿"})
print(res)
print(type(res))
```

链上各环节的类型要求：

| 组件 | 输入 | 输出 |
| --- | --- | --- |
| 提示词模板 | 字典 | `PromptValue` |
| 模型 | `PromptValue` / 字符串 / 消息序列 | `AIMessage` |
| `StrOutputParser` | `AIMessage` | 字符串 |
| `JsonOutputParser` | `AIMessage` | 字典 |

### 8.5 RunnableLambda 与函数入链

除内置解析器外，可以用 `RunnableLambda` 把普通函数或 lambda 转成 Runnable：

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models.tongyi import ChatTongyi

str_parser = StrOutputParser()
my_func = RunnableLambda(lambda ai_msg: {"name": ai_msg.content})

model = ChatTongyi(model="qwen3-max")

first_prompt = PromptTemplate.from_template(
    "我邻居姓：{lastname}，刚生了{gender}，请起名，仅告知我名字，不要额外信息"
)
second_prompt = PromptTemplate.from_template("姓名{name}，请帮我解析含义。")

chain = first_prompt | model | my_func | second_prompt | model | str_parser

res: str = chain.invoke({"lastname": "张", "gender": "女儿"})
print(res)
print(type(res))
```

函数也可以直接入链：

```python
chain = first_prompt | model | (lambda ai_msg: {"name": ai_msg.content}) | second_prompt | model | str_parser
```

因为 `Runnable.__or__` 支持 `Callable` 实例，函数会自动转换为 `RunnableLambda`。

## 9. Memory：会话记忆

### 9.1 临时记忆：RunnableWithMessageHistory

大模型本身不具备记忆能力。要让模型记住之前聊的内容，只能把历史消息和新提示词一起发送。

LangChain 提供：

- `RunnableWithMessageHistory`：在原有链基础上包一层，得到带历史记录功能的新链。
- `InMemoryChatMessageHistory`：基于内存存储历史（临时，程序退出即丢失）。

```python
from langchain_core.runnables.history import RunnableWithMessageHistory

conversation_chain = RunnableWithMessageHistory(
    some_chain,                       # 被附加历史消息的 Runnable，通常是 chain
    None,                             # 获取指定会话 ID 的历史会话函数
    input_messages_key="input",       # 用户输入在模板中的占位符
    history_messages_key="chat_history",  # 历史消息在模板中的占位符
)
```

完整示例：

```python
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory


def print_prompt(full_prompt):
    print("=" * 20, full_prompt.to_string(), "=" * 20)
    return full_prompt


model = ChatTongyi(model="qwen3-max")
prompt = PromptTemplate.from_template(
    "你需要根据对话历史回应用户问题。对话历史：{chat_history}。用户当前输入：{input}， 请给出回应"
)
base_chain = prompt | print_prompt | model | StrOutputParser()

chat_history_store = {}


def get_history(session_id):
    if session_id not in chat_history_store:
        chat_history_store[session_id] = InMemoryChatMessageHistory()
    return chat_history_store[session_id]


conversation_chain = RunnableWithMessageHistory(
    base_chain,
    get_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

if __name__ == '__main__':
    session_config = {"configurable": {"session_id": "user_001"}}

    print(conversation_chain.invoke({"input": "小明有一只猫"}, session_config))
    print(conversation_chain.invoke({"input": "小刚有两只狗"}, session_config))
    print(conversation_chain.invoke({"input": "共有几只宠物？"}, session_config))
```

> 在链中加入自定义函数打印提示词时，函数必须把输入原封不动返回，避免破坏原有业务。

### 9.2 长期记忆：自实现 FileChatMessageHistory

`InMemoryChatMessageHistory` 继承自 `BaseChatMessageHistory`，只在内存中临时存储。官方注释给出了基于文件的历史消息存储示例，可以自行实现 JSON 文件持久化。

核心思路：

- 以 `session_id` 为文件名，不同会话存不同文件。
- 继承 `BaseChatMessageHistory`，实现三个方法：
  - `add_messages`：添加消息。
  - `messages`：获取消息。
  - `clear`：清除消息。

```python
import json
import os
from typing import Sequence

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, messages_from_dict, message_to_dict


class FileChatMessageHistory(BaseChatMessageHistory):
    storage_path: str
    session_id: str

    @property
    def messages(self) -> list[BaseMessage]:
        try:
            with open(
                os.path.join(self.storage_path, self.session_id),
                "r",
                encoding="utf-8",
            ) as f:
                messages_data = json.load(f)
                return messages_from_dict(messages_data)
        except FileNotFoundError:
            return []

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        all_messages = list(self.messages)
        all_messages.extend(messages)

        serialized = [message_to_dict(message) for message in all_messages]
        file_path = os.path.join(self.storage_path, self.session_id)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(serialized, f)

    def clear(self) -> None:
        file_path = os.path.join(self.storage_path, self.session_id)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f)
```

接入链：

```python
def get_message_history(session_id: str) -> BaseChatMessageHistory:
    return FileChatMessageHistory(session_id=session_id, storage_path="./chat_history")


conversation_chain = RunnableWithMessageHistory(
    runnable=base_chain,
    get_session_history=get_message_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)
```

## 10. Document Loaders：文档加载器

### 10.1 Document 与 BaseLoader

文档加载器把不同来源（CSV、PDF、JSON、文本等）的数据读取为 LangChain 的 `Document`。所有加载器实现 `BaseLoader` 接口，最终返回 `Document` 实例。

```python
from langchain_core.documents import Document

document = Document(
    page_content="Hello, world!",
    metadata={"source": "https://example.com"},
)
```

`Document` 的核心字段：

- `page_content`：文档内容。
- `metadata`：文档元数据（字典）。

统一接口：

| 方法 | 说明 |
| --- | --- |
| `load()` | 一次性加载全部文档，返回 list |
| `lazy_load()` | 延迟流式传输，返回生成器，适合大数据集，避免内存溢出 |

### 10.2 CSVLoader

```python
from langchain_community.document_loaders.csv_loader import CSVLoader

loader = CSVLoader(file_path="./xxx.csv")
data = loader.load()
print(data)
```

自定义解析参数：

```python
loader = CSVLoader(
    file_path="./xxx.csv",
    csv_args={
        "delimiter": ",",
        "quotechar": '"',
        # 无表头时使用；有表头勿用，否则会把首行当数据
        "fieldnames": ["name", "age", "gender"],
    },
)
data = loader.load()
print(data)
```

### 10.3 JSONLoader 与 jq 语法

`JSONLoader` 依赖 `jq`：

```bash
pip install jq
```

常用 jq 语法：

| 表达式 | 含义 |
| --- | --- |
| `.` | 整个 JSON 对象（根） |
| `[]` | 数组 |
| `.name` | 取根对象的 `name` |
| `.hobby` | 取爱好数组 |
| `.hobby[1]` | 取爱好数组第二个元素 |
| `.other.addr` | 取嵌套对象中的地址 |
| `.[]` | 取出数组中的每个 JSON 对象 |
| `.[].name` | 取出数组中每个对象的 `name` |

```python
from langchain_community.document_loaders import JSONLoader

loader = JSONLoader(
    file_path="xxx.json",
    jq_schema=".",
    text_content=False,  # 抽取的是否是字符串，默认 True
    json_lines=True,     # 是否是 JsonLines 文件（每行一个 JSON）
)
```

JsonLines 示例：

```json
{"name": "周杰轮", "age": 11, "gender": "男"}
{"name": "蔡依临", "age": 12, "gender": "女"}
{"name": "王力鸿", "age": 11, "gender": "男"}
```

### 10.4 PyPDFLoader

```bash
pip install pypdf
```

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader(
    file_path="",
    mode="page",          # page：按页拆成多个 Document；single：单个 Document
    password="password",  # 文件密码
)
```

### 10.5 TextLoader

`TextLoader` 读取文本文件，把全部内容放入一个 `Document`：

```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader("xxx.txt", encoding="utf-8")
docs = loader.load()
print(docs)
print(len(docs))  # 1
```

大文档只有一个 `Document` 不合适，需要文本分割器。

## 11. 文本分割：RecursiveCharacterTextSplitter

`RecursiveCharacterTextSplitter` 是 LangChain 官方推荐的默认字符分割器，按自然段落递归切分大文档，在保持上下文完整性和控制片段大小之间取得平衡。

```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = TextLoader("../P3_LangChainRAG开发/data/Python基础语法.txt", encoding="utf-8")
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # 分段最大字符数
    chunk_overlap=50,    # 相邻分段允许重叠的字符数
    separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""],
    length_function=len,
)

split_docs = splitter.split_documents(docs)
```

## 12. Vector Stores：向量存储

LangChain 为向量存储提供统一接口：

| 方法 | 作用 |
| --- | --- |
| `add_documents` / `add_texts` | 存入向量 |
| `delete` | 删除向量 |
| `similarity_search` | 相似度检索 |

### 12.1 内存向量存储 InMemoryVectorStore

```python
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.embeddings import DashScopeEmbeddings

vector_store = InMemoryVectorStore(embedding=DashScopeEmbeddings())

# 添加文档并指定 id
vector_store.add_documents(documents=[doc1, doc2], ids=["id1", "id2"])

# 按 id 删除
vector_store.delete(ids=["id1"])

# 相似性搜索，返回 4 条
similar_docs = vector_store.similarity_search("your query here", 4)
```

### 12.2 Chroma 外部向量存储

```python
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma

vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=DashScopeEmbeddings(),
    persist_directory="./chroma_langchain_db",  # 本地持久化目录，不需要可删除
)
```

### 12.3 向量存储的整体流程

![向量存储的索引与查询流程](file:///D:/Java/data/AI/02-大模型RAG开发/slide-110-img-01.png)

图 2-6 文档经嵌入模型写入 Vector stores；query 经同一嵌入模型检索 top-k（PPT 第 110 页）

## 13. 检索并构建提示词（PPT 未讲完）

PPT 最后一页只给出了思路和一段代码，未完成完整链的讲解：

1. 通过向量存储检索匹配信息。
2. 把用户提问和匹配信息一起封装到提示词模板中，再调用模型。

```python
# 准备资料（向量库的数据）
# add_texts 传入 list[str]
vector_store.add_texts(
    ["减肥就是少吃多练", "在减脂期间吃东西很重要,清淡少油控制卡路里摄入并运动起来"],
)

input_text = "怎么减肥？"

# 检索向量库
result = vector_store.similarity_search(input_text, k=2)
reference_text = "["
for doc in result:
    reference_text += doc.page_content
    reference_text += "]"

chain = prompt | print_prompt | model | StrOutputParser()
res = chain.invoke({"input": input_text, "context": reference_text})
print(res)
```

![RunnablePassthrough 相关代码截图](file:///D:/Java/data/AI/02-大模型RAG开发/slide-114-img-02.png)

图 2-7 PPT 结尾的检索链代码截图（第 114 页），原页标题为 `RunnablePassthrough`，但正文未展开

> 待确认：原 PPT 在此处结束，没有给出 `RunnablePassthrough` 的完整用法和最终可运行的 RAG 链。上图中的 `reference_text` 拼接逻辑也会多出一个 `]`，实际使用时建议改为 `"\n\n".join(doc.page_content for doc in result)`。

### 13.1 补充：RunnablePassthrough 与完整检索链（非原 PPT）

> 补充（非原 PPT）：以下检索链在 PPT 结束后补写，用于补全 `RunnablePassthrough` 的用法和可直接运行的 RAG 链。

`RunnablePassthrough` 是“原样透传输入”的 Runnable。RAG 链里常见两种写法：

1. **字典分发**：`{"context": ..., "input": RunnablePassthrough()}`，同一个问题同时进入检索分支和原始输入分支。
2. **`RunnablePassthrough.assign(...)`**：保留原输入，并追加一个新字段（例如 `context`）。

完整的检索链可以写成：

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

retriever = vector_store.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_template(
    "请只依据下面的参考资料回答问题。\n"
    "如果资料不足以回答，请明确说“资料中没有相关信息”，不要编造。\n\n"
    "参考资料：\n{context}\n\n"
    "问题：{input}"
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {
        "context": retriever | format_docs,
        "input": RunnablePassthrough(),
    }
    | prompt
    | model
    | StrOutputParser()
)

answer = rag_chain.invoke("怎么减肥？")
print(answer)
```

等价的 `assign` 写法：

```python
rag_chain = (
    RunnablePassthrough.assign(context=retriever | format_docs)
    | prompt
    | model
    | StrOutputParser()
)
```

链上各环节的类型流转：

| 环节 | 输入 | 输出 |
| --- | --- | --- |
| 字典/`assign` | `str` | `{"context": str, "input": str}` |
| `ChatPromptTemplate` | `dict` | `PromptValue` |
| 聊天模型 | `PromptValue` | `AIMessage` |
| `StrOutputParser` | `AIMessage` | `str` |

流式执行：

```python
for chunk in rag_chain.stream("怎么减肥？"):
    print(chunk, end="", flush=True)
```

关键点：

- `retriever` 本身是 Runnable，`retriever | format_docs` 把 `list[Document]` 转成字符串。
- `RunnablePassthrough` 不修改输入；`assign` 在保留原输入的基础上追加字段。
- Prompt 中的变量名必须和字典 key 一致（`context`、`input`）。
- 检索不到内容时 `context` 为空字符串，要靠 Prompt 约束模型“资料不足时明确说明”，避免幻觉。
- 原 PPT 的 `reference_text` 用循环拼接且会多出一个 `]`，建议改用 `"\n\n".join(...)`。
- 需要给答案附来源时，让检索分支同时返回原始 docs，再从 `doc.metadata["source"]` 取文件名。

## 14. 面试题与答案要点

### 14.1 RAG 的流程是什么？

- 索引：加载文档 → 提取文本 → 分割 chunk → 向量化 → 存向量库。
- 检索：query 向量化 → 相似度匹配 → 返回 top-k。
- 生成：query + 检索结果组装 Prompt → LLM 生成答案。

### 14.2 RAG 和微调怎么选？

- RAG 适合知识频繁更新、需要引用来源、私有知识库的场景；更新知识库即可，不必重新训练。
- 微调适合改变模型行为、风格、特定任务能力；需要训练数据和算力。
- 两者可以结合：微调模型能力，RAG 提供最新事实。

### 14.3 向量维度越高越好吗？

- 维度高能记录更多语义特征，匹配通常更精准。
- 但计算、存储、检索成本更高。
- 需要在精度和性能之间平衡，课程常用 1536 维。

### 14.4 LangChain 的链是什么？

- 把多个 Runnable 组件用 `|` 串联，前一个的输出作为后一个的输入。
- 链本身也是 Runnable，可用 `invoke` / `stream` 执行。
- 组件之间的输入输出类型必须兼容，必要时用 `StrOutputParser` / `JsonOutputParser` / `RunnableLambda` 转换。

### 14.5 会话记忆怎么实现？

- 临时：`RunnableWithMessageHistory` + `InMemoryChatMessageHistory`。
- 长期：实现 `BaseChatMessageHistory`，把消息序列化到文件、Redis 或数据库。
- 多会话隔离：用 `session_id` 区分不同会话。

## 15. 易错点

- `qwen3-max` 是聊天模型，`qwen-max` 是大语言模型，用错类会报错。
- 模型输出 `AIMessage`，不能直接喂给下一个聊天模型，需要解析器转换。
- 提示词模板的 `format` 与 `invoke` 返回类型不同：字符串 vs `PromptValue`。
- `MessagesPlaceholder` 只能用 `invoke` 注入，不能用 `format`。
- `TextLoader` 只产生一个 `Document`，大文档必须先分割。
- `CSVLoader` 的 `fieldnames` 只适用于无表头文件。
- `JSONLoader` 依赖 `jq`，`jq_schema` 写错会取不到数据。
- `InMemoryChatMessageHistory` 重启即丢失，生产环境要持久化。
- 文档加载器的 `load()` 可能一次占用大量内存，大文档用 `lazy_load()`。

---

> 📎 **相关笔记**：[[05-LangChain4j核心]] · [[03-RAG项目]] · [[AI/AI 索引|AI 索引]]
