---
aliases:
  - LangChain4J
  - 通义千问
  - Function Calling
---

# LangChain4J 与通义千问（志愿填报大师）

> 来源：`AI/LangChain4J+通义千问大模型应用开发(志愿填报大师).pptx`（132 页）。本笔记按“Java AI 化背景 → 大模型基础与调用 → LangChain4J 会话功能 → RAG 知识库 → Tools 工具调用”的主线整理。原 PPT 在第 130 页讲完 Tools 实现后结束，未展示完整的志愿填报项目整合；第 131 页为空，第 132 页为结束页。
>
> RAG 原理与 LangChain 版本：[[02-大模型RAG开发]]；Python 项目案例：[[03-RAG项目]]；提示词基础：[[01-提示词工程]]；同一课程的讲义级深化版：[[05-LangChain4j核心]]。

## 1. 课程定位与学习要求

课程目标：用 Java 技术栈（Spring Boot + LangChain4J）开发大模型应用，最终项目是“AI 志愿填报顾问”。

学习要求（PPT 第 15 页）：

- 必须掌握：Spring Boot + MyBatis。
- 熟练使用：IDEA + Maven。
- 初步了解：Docker + Redis + MySQL。
- JDK 17。

课程内容分三部分：

| 部分 | 内容 | 目标 |
| --- | --- | --- |
| 认识 AI | AI 发展、常见大模型、AI 市场分布 | 了解 AI 与大模型的关系，知道常见模型，找准定位 |
| 大模型使用 | 模型部署、模型调用、常见参数 | 了解部署方式区别，学会 Ollama 部署，学会 HTTP 调用，理解请求/响应 |
| LangChain4J | AI 志愿填报顾问 | 基本使用、阻塞/流式调用、会话记忆、向量模型与向量数据库、RAG 知识库、Tools 工具调用 |

## 2. 为什么 Java 需要 LangChain4J

传统 Java 应用 AI 化面临两个现实问题：

- **缺技术**：Java 领域缺少大模型应用开发的技术框架和统一标准。
- **缺人才**：既懂 Java 开发、又懂大模型应用开发的人才稀缺。

课程提到 Java 生态中的两个主要方案：**LangChain4j** 与 **Spring AI**。本课程选择 LangChain4J，官方文档：<https://docs.langchain4j.dev/>。

## 3. AI 基础

### 3.1 AI 发展史

AI（Artificial Intelligence）是让机器能够像人类一样思考、学习和解决问题的技术。

- 1950 年：图灵测试，用“测试者能否区分机器和人的回答”来判断机器智能。
- 符号主义：把现实抽象为符号，设置规则并执行。例如“如果天晴（A），就打篮球（B），否则打游戏（C）”。
- 连接主义：用神经网络模拟神经元连接。
  - 神经元结构：树突接收信息，细胞体处理，轴突传递信息，突触连接其他神经元。
  - 感知机：输入 × 权重，加上偏置/阈值，经过激活函数得到输出。
  - 多层感知机：输入层 → 多个隐藏层 → 输出层。
  - 每个神经元上的参数数量 = 权重数量 + 1（偏置）。
- 神经网络：用数据训练模型参数，参数规模从 10B 到 100B，课程用“大力出奇迹”形容大模型时代。
- 2022 年 11 月 30 日：OpenAI 发布基于 GPT-3.5 的 ChatGPT，大模型进入大众视野。

### 3.2 AI 市场分布

AI 产业可以分成三层：

| 层级 | 内容 | 课程举例 |
| --- | --- | --- |
| 基础算力 | GPU/芯片、云算力 | 英伟达、超威、寒武纪；亚马逊、阿里云、微软 |
| 核心算法 | 大模型（软件） | OpenAI、深度求索、Meta、Google |
| 智能应用 | Agent、行业应用 | 新零售、金融、教育、医疗、出行、游戏等 |

课程给出的行业覆盖包括新零售、企业服务、游戏、电信、出行、社交、旅游、工具、区块链、物联网、广告营销、汽车后市场、房地产、金融、数据服务等。

### 3.3 大模型部署方式

| 方式 | 子类 | 优势 | 劣势 |
| --- | --- | --- | --- |
| 自己部署 | 云服务器部署 | 前期成本低，维护简单 | 数据不安全，长期使用成本高 |
| 自己部署 | 本地机器部署 | 数据安全，长期成本低 | 初期成本高，维护困难 |
| 他人部署 | 第三方平台 API | 无需部署 | 数据不安全，长期成本高 |

自己部署本机模型的两种路径：

1. 手动：Python 解释器 → 安装依赖 → 手动下载模型 → 编写脚本。
2. 工具：Ollama、LM Studio 一键下载、运行大模型。

Ollama 官网：<https://ollama.com>，默认端口 `11434`。

阿里云百炼接入步骤：

1. 登录 <https://www.aliyun.com/>。
2. 开通“大模型服务平台百炼”。
3. 申请百炼平台 API-KEY。
4. 选择模型并使用。

## 4. 大模型调用：HTTP 视角

### 4.1 请求参数

调用大模型时，请求体以 JSON 形式传递。PPT 给出的示例：

```json
{
  "model": "qwen-plus",
  "messages": [
    {
      "role": "system",
      "content": "你是东哥的助手小月月"
    },
    {
      "role": "user",
      "content": "你是谁？"
    },
    {
      "role": "assistant",
      "content": "您好，有什么可以帮助您？"
    }
  ],
  "stream": true,
  "enable_search": true
}
```

| 参数 | 说明 |
| --- | --- |
| `model` | 当前调用的模型 |
| `messages` | 发送给模型的消息列表 |
| `messages[].role` | `user` 用户、`system` 系统、`assistant` 模型响应 |
| `messages[].content` | 消息内容 |
| `stream` | `true` 流式/非阻塞；`false` 阻塞/一次性响应，默认 `false` |
| `enable_search` | 联网搜索；`true` 开启，`false` 关闭（默认） |

### 4.2 直接用 HTTP 调用

![用 Apifox 调用通义千问](file:///D:/Java/data/AI/04-LangChain4J与通义千问/slide-060-img-01.png)

图 4-1 通过 `POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions` 调用 `qwen-plus`，请求体只含 system 消息，响应 200（PPT 第 60 页）

这张图说明：不依赖 Java SDK，也可以直接按 OpenAI 兼容协议发 HTTP 请求。请求地址、模型名、messages 结构与 SDK 中一致。

### 4.3 响应数据

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "我是通义千问，阿里巴巴…"
      },
      "finish_reason": "stop",
      "index": 0
    }
  ],
  "object": "chat.completion",
  "usage": {
    "prompt_tokens": 22,
    "completion_tokens": 80,
    "total_tokens": 102
  },
  "created": 1748068508,
  "system_fingerprint": null,
  "model": "qwen-plus",
  "id": "chatcmpl-99f8d040-0f49-955b-943a-21c83"
}
```

| 字段 | 说明 |
| --- | --- |
| `choices` | 模型生成内容数组，可含一条或多条 |
| `choices[].message` | 本次输出的消息 |
| `choices[].finish_reason` | `stop` 自然结束；`length` 生成内容过长 |
| `choices[].index` | 当前内容在数组中的索引 |
| `object` | 固定为 `chat.completion`，无需关注 |
| `usage` | Token 信息：`prompt_tokens` 输入、`completion_tokens` 输出、`total_tokens` 总计 |
| `created` | 会话创建时间戳 |
| `system_fingerprint` | 固定为 `null`，无需关注 |
| `model` | 本次使用的模型 |
| `id` | 本次调用的唯一标识 |

Token 是大模型处理文本的基本单位：

- 英文：一个 token ≈ 4 个字符。
- 中文：一个汉字 ≈ 1–2 个 token。

### 4.4 多轮对话与历史消息

![通过 messages 携带多轮历史](file:///D:/Java/data/AI/04-LangChain4J与通义千问/slide-082-img-01.png)

图 4-2 请求体按 system → user → assistant → user 的顺序携带历史消息（PPT 第 82 页）

大模型本身不具备记忆能力。要让模型“记住”之前聊的内容，唯一办法是把历史消息和新提示词一起发给模型。上图请求体中的 4 条消息就是最直接的历史上下文。

## 5. LangChain4J 会话功能

### 5.1 快速入门

三步：

1. 引入 `langchain4j-open-ai` 依赖。
2. 构建 `OpenAiChatModel` 对象。
3. 调用 `chat` 方法。

```xml
<dependency>
  <groupId>dev.langchain4j</groupId>
  <artifactId>langchain4j-open-ai</artifactId>
  <version>1.0.1</version>
</dependency>
```

```java
OpenAiChatModel model = OpenAiChatModel.builder()
        .baseUrl("https://dashscope.aliyuncs.com/compatible-mode/v1")
        .apiKey(System.getenv("API-KEY"))
        .modelName("qwen-plus")
        .build();

String result = model.chat("东哥帅不帅");
System.out.println(result);
```

打印请求/响应日志：

```xml
<dependency>
  <groupId>ch.qos.logback</groupId>
  <artifactId>logback-classic</artifactId>
  <version>1.5.18</version>
</dependency>
```

```java
OpenAiChatModel model = OpenAiChatModel.builder()
        .baseUrl("https://dashscope.aliyuncs.com/compatible-mode/v1")
        .apiKey(System.getenv("API-KEY"))
        .modelName("qwen-plus")
        .logRequests(true)
        .logResponses(true)
        .build();
```

### 5.2 Spring Boot 整合

1. 构建 Spring Boot 项目。
2. 引入起步依赖。
3. 在 `application.yml` 配置大模型。
4. 开发接口调用大模型。

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai-spring-boot-starter</artifactId>
    <version>1.0.1-beta6</version>
</dependency>
```

```yaml
langchain4j:
  open-ai:
    chat-model:
      base-url: https://dashscope.aliyuncs.com/compatible-mode/v1
      api-key: ${API-KEY}
      model-name: qwen-plus
      log-requests: true
      log-responses: true

logging:
  level:
    dev.langchain4j: debug
```

```java
@RestController
public class ChatController {
    @Autowired
    private OpenAiChatModel model;

    @RequestMapping("/chat")
    public String chat(String message) {
        return model.chat(message);
    }
}
```

### 5.3 AiServices：声明式接口

直接用 `OpenAiChatModel.chat()` 适合简单场景；当需要会话记忆、RAG、Tools 时，使用 `AiServices` 为接口创建代理对象。

四步：

1. 引入依赖。
2. 声明接口。
3. 使用 `AiServices` 为接口创建代理对象。
4. 在 Controller 中注入并使用。

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-spring-boot-starter</artifactId>
    <version>1.0.1-beta6</version>
</dependency>
```

```java
public interface ConsultantService {
    // 用于聊天的方法，message 为用户输入的内容
    String chat(String message);
}
```

```java
@Configuration
public class CommonConfig {
    @Autowired
    private OpenAiChatModel model;

    @Bean
    public ConsultantService consultantService() {
        return AiServices.builder(ConsultantService.class)
                .chatModel(model)
                .build();
    }
}
```

```java
@RestController
public class ChatController {
    @Autowired
    private ConsultantService consultantService;

    @RequestMapping("/chat")
    public String chat(String message) {
        return consultantService.chat(message);
    }
}
```

声明式写法：

```java
@AiService(
        wiringMode = AiServiceWiringMode.EXPLICIT,
        chatModel = "openAiChatModel"
)
public interface ConsultantService {
    String chat(String message);
}
```

### 5.4 流式调用

1. 引入 `spring-boot-starter-webflux` 和 `langchain4j-reactor`。
2. 配置流式模型对象。
3. 接口方法返回值改为 `Flux<String>`。
4. 修改 Controller。

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-reactor</artifactId>
    <version>1.0.1-beta6</version>
</dependency>
```

```yaml
langchain4j:
  open-ai:
    streaming-chat-model:
      base-url: https://dashscope.aliyuncs.com/compatible-mode/v1
      api-key: ${API-KEY}
      model-name: qwen-plus
      log-requests: true
      log-responses: true
```

```java
@AiService(
        wiringMode = AiServiceWiringMode.EXPLICIT,
        chatModel = "openAiChatModel",
        streamingChatModel = "openAiStreamingChatModel"
)
public interface ConsultantService {
    Flux<String> chat(String message);
}
```

### 5.5 消息注解

| 注解 | 作用 | 示例 |
| --- | --- | --- |
| `@SystemMessage` | 设定系统提示词 | `@SystemMessage("你是东哥的助手小月月，温柔貌美又多金。")` |
| `@SystemMessage(fromResource = ...)` | 从资源文件读取系统提示词 | `@SystemMessage(fromResource = "system.txt")` |
| `@UserMessage` | 设定用户消息模板 | `@UserMessage("...{{it}}")` |
| `@V` | 给方法参数起变量名，供模板引用 | `@UserMessage("...{{msg}}") chat(@V("msg") String message)` |

示例：

```java
@SystemMessage("你是东哥的助手小月月，温柔貌美又多金。")
Flux<String> chat(String message);

@SystemMessage(fromResource = "system.txt")
Flux<String> chat(String message);

@UserMessage("你是东哥的助手小月月，温柔貌美又多金。{{it}}")
Flux<String> chat(String message);

@UserMessage("你是东哥的助手小月月，温柔貌美又多金。{{msg}}")
Flux<String> chat(@V("msg") String message);
```

### 5.6 会话记忆

#### 临时记忆

`ChatMemory` 接口：

```java
public interface ChatMemory {
    Object id();                       // 记忆存储对象的唯一标识
    void add(ChatMessage message);     // 添加一条会话记忆
    List<ChatMessage> messages();      // 获取所有会话记忆
    void clear();                      // 清除所有会话记忆
}
```

配置 `MessageWindowChatMemory`，只保留最近 20 条消息：

```java
@Bean
public ChatMemory chatMemory() {
    return MessageWindowChatMemory.builder()
            .maxMessages(20)
            .build();
}
```

在 `@AiService` 上挂载：

```java
@AiService(
        wiringMode = AiServiceWiringMode.EXPLICIT,
        chatModel = "openAiChatModel",
        streamingChatModel = "openAiStreamingChatModel",
        chatMemory = "chatMemory"
)
public interface ConsultantService {
    @SystemMessage(fromResource = "system.txt")
    Flux<String> chat(String message);
}
```

#### 多会话隔离

上面的配置所有会话共用一个 `ChatMemory`。需要按用户/会话隔离时，使用 `ChatMemoryProvider`：

```java
@Bean
public ChatMemoryProvider chatMemoryProvider() {
    return new ChatMemoryProvider() {
        @Override
        public ChatMemory get(Object memoryId) {
            return MessageWindowChatMemory.builder()
                    .id(memoryId)
                    .maxMessages(20)
                    .build();
        }
    };
}
```

接口方法增加 `@MemoryId` 参数：

```java
@AiService(
        wiringMode = AiServiceWiringMode.EXPLICIT,
        chatModel = "openAiChatModel",
        streamingChatModel = "openAiStreamingChatModel",
        chatMemory = "chatMemory",
        chatMemoryProvider = "chatMemoryProvider"
)
public interface ConsultantService {
    @SystemMessage(fromResource = "system.txt")
    Flux<String> chat(
            @MemoryId String memoryId,
            @UserMessage String message
    );
}
```

#### 持久化到 Redis

`MessageWindowChatMemory` 把消息读写委托给 `ChatMemoryStore`：

```java
public interface ChatMemoryStore {
    List<ChatMessage> getMessages(Object memoryId);
    void updateMessages(Object memoryId, List<ChatMessage> messages);
    void deleteMessages(Object memoryId);
}
```

实现 `RedisChatMemoryStore`，重写三个方法：

```java
@Repository
public class RedisChatMemoryStore implements ChatMemoryStore {
    @Override
    public List<ChatMessage> getMessages(Object memoryId) {
        // TODO 从 Redis 获取数据
        return List.of();
    }

    @Override
    public void updateMessages(Object memoryId, List<ChatMessage> messages) {
        // TODO 更新 Redis 数据
    }

    @Override
    public void deleteMessages(Object memoryId) {
        // TODO 删除 Redis 数据
    }
}
```

准备 Redis：

```bash
docker run --name redis -d -p 6379:6379 redis
```

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

```yaml
spring:
  data:
    redis:
      host: localhost
      port: 6379
```

构建记忆对象时挂上存储：

```java
public ChatMemory get(Object memoryId) {
    return MessageWindowChatMemory.builder()
            .id(memoryId)
            .maxMessages(20)
            .chatMemoryStore(store)
            .build();
}
```

## 6. RAG 知识库

### 6.1 原理

RAG（Retrieval Augmented Generation，检索增强生成）通过检索外部知识库增强大模型的生成能力，解决通用训练数据截止和私有领域知识不足的问题。

![RAG 问答时序](file:///D:/Java/data/AI/04-LangChain4J与通义千问/slide-093-img-01.png)

图 4-3 用户提问 → AI 应用组织 Prompt → 基础大模型 → 返回响应（PPT 第 93 页）

#### 向量与余弦相似度

- 向量是表示大小和方向的量；文本经嵌入模型转换为高维向量。
- 余弦相似度用于衡量两个向量方向的接近程度：

```text
cos(θ) = (V · U) / (||V|| × ||U||)
```

课程例子：

- `V = (1, 2)`，`U = (2, 1)`：`cos(θ) = 0.8`。
- `A = (0, 2)`，`B = (2, 0)`：`cos(θ) = 0`（方向垂直）。
- 余弦相似度越大，向量方向越接近，文本相似度越高。

常用向量数据库：Milvus、Chroma、Pinecone、RedisSearch（Redis）、pgvector（PostgreSQL）。

#### 索引与检索流程

![RAG 索引流程](file:///D:/Java/data/AI/04-LangChain4J与通义千问/slide-101-img-01.png)

图 4-4 文档 → 文本分割 → Segments → 嵌入模型 → Embeddings → 向量存储（PPT 第 101 页）

![RAG 检索流程](file:///D:/Java/data/AI/04-LangChain4J与通义千问/slide-103-img-01.png)

图 4-5 Query → Query Embedding → 向量库检索 Relevant Segments → 与原始 Query 一起送入语言模型（PPT 第 103 页）

### 6.2 快速入门（Easy RAG）

存储侧：

1. 引入 `langchain4j-easy-rag` 依赖。
2. 加载知识数据文档。
3. 构建向量数据库操作对象。
4. 把文档切割、向量化并存储。

检索侧：

1. 构建向量数据库检索对象。
2. 配置检索对象。
3. 挂到 `@AiService` 的 `contentRetriever`。

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-easy-rag</artifactId>
    <version>1.0.1-beta6</version>
</dependency>
```

```java
List<Document> documents = ClassPathDocumentLoader.loadDocuments("文档路径");

InMemoryEmbeddingStore<TextSegment> store = new InMemoryEmbeddingStore<>();

EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
        .embeddingStore(store)
        .build();
ingestor.ingest(documents);

EmbeddingStoreContentRetriever retriever = EmbeddingStoreContentRetriever.builder()
        .embeddingStore(store)
        .maxResults(3)
        .minScore(0.6)
        .build();
```

```java
@AiService(
        wiringMode = AiServiceWiringMode.EXPLICIT,
        contentRetriever = "retriever"
)
public interface ConsultantService {
    String chat(String message);
}
```

### 6.3 核心 API

RAG 入库链路：

```text
文档 → Document Loader → Document Parser → Document
     → Document Splitter → TextSegment
     → EmbeddingModel → Embedding
     → EmbeddingStore
```

`EmbeddingStoreIngestor` 负责把加载、解析、分割、向量化、存储串起来。

#### 文档加载器

| 加载器 | 用途 |
| --- | --- |
| `FileSystemDocumentLoader` | 按本地磁盘绝对路径加载 |
| `ClassPathDocumentLoader` | 相对于类路径加载 |
| `UrlDocumentLoader` | 按 URL 加载 |

#### 文档解析器

| 解析器 | 用途 |
| --- | --- |
| `TextDocumentParser` | 纯文本 |
| `ApachePdfBoxDocumentParser` | PDF |
| `ApachePoiDocumentParser` | Office 文件（DOC、PPT、XLS） |
| `ApacheTikaDocumentParser` | 默认，几乎支持所有格式 |

PDF 解析依赖：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-document-parser-apache-pdfbox</artifactId>
    <version>1.0.1-beta6</version>
</dependency>
```

```java
ClassPathDocumentLoader.loadDocuments("文档路径", new ApachePdfBoxDocumentParser());
```

#### 文档分割器

| 分割器 | 依据 |
| --- | --- |
| `DocumentByParagraphSplitter` | 段落 |
| `DocumentByLineSplitter` | 行 |
| `DocumentBySentenceSplitter` | 句子 |
| `DocumentByWordSplitter` | 词 |
| `DocumentByCharacterSplitter` | 固定字符数 |
| `DocumentByRegexSplitter` | 正则表达式 |
| `DocumentSplitters.recursive(...)` | 默认，递归分割：优先段落，再行、句子、词 |

```java
DocumentSplitter documentSplitter = DocumentSplitters.recursive(
        每个片段最大容纳的字符,
        两个片段之间重叠字符的个数
);

EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
        .embeddingStore(store)
        .documentSplitter(documentSplitter)
        .build();
```

#### 向量模型

`EmbeddingModel` 把文本片段或用户输入转为向量：

```java
public interface EmbeddingModel {
    Response<Embedding> embed(String text);
    Response<Embedding> embed(TextSegment textSegment);
    Response<List<Embedding>> embedAll(List<TextSegment> texts);
    int dimension();
}
```

配置：

```yaml
langchain4j:
  open-ai:
    embedding-model:
      base-url: https://dashscope.aliyuncs.com/compatible-mode/v1
      api-key: ${API-KEY}
      model-name: text-embedding-v3
      log-requests: true
      log-responses: true
```

挂到入库和检索对象：

```java
EmbeddingStoreIngestor.builder()
        .embeddingStore(store)
        .documentSplitter(documentSplitter)
        .embeddingModel(embeddingModel)
        .build();

EmbeddingStoreContentRetriever.builder()
        .embeddingStore(store)
        .embeddingModel(embeddingModel)
        .maxResults(3)
        .minScore(0.6)
        .build();
```

#### 向量存储

`EmbeddingStore` 负责向向量数据库添加和检索：

```java
public interface EmbeddingStore<Embedded> {
    String add(Embedding embedding);
    void add(String text, Embedding embedding);
    String add(Embedding embedding, Embedded embedded);
    List<String> addAll(List<Embedding> embeddings);
    EmbeddingSearchResult<Embedded> search(EmbeddingSearchRequest request);
}
```

#### 使用 Redis 作为向量库

```bash
docker stop redis          # 停止原有 redis 镜像
docker rm redis            # 删除原有 redis 镜像
docker run --name redis-vector -d -p 6379:6379 redislabs/redisearch
```

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-redis-spring-boot-starter</artifactId>
    <version>1.0.1-beta6</version>
</dependency>
```

```yaml
langchain4j:
  community:
    redis:
      host: localhost
      port: 6379
```

## 7. Tools 工具调用

### 7.1 业务场景

志愿填报助手除了回答问题，还要能帮用户预约一对一指导：

1. 每次回答完用户问题，最后加上一句：

   > 志愿填报需要考虑的因素有很多，如果要得到专业的志愿填报指导，建议您预约一个一对一的指导服务，是否需要预约？

2. 当用户表达预约意愿后，委婉引导用户提供：考生姓名、考生性别、考生电话、考生预约沟通时间（日期+时间）、考生所在省份、考生预估分数。

3. 获取信息后，通过一对一电话沟通促成报名，并把预约信息写入 MySQL 的 `reservation` 表。

### 7.2 准备工作：预约信息服务

1. 准备数据库环境：

```bash
docker run --name mysql -d -p 3307:3306 -e MYSQL_ROOT_PASSWORD=1234 mysql
```

2. 引入 Lombok、MyBatis、MySQL 驱动依赖。
3. 配置数据源：

```yaml
spring:
  datasource:
    username: root
    password: 1234
    url: jdbc:mysql://localhost:3307/gk?useUnicode=true&characterEncoding=utf-8&useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true
    driver-class-name: com.mysql.cj.jdbc.Driver

mybatis:
  configuration:
    map-underscore-to-camel-case: true
```

4. 准备实体类、Mapper、Service，并完成测试。

Service 示例：

```java
@Service
public class ReservationService {
    @Autowired
    private ReservationMapper reservationMapper;

    public void insert(Reservation reservation) {
        reservationMapper.insert(reservation);
    }

    public Reservation findByPhone(String phone) {
        return reservationMapper.findByPhone(phone);
    }
}
```

### 7.3 原理：Function Calling

![Function Calling 时序](file:///D:/Java/data/AI/04-LangChain4J与通义千问/slide-128-img-01.png)

图 4-6 AI 应用在 Prompt 中带上函数定义，模型返回函数名和参数，应用执行函数后再次发送 Prompt（PPT 第 128 页）

流程：

1. 用户提出问题。
2. AI 应用组织 Prompt，其中包含 Function 定义（方法名称、作用、入参）。
3. 发送 Prompt 给基础大模型。
4. 模型判断是否需要调用 Function：
   - 需要：返回函数名称和参数。
   - AI 应用执行函数，把结果拼接到 Prompt。
   - 再次发送 Prompt，循环直到任务完成。
5. 模型返回最终响应，AI 应用返回给用户。

### 7.4 实现

定义工具类，用 `@Tool` 描述方法作用，用 `@P` 描述参数：

```java
@Component
public class ReservationTool {
    @Autowired
    private ReservationService reservationService;

    @Tool("添加志愿指导服务预约")
    public void addReservation(
            @P("考生姓名") String name,
            @P("考生性别") String gender,
            @P("考生电话") String phone,
            @P("沟通时间") LocalDateTime communicationTime,
            @P("考生所在省份") String province,
            @P("考生预估分数") Integer estimatedScore) {
        reservationService.insert(new Reservation(
                null, name, gender, phone, communicationTime, province, estimatedScore));
    }

    @Tool("根据考生电话查询考生预约详情")
    public Reservation findReservation(@P("考生电话") String phone) {
        return reservationService.findByPhone(phone);
    }
}
```

挂到 `@AiService`：

```java
@AiService(
        wiringMode = AiServiceWiringMode.EXPLICIT,
        tools = "reservationTool"
)
public interface ConsultantService {
    String chat(String message);
}
```

### 7.5 补充：Tools / Function Calling 完整实现要点（非原 PPT）

> 补充（非原 PPT）：PPT 讲完 `@Tool` / `@P` 和 `@AiService(tools = ...)` 就结束了，没有给出建表、实体、Mapper、Service 的完整代码，也没有展开 Function Calling 的执行细节。下面按同一门课程的第三章讲义补齐一套可运行实现，并补充工程要点。

#### 7.5.1 建表

```sql
create database if not exists gk;
use gk;

create table if not exists reservation
(
    id                 bigint      primary key auto_increment not null comment '主键ID',
    name               varchar(50)  not null comment '考生姓名',
    gender             varchar(2)   not null comment '考生性别',
    phone              varchar(20)  not null comment '考生手机号',
    communication_time datetime     not null comment '沟通时间',
    province           varchar(32)  not null comment '考生所处的省份',
    estimated_score    int          not null comment '考生预估分数'
);
```

> 库名 `gk` 与第 7.2 节的数据源 URL 保持一致；如果你按第三章讲义建库，也可以把 URL 改成 `volunteer`，两处必须一致。

#### 7.5.2 实体、Mapper、Service

实体：

```java
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Reservation {
    private Long id;
    private String name;
    private String gender;
    private String phone;
    private LocalDateTime communicationTime;
    private String province;
    private Integer estimatedScore;
}
```

Mapper：

```java
import com.itheima.consultant.pojo.Reservation;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface ReservationMapper {

    @Insert("insert into reservation(name, gender, phone, communication_time, province, estimated_score) " +
            "values(#{name}, #{gender}, #{phone}, #{communicationTime}, #{province}, #{estimatedScore})")
    void insert(Reservation reservation);

    @Select("select * from reservation where phone = #{phone}")
    Reservation findByPhone(String phone);
}
```

Service：

```java
import com.itheima.consultant.mapper.ReservationMapper;
import com.itheima.consultant.pojo.Reservation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class ReservationService {
    @Autowired
    private ReservationMapper reservationMapper;

    public void insert(Reservation reservation) {
        reservationMapper.insert(reservation);
    }

    public Reservation findByPhone(String phone) {
        return reservationMapper.findByPhone(phone);
    }
}
```

#### 7.5.3 完整 Tool 类

```java
import com.itheima.consultant.pojo.Reservation;
import com.itheima.consultant.service.ReservationService;
import dev.langchain4j.agent.tool.P;
import dev.langchain4j.agent.tool.Tool;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component
public class ReservationTool {

    @Autowired
    private ReservationService reservationService;

    @Tool("预约志愿填报服务")
    public void addReservation(
            @P("考生姓名") String name,
            @P("考生性别") String gender,
            @P("考生手机号") String phone,
            @P("预约沟通时间,格式为: yyyy-MM-dd'T'HH:mm") String communicationTime,
            @P("考生所在省份") String province,
            @P("考生预估分数") Integer estimatedScore
    ) {
        Reservation reservation = new Reservation(
                null,
                name,
                gender,
                phone,
                LocalDateTime.parse(communicationTime),
                province,
                estimatedScore);
        reservationService.insert(reservation);
    }

    @Tool("根据考生手机号查询预约单")
    public Reservation findReservation(@P("考生手机号") String phone) {
        return reservationService.findByPhone(phone);
    }
}
```

#### 7.5.4 最终装配

```java
@AiService(
        wiringMode = AiServiceWiringMode.EXPLICIT,
        chatModel = "openAiChatModel",
        streamingChatModel = "openAiStreamingChatModel",
        chatMemoryProvider = "chatMemoryProvider",
        contentRetriever = "contentRetriever",
        tools = "reservationTool"
)
public interface ConsultantService {
    @SystemMessage(fromResource = "system.txt")
    Flux<String> chat(@MemoryId String memoryId, @UserMessage String message);
}
```

Controller：

```java
@RestController
public class ChatController {
    @Autowired
    private ConsultantService consultantService;

    @RequestMapping(value = "/chat", produces = "text/html;charset=utf-8")
    public Flux<String> chat(String memoryId, String message) {
        return consultantService.chat(memoryId, message);
    }
}
```

#### 7.5.5 Function Calling 执行细节

1. LangChain4j 通过反射读取 `@Tool` 的方法名、作用描述，以及 `@P` 的参数名、类型、描述，生成 JSON Schema，放进请求体的 `tools` 字段。
2. 模型判断需要调用工具时，返回工具名和参数（`tool_calls`），而不是直接返回自然语言答案。
3. LangChain4j 在本地调用对应方法，把返回值序列化后作为工具结果追加到消息列表。
4. 再次请求模型；如果模型还要调用其他工具，继续循环，直到模型给出最终答案。
5. 整个过程对业务代码透明：`ConsultantService.chat()` 仍然只返回 `Flux<String>`。

打开 `log-requests` / `log-responses` 可以看到 `tools` 数组和 `tool_calls`，这是排查“模型为什么不调用工具”的第一手材料。

#### 7.5.6 工程要点

| 要点 | 说明 |
| --- | --- |
| 描述面向意图 | `@Tool` 写“什么时候用”，例如“预约志愿填报服务”，不要写内部实现细节 |
| 参数描述完整 | 时间、枚举、单位、格式都要写进 `@P`；模型靠描述生成参数 |
| 参数校验 | 手机号、分数、时间格式在工具方法内再校验一次，不能只依赖模型 |
| 幂等 | 写库前可按手机号查重，避免模型重复调用造成重复预约 |
| 返回值可序列化 | 返回 DTO、`Map` 或简单实体；避免懒加载代理和循环引用 |
| 错误处理 | 工具抛异常时，把可读错误信息返回给模型，让它向用户解释或重试 |
| 安全边界 | 不要暴露删库、转账、发邮件等高风险工具；高风险操作要二次确认 |
| 多工具 | `tools` 可以配置多个 Bean，模型根据描述自行选择 |
| 可选参数 | 较新版本可用 `@P(required = false)` 标记可选参数，具体以所用版本 API 为准 |
| 时间类型 | 示例用 `String` 接收再 `LocalDateTime.parse`，避免模型生成的格式与 Jackson 反序列化冲突 |

#### 7.5.7 测试建议

- 先直接调用 `ReservationService`，确认数据库和 MyBatis 配置正确。
- 再通过聊天接口说“我想预约”，观察日志中是否出现 `tool_calls`。
- 验证模型是否收集齐六项信息；缺项时应继续追问，而不是调用工具。
- 重复提交同一手机号，验证幂等逻辑。
- 查询预约时，确认 `findReservation` 的返回结果能被模型正确转述。

## 8. 面试题与答案要点

### 8.1 LangChain4J 和直接调用 HTTP 有什么区别？

- 直接 HTTP 需要自己拼 JSON、解析响应、处理流式数据和历史消息。
- LangChain4J 提供 `OpenAiChatModel`、`AiServices`、消息注解、会话记忆、RAG、Tools 等封装。
- 简单调用可以用 HTTP/SDK；复杂应用（记忆、RAG、工具）用 LangChain4J 更省事。

### 8.2 AiServices 的作用是什么？

- 把 Java 接口声明成 AI 服务，底层用动态代理调用模型。
- 通过注解配置系统提示词、用户消息、记忆、RAG 检索器、工具。
- 让业务代码面向接口，减少手动拼 Prompt 和解析响应。

### 8.3 会话记忆如何隔离和持久化？

- 隔离：`ChatMemoryProvider` 按 `memoryId` 创建不同的 `ChatMemory`，接口方法用 `@MemoryId` 接收会话 ID。
- 持久化：实现 `ChatMemoryStore` 的 `getMessages`、`updateMessages`、`deleteMessages`，可存 Redis、MySQL 或文件。
- 临时方案：`MessageWindowChatMemory` 只保留最近 N 条消息。

### 8.4 RAG 的完整链路是什么？

- 入库：Document Loader → Document Parser → Document → Document Splitter → TextSegment → EmbeddingModel → Embedding → EmbeddingStore。
- 检索：Query → EmbeddingModel → Query Embedding → EmbeddingStore 相似度检索 → Relevant Segments。
- 生成：Query + Relevant Segments → Prompt → LLM → 回答。

### 8.5 Function Calling 的流程是什么？

- 应用把函数名称、作用、入参写进 Prompt。
- 模型判断需要调用函数时，返回函数名和参数。
- 应用执行本地函数，把结果拼回 Prompt。
- 循环直到模型给出最终答案。

### 8.6 如何选择向量数据库？

- 快速原型：Chroma、InMemoryEmbeddingStore。
- 已有 Redis：RedisSearch。
- 大规模：Milvus、Qdrant。
- 已有 PostgreSQL：pgvector。
- 选择时综合考虑数据规模、部署方式、混合搜索、运维成本。

## 9. 易错点

- `@AiService` 的 `wiringMode = EXPLICIT` 时，`chatModel`、`streamingChatModel`、`chatMemory`、`contentRetriever`、`tools` 的 bean 名称必须与配置一致。
- 流式接口返回 `Flux<String>`，需要 WebFlux 和 `langchain4j-reactor`；普通 MVC 不能直接返回 `Flux`。
- `@SystemMessage(fromResource = "system.txt")` 的文件要放在资源目录。
- `@UserMessage` 中 `{{it}}` 表示唯一参数；多参数要用 `@V` 命名。
- `MessageWindowChatMemory.maxMessages(20)` 只保留最近 20 条，长对话会丢失早期上下文。
- `ChatMemoryProvider` 的 `memoryId` 必须由接口方法的 `@MemoryId` 参数传入，否则无法隔离。
- Redis 作为向量库时，要用 `redislabs/redisearch` 镜像，不是普通 Redis 镜像。
- PDF 解析要显式引入 `langchain4j-document-parser-apache-pdfbox` 并指定 `ApachePdfBoxDocumentParser`。
- `EmbeddingStoreContentRetriever` 的 `maxResults` 和 `minScore` 会直接影响召回数量和质量，需要按业务调参。
- PPT 第 131 页为空，第 132 页为结束页；课程未展示完整项目整合代码，实际项目需结合课程源码。

---

> 📎 **相关笔记**：[[05-LangChain4j核心]] · [[02-大模型RAG开发]] · [[AI/AI 索引|AI 索引]]