---
aliases:
  - LangChain4j
  - LangChain4j 核心
  - AiServices
---

# LangChain4j 核心

> 来源：课程第三章讲义《LangChain4j》（79KB，43 处图片）。本笔记按“快速入门 → Spring 整合 → AiServices → 流式调用 → 消息注解 → 会话记忆 → RAG 知识库 → Tools → 核心 API”的主线重组，代码按可运行结构重排，重复截图和营销性内容已压缩。
>
> 说明：文中带 `补充（非原 PPT）` 标记的段落为整理者补充；面试题、易错点和速查表是对讲义内容的归纳，不是讲义原文。
>
> 前置：[[01-提示词工程]]（模型调用与提示词基础）、[[04-LangChain4J与通义千问]]（同一课程的 PPT 主线，偏项目视角）；RAG 原理：[[02-大模型RAG开发]]；对比：[[03-RAG项目]]（Python + LangChain 实现）。

## 1. 为什么需要 LangChain4j

直接用 HTTP 或 SDK 调模型，需要自己拼 JSON、解析响应、处理流式数据、维护历史消息；一旦要做会话记忆、RAG、Tools，调用前的准备工作会迅速膨胀。

Java 生态里主流的两个封装库是 **LangChain4j** 和 **Spring AI**：

| 方案 | 特点 | 课程选择 |
| --- | --- | --- |
| LangChain4j | 组件齐全，AiServices、会话记忆、RAG、Tools 封装完整，和 Spring Boot 有 starter | 本课程主线 |
| Spring AI | Spring 官方生态，抽象风格更贴近 Spring | 另有课程，不在本篇范围 |

LangChain4j 官方文档：<https://docs.langchain4j.dev/>。

它主要替我们做四件事：

- 把 HTTP 调用封装成 `ChatModel`、`StreamingChatModel` 等对象。
- 用 `AiServices` 把 Java 接口声明成 AI 服务，自动组装提示词和解析返回值。
- 提供 `ChatMemory`、`ContentRetriever`、`Tool` 等能力，分别解决记忆、知识库和函数调用。
- 通过 Spring Boot starter 把模型、向量库、检索器等对象自动注入 IOC 容器。

## 2. 快速入门

### 2.1 引入依赖

```xml
<dependency>
  <groupId>dev.langchain4j</groupId>
  <artifactId>langchain4j-open-ai</artifactId>
  <version>1.0.1</version>
</dependency>
```

### 2.2 构建聊天对象

`OpenAiChatModel` 需要三个关键信息：模型地址、API-KEY、模型名称。百炼平台兼容 OpenAI 协议，所以地址使用：

```text
https://dashscope.aliyuncs.com/compatible-mode/v1
```

API-KEY 不建议硬编码在代码里，推荐放到操作系统环境变量。Windows 下新建用户变量 `API-KEY`，值为百炼平台申请的 key，配置完成后重启 IDEA，否则 IDE 读不到新变量。

![配置 API-KEY 环境变量](file:///D:/Java/data/AI/05-LangChain4j核心/29-api-key-env.png)

图 5-1 在 Windows 用户变量中配置 `API-KEY`，代码通过 `System.getenv("API-KEY")` 读取。

```java
OpenAiChatModel model = OpenAiChatModel.builder()
        .baseUrl("https://dashscope.aliyuncs.com/compatible-mode/v1")
        .apiKey(System.getenv("API-KEY"))
        .modelName("qwen-plus")
        .build();
```

### 2.3 调用模型

```java
public class App {
    public static void main(String[] args) {
        OpenAiChatModel model = OpenAiChatModel.builder()
                .baseUrl("https://dashscope.aliyuncs.com/compatible-mode/v1")
                .apiKey(System.getenv("API-KEY"))
                .modelName("qwen-plus")
                .build();

        String result = model.chat("东哥帅不帅?");
        System.out.println(result);
    }
}
```

### 2.4 打开请求/响应日志

排查问题时，最有用的是看到 LangChain4j 实际发给模型的请求体和模型返回的原始响应。构建模型时打开两个开关：

```java
OpenAiChatModel model = OpenAiChatModel.builder()
        .baseUrl("https://dashscope.aliyuncs.com/compatible-mode/v1")
        .apiKey(System.getenv("API-KEY"))
        .modelName("qwen-plus")
        .logRequests(true)
        .logResponses(true)
        .build();
```

![请求与响应日志](file:///D:/Java/data/AI/05-LangChain4j核心/28-request-response-log.png)

图 5-2 `logRequests` / `logResponses` 打印出的 HTTP 请求与响应，可看到 `model`、`messages`、`stream` 等字段。

> 补充（非原 PPT）：日志由 SLF4J 输出。Spring Boot 项目自带日志实现；普通 Maven 项目如果看不到日志，需要补充 `logback-classic` 等日志实现。

## 3. Spring Boot 整合

### 3.1 引入 starter

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai-spring-boot-starter</artifactId>
    <version>1.0.1-beta6</version>
</dependency>
```

### 3.2 配置模型

```yaml
langchain4j:
  open-ai:
    chat-model:
      base-url: https://dashscope.aliyuncs.com/compatible-mode/v1
      api-key: ${API-KEY}
      model-name: qwen-plus
```

starter 读取到配置后，会自动向 IOC 容器注入一个 `OpenAiChatModel` 对象，Bean 名称默认为 `openAiChatModel`。

### 3.3 编写接口

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

### 3.4 在 yml 中打开日志

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

| 配置 | 作用 |
| --- | --- |
| `base-url` | 模型服务地址，百炼使用 OpenAI 兼容模式 |
| `api-key` | 认证密钥，建议用环境变量占位符 |
| `model-name` | 模型名称，例如 `qwen-plus` |
| `log-requests` | 打印请求日志 |
| `log-responses` | 打印响应日志 |
| `logging.level.dev.langchain4j` | 控制 LangChain4j 日志级别 |

## 4. AiServices

### 4.1 它解决什么问题

直接调用 `OpenAiChatModel.chat()` 只适合最简单的一问一答。要做会话记忆、RAG、Tools，每次调用前都要自己准备历史消息、检索片段和工具描述，调用后还要解析响应。`AiServices` 把这些工作封装到一个动态代理里：开发者只声明接口，框架负责组装提示词、调用模型、处理记忆/检索/工具。

![AiServices 整合记忆、RAG 与 Tools](file:///D:/Java/data/AI/05-LangChain4j核心/01-aiservices-architecture.png)

图 5-3 `AiServices` 把会话记忆、RAG 知识库、Tools 工具与 `OpenAiChatModel` 组织在一起，再统一调用大模型。

### 4.2 编程式使用

引入依赖：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-spring-boot-starter</artifactId>
    <version>1.0.1-beta6</version>
</dependency>
```

声明接口：

```java
public interface ConsultantService {
    // message 为用户输入的内容
    String chat(String message);
}
```

用 `AiServices.builder()` 创建代理对象并注册为 Bean：

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

Controller 注入接口使用：

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

### 4.3 声明式使用

在接口上添加 `@AiService`，LangChain4j 扫描后自动创建代理对象并注入 IOC 容器：

```java
@AiService(
        wiringMode = AiServiceWiringMode.EXPLICIT,
        chatModel = "openAiChatModel"
)
public interface ConsultantService {
    String chat(String message);
}
```

| 属性 | 说明 |
| --- | --- |
| `wiringMode` | `AUTOMATIC` 自动装配（默认）；`EXPLICIT` 手动指定 Bean 名称 |
| `chatModel` | 阻塞式聊天模型 Bean 名称，默认 `openAiChatModel` |
| `streamingChatModel` | 流式聊天模型 Bean 名称 |
| `chatMemory` | 全局共享的会话记忆 Bean 名称 |
| `chatMemoryProvider` | 按 `memoryId` 创建记忆对象的提供者 |
| `contentRetriever` | RAG 检索器 Bean 名称 |
| `tools` | 工具类 Bean 名称，可配置多个 |

> 自动装配更省事，手动装配更容易看清“到底用了哪个 Bean”。课程统一使用 `EXPLICIT`，便于排查配置错误。

## 5. 流式调用

阻塞式调用一次性返回完整结果；流式调用把模型输出拆成多个片段，前端可以边生成边显示。

### 5.1 引入依赖

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

### 5.2 配置流式模型

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

### 5.3 接口返回 Flux

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

### 5.4 Controller 返回流

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

`produces = "text/html;charset=utf-8"` 用于避免浏览器把中文流式内容显示成乱码。

> 补充（非原 PPT）：流式接口返回 `Flux<String>`，项目需要 Reactor 相关依赖。若项目同时引入 Web 与 WebFlux，要确认实际启动的 Web 容器和异步配置，避免流式响应被缓冲。

### 5.5 对接前端

课程提供现成的 `index.html`，复制到 `src/main/resources/static/` 后可直接访问。前端通过 `fetch` 读取流式响应，逐块追加到聊天窗口；前端实现不是本篇重点，理解“后端返回 `Flux`，前端逐块消费”即可。

## 6. 消息注解

志愿填报顾问只应回答志愿相关问题。用户问“特朗普靠谱吗”时，它应当拒绝并引导回业务范围。这类“角色和边界”通过系统消息设定。

![SystemMessage 限定回答范围](file:///D:/Java/data/AI/05-LangChain4j核心/24-system-message-scope.png)

图 5-4 通过系统消息限定服务范围后，模型拒绝回答政治话题并引导回志愿填报。

### 6.1 SystemMessage

直接在方法上写系统消息：

```java
@SystemMessage("你是东哥的助手小月月，人美心善又多金！")
Flux<String> chat(String message);
```

系统消息较长时，放到资源文件中：

```java
@SystemMessage(fromResource = "system.txt")
Flux<String> chat(String message);
```

`system.txt` 放在 `src/main/resources/` 下。这样提示词可以独立维护，不必反复改 Java 代码。

### 6.2 UserMessage

`@UserMessage` 用于在用户消息前后拼接预设内容：

```java
@UserMessage("你是东哥的助手小月月，温柔貌美又多金。{{it}}")
Flux<String> chat(String message);
```

`{{it}}` 是固定占位符，代表方法唯一的参数。若想给参数换名字，用 `@V`：

```java
@UserMessage("你是东哥的助手小月月，温柔貌美又多金。{{msg}}")
Flux<String> chat(@V("msg") String message);
```

| 注解 | 作用 | 关键点 |
| --- | --- | --- |
| `@SystemMessage` | 设定系统角色、边界、规则 | 可内联，也可 `fromResource` |
| `@UserMessage` | 包装用户消息 | 用 `{{it}}` 引用唯一参数 |
| `@V` | 给参数命名 | 配合 `{{msg}}` 使用 |
| `@MemoryId` | 标记会话记忆 ID | 多参数时必须显式标注用户消息 |

> 方法只有一个参数时，LangChain4j 默认把它当用户消息；方法有多个参数时，必须用 `@UserMessage` 明确哪个参数是用户输入，否则框架无法判断。

### 6.3 选择建议

- **角色、规则、边界**放 `@SystemMessage`，例如“你只回答志愿填报问题”。
- **单次输入的前后缀**放 `@UserMessage`，例如“请用一句话回答：{{it}}”。
- 两者同时使用时，不要让系统消息和用户消息给出冲突指令。
- 课程项目最终保留 `@SystemMessage(fromResource = "system.txt")`，注释掉测试用的 `@UserMessage`。

## 7. 会话记忆

### 7.1 原理

大模型本身无状态，每次请求都是独立的。要让模型“记住”上下文，只能把历史消息和新问题一起发送。LangChain4j 的做法是引入一个存储对象：

1. 用户消息到达后端，先写入存储对象。
2. 从存储对象读出全部历史消息。
3. 历史消息 + 新问题一起发送给大模型。
4. 模型回复后，把回复也写入存储对象。

![会话记忆原理](file:///D:/Java/data/AI/05-LangChain4j核心/02-chat-memory-flow.gif)

图 5-5 会话记忆：每轮都把存储对象中的全部消息一起发给模型，再把模型回复追加回存储对象。

第二轮提问“是985吗”时，存储对象里已经有“用户问 211”“模型答是”“用户问 985”三条消息，模型据此判断“它”指西北大学。这就是“记忆”的本质：不是模型记住了，而是应用每轮都重发上下文。

### 7.2 ChatMemory 接口

```java
public interface ChatMemory {
    Object id();                       // 记忆存储对象的唯一标识
    void add(ChatMessage message);     // 添加一条会话记忆
    List<ChatMessage> messages();      // 获取所有会话记忆
    void clear();                      // 清除所有会话记忆
}
```

LangChain4j 提供两个常用实现：

| 实现 | 淘汰策略 | 适用场景 |
| --- | --- | --- |
| `MessageWindowChatMemory` | 按消息条数保留最近 N 条 | 课程使用，简单直观 |
| `TokenWindowChatMemory` | 按 token 数保留窗口 | 对上下文成本敏感时更精确 |

为什么需要上限：

- 模型上下文窗口有限，消息太多会超出限制。
- 发送的 token 越多，费用越高。
- 课程设置 `maxMessages(20)`，超过后淘汰最早的消息。

> 注意：`maxMessages` 统计的是消息条数，用户消息和 AI 回复各算一条。20 条约等于 10 轮对话。

### 7.3 基本实现

在配置类中创建 `MessageWindowChatMemory`：

```java
@Bean
public ChatMemory chatMemory() {
    return MessageWindowChatMemory.builder()
            .maxMessages(20)
            .build();
}
```

挂到 `@AiService`：

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

这样所有请求共用同一个 `ChatMemory`，适合单用户演示，但不适合多用户。

### 7.4 会话记忆隔离

多用户场景下，如果共用一个 `ChatMemory`，A 用户会看到 B 用户的对话。LangChain4j 用 `ChatMemoryProvider` + `memoryId` 解决：

1. 请求携带 `memoryId`。
2. 框架在容器中查找该 ID 对应的 `ChatMemory`。
3. 找到就复用；找不到就调用 `ChatMemoryProvider.get(memoryId)` 创建。
4. 不同 `memoryId` 使用不同记忆对象，实现隔离。

![会话记忆隔离原理](file:///D:/Java/data/AI/05-LangChain4j核心/03-chat-memory-isolation.gif)

图 5-6 不同 `memoryId` 对应不同 `ChatMemory`；相同 `memoryId` 复用同一个记忆对象。

定义提供者：

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

接口方法增加 `@MemoryId`：

```java
@AiService(
        wiringMode = AiServiceWiringMode.EXPLICIT,
        chatModel = "openAiChatModel",
        streamingChatModel = "openAiStreamingChatModel",
        chatMemoryProvider = "chatMemoryProvider"
)
public interface ConsultantService {
    @SystemMessage(fromResource = "system.txt")
    Flux<String> chat(@MemoryId String memoryId, @UserMessage String message);
}
```

Controller 接收前端传来的 `memoryId`：

```java
@RequestMapping(value = "/chat", produces = "text/html;charset=utf-8")
public Flux<String> chat(String memoryId, String message) {
    return consultantService.chat(memoryId, message);
}
```

> 使用 `chatMemoryProvider` 后，原来的全局 `chatMemory` 应注释掉，避免两个配置同时生效造成语义混乱。

### 7.5 持久化到 Redis

#### 为什么会丢

`MessageWindowChatMemory` 自己不存消息，它把读写委托给 `ChatMemoryStore`：

```java
public class MessageWindowChatMemory implements ChatMemory {
    private final Object id;
    private final ChatMemoryStore store;

    public void add(ChatMessage message) {
        List<ChatMessage> messages = new ArrayList<>(messages());
        messages.add(message);
        this.store.updateMessages(this.id, messages);
    }

    public List<ChatMessage> messages() {
        return this.store.getMessages(this.id);
    }

    public void clear() {
        this.store.deleteMessages(this.id);
    }
}
```

`ChatMemoryStore` 接口：

```java
public interface ChatMemoryStore {
    List<ChatMessage> getMessages(Object memoryId);
    void updateMessages(Object memoryId, List<ChatMessage> messages);
    void deleteMessages(Object memoryId);
}
```

默认实现 `SingleSlotChatMemoryStore` 用一个 `ArrayList` 存消息，属于纯内存存储，服务重启即丢失。

![ChatMemoryStore 的实现类](file:///D:/Java/data/AI/05-LangChain4j核心/04-chat-memory-store-classes.png)

图 5-7 `ChatMemoryStore` 的常用实现：`InMemoryChatMemoryStore` 与 `SingleSlotChatMemoryStore` 都是内存存储。

#### 用 Redis 持久化

准备 Redis：

```bash
docker run --name redis -d -p 6379:6379 redis
```

引入依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

配置连接：

```yaml
spring:
  data:
    redis:
      host: localhost
      port: 6379
```

实现 `ChatMemoryStore`：

```java
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.data.message.ChatMessageDeserializer;
import dev.langchain4j.data.message.ChatMessageSerializer;
import dev.langchain4j.store.memory.chat.ChatMemoryStore;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Repository;

import java.time.Duration;
import java.util.List;

@Repository
public class RedisChatMemoryStore implements ChatMemoryStore {

    @Autowired
    private StringRedisTemplate redisTemplate;

    @Override
    public List<ChatMessage> getMessages(Object memoryId) {
        String json = redisTemplate.opsForValue().get(memoryId.toString());
        return ChatMessageDeserializer.messagesFromJson(json);
    }

    @Override
    public void updateMessages(Object memoryId, List<ChatMessage> messages) {
        String json = ChatMessageSerializer.messagesToJson(messages);
        redisTemplate.opsForValue().set(
                memoryId.toString(), json, Duration.ofDays(1));
    }

    @Override
    public void deleteMessages(Object memoryId) {
        redisTemplate.delete(memoryId.toString());
    }
}
```

把 Store 交给 `MessageWindowChatMemory`：

```java
@Autowired
private ChatMemoryStore redisChatMemoryStore;

@Bean
public ChatMemoryProvider chatMemoryProvider() {
    return new ChatMemoryProvider() {
        @Override
        public ChatMemory get(Object memoryId) {
            return MessageWindowChatMemory.builder()
                    .id(memoryId)
                    .maxMessages(20)
                    .chatMemoryStore(redisChatMemoryStore)
                    .build();
        }
    };
}
```

| 方案 | 存储位置 | 重启后是否保留 | 适用场景 |
| --- | --- | --- | --- |
| `SingleSlotChatMemoryStore` | JVM 内存 | 否 | 本地演示 |
| `InMemoryChatMemoryStore` | JVM 内存 | 否 | 单机临时使用 |
| 自定义 `RedisChatMemoryStore` | Redis | 是 | 多实例、生产环境 |
| 自定义数据库 Store | MySQL/Mongo 等 | 是 | 需要审计或长期归档 |

> 补充（非原 PPT）：`memoryId` 会被直接拼成 Redis key。生产环境不要直接信任前端传入的任意字符串，应先做身份校验，并在 key 前加业务前缀，例如 `chat:memory:{memoryId}`，避免不同业务互相覆盖。

### 7.6 常见坑

- `maxMessages` 限制的是消息条数，不是对话轮数。
- `memoryId` 必须在接口方法上用 `@MemoryId` 标注，否则不会参与隔离。
- 多参数方法必须用 `@UserMessage` 标注哪个参数是用户输入。
- 使用 `chatMemoryProvider` 时不要再配 `chatMemory`。
- 切换持久化 Store 后，旧的内存消息不会自动迁移。
- 系统消息通常不写入 `ChatMemory`，它由 `@SystemMessage` 每轮重新注入。

## 8. RAG 知识库

### 8.1 为什么需要 RAG

课程使用的 `qwen-plus` 训练数据截止到 2023 年 10 月，无法知道 2024 年的录取分数。类似地，企业内部制度、专业领域资料也不在通用训练数据里。

![模型知识截止导致的回答局限](file:///D:/Java/data/AI/05-LangChain4j核心/05-model-knowledge-cutoff.png)

图 5-8 模型只能基于训练期知识回答，无法给出 2024 年录取分数。

RAG（Retrieval Augmented Generation，检索增强生成）的做法是：在调用大模型前，先从外部知识库检索与问题相关的片段，再把“用户问题 + 检索片段”一起交给模型生成答案。

没有知识库时：

![普通问答时序](file:///D:/Java/data/AI/05-LangChain4j核心/06-rag-normal-sequence.png)

图 5-9 普通问答：用户 → AI 应用 → 基础大模型 → 返回响应。

外挂知识库后：

![RAG 问答时序](file:///D:/Java/data/AI/05-LangChain4j核心/07-rag-with-kb-sequence.png)

图 5-10 RAG 问答：AI 应用先检索知识库，再把问题与知识片段一起组织成 Prompt。

RAG 要解决的核心问题只有两个：

1. **知识库怎么建**：文档加载、解析、分割、向量化、入库。
2. **怎么检索**：把问题向量化，在向量库中找相似片段。

### 8.2 向量与余弦相似度

#### 向量是什么

向量是表示大小和方向的量。几何上用带箭头的线段表示；代数上用一组坐标表示：

![向量的几何表示与代数表示](file:///D:/Java/data/AI/05-LangChain4j核心/09-vector-definition.png)

图 5-11 向量既可以用有向线段表示，也可以用坐标表示，例如 `V = (1, 2)`。

维度可以扩展：

- 二维向量：`V = (v1, v2)`
- 三维向量：`V = (v1, v2, v3)`
- N 维向量：`V = (v1, v2, …, vn)`

RAG 中的文本向量通常是几百到几千维。文本经嵌入模型转换后，语义相近的文本在向量空间中方向更接近。

#### 余弦相似度

余弦相似度衡量两个向量方向的接近程度：

```text
cos(θ) = (A · B) / (||A|| × ||B||)
```

- 分子是内积：对应坐标乘积之和。
- 分母是两个向量模长的乘积。
- 结果越大，方向越接近，文本语义通常越相似。

课程例子：`V = (1, 2)`，`U = (2, 1)`：

```text
cos(θ) = (1×2 + 2×1) / (√(1²+2²) × √(2²+1²))
       = 4 / (√5 × √5)
       = 4 / 5
       = 0.8
```

![余弦相似度计算](file:///D:/Java/data/AI/05-LangChain4j核心/10-cosine-similarity.png)

图 5-12 `V = (1,2)` 与 `U = (2,1)` 的余弦相似度为 0.8。

两个极端情况：

- 两个向量重合：`cos(θ) = 1`，方向完全一致。
- 两个向量正交：`cos(θ) = 0`，方向垂直。

![正交向量的余弦相似度](file:///D:/Java/data/AI/05-LangChain4j核心/11-orthogonal-vectors.png)

图 5-13 `A = (0,2)` 与 `B = (2,0)` 正交，余弦相似度为 0。

![余弦相似度与距离的关系](file:///D:/Java/data/AI/05-LangChain4j核心/12-cosine-conclusion.png)

图 5-14 在第一象限的例子里，余弦相似度越大，向量方向越接近，对应点之间的距离越小。

> 补充（非原 PPT）：余弦相似度的完整取值范围是 `[-1, 1]`。课程例子都在第一象限，所以只观察到 `0~1`；实际文本向量可能出现负值，但“越大越相似”的结论不变。

### 8.3 存储流程

LangChain4j 的入库链路：

![RAG 入库流程](file:///D:/Java/data/AI/05-LangChain4j核心/13-rag-ingestion-flow.png)

图 5-15 `Document → Text Splitter → Segments → Embedding Model → Embeddings → Embedding Store`。

具体步骤：

1. 把最新资料或专业资料整理成文档。
2. 用文档加载器把文档读入内存，生成 `Document` 对象。
3. 用文档分割器把长文档切成文本片段（`TextSegment`）。
4. 用向量模型把每个片段转成向量（`Embedding`）。
5. 把向量和对应文本片段一起写入向量数据库（`EmbeddingStore`）。

![RAG 存储过程示例](file:///D:/Java/data/AI/05-LangChain4j核心/14-rag-ingestion-example.gif)

图 5-16 一篇文档被切成多个片段，每个片段向量化后与原文一起入库。

课程例子把文档切成“我爱上班、上班真好、我爱工作、拒绝加班、我要躺平”五个片段，每个片段对应一条“向量 + 文本”的记录。

#### 快速实现

引入 easy-rag：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-easy-rag</artifactId>
    <version>1.0.1-beta6</version>
</dependency>
```

加载文档、构建内存向量库、切分并入库：

```java
@Bean
public EmbeddingStore store() {
    // 1. 加载文档进内存
    List<Document> documents = ClassPathDocumentLoader.loadDocuments("content");

    // 2. 构建内存版向量数据库操作对象
    InMemoryEmbeddingStore<TextSegment> store = new InMemoryEmbeddingStore<>();

    // 3. 切分、向量化并存储
    EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
            .embeddingStore(store)
            .build();
    ingestor.ingest(documents);

    return store;
}
```

`EmbeddingStoreIngestor` 内部封装了默认的分割器、向量模型和入库逻辑。快速入门阶段不指定这些组件也能跑通。

### 8.4 检索流程

![RAG 检索流程](file:///D:/Java/data/AI/05-LangChain4j核心/15-rag-retrieval-flow.png)

图 5-17 `Query → Embedding Model → Query Embedding → Embedding Store → Relevant Segments → Query + Segments → Language Model`。

步骤：

1. 用户问题经同一个向量模型转成查询向量。
2. 在向量库中计算查询向量与已有向量的余弦相似度。
3. 按 `minScore` 过滤，按分数排序取前 `maxResults` 个片段。
4. 把用户问题和片段一起组织成 Prompt，交给大模型生成答案。

![RAG 检索过程示例](file:///D:/Java/data/AI/05-LangChain4j核心/16-rag-retrieval-example.gif)

图 5-18 查询“你爱上班吗”与五个片段分别计算相似度，超过阈值的片段被召回。

课程例子中相似度为 `0.8、0.6、0.7、0.3、0.2`，阈值设为 `0.5`，因此召回前三个片段，再把问题和这三个片段一起发给模型。

#### 构建检索器

```java
@Bean
public ContentRetriever contentRetriever(EmbeddingStore store) {
    return EmbeddingStoreContentRetriever.builder()
            .embeddingStore(store)   // 从哪里检索
            .minScore(0.5)           // 最低相似度
            .maxResults(3)           // 最多返回几个片段
            .build();
}
```

| 参数 | 作用 | 调大后的影响 |
| --- | --- | --- |
| `minScore` | 相似度下限 | 召回更少、更精准，但可能漏掉正确片段 |
| `maxResults` | 返回片段上限 | 召回更多、上下文更全，但 token 成本和噪声增加 |

挂到 `@AiService`：

```java
@AiService(
        wiringMode = AiServiceWiringMode.EXPLICIT,
        chatModel = "openAiChatModel",
        streamingChatModel = "openAiStreamingChatModel",
        chatMemoryProvider = "chatMemoryProvider",
        contentRetriever = "contentRetriever"
)
public interface ConsultantService {
    @SystemMessage(fromResource = "system.txt")
    Flux<String> chat(@MemoryId String memoryId, @UserMessage String message);
}
```

#### 验证检索是否生效

提问“西北大学2024年录取分数？”，模型能够基于知识库回答，说明检索链路生效。

![基于知识库的回答](file:///D:/Java/data/AI/05-LangChain4j核心/25-rag-answer-example.png)

图 5-19 模型基于检索到的 2024 年录取数据回答，而不是声称“知识截止”。

查看请求日志，可以看到 LangChain4j 自动把检索片段拼进了用户消息：

![RAG 请求日志](file:///D:/Java/data/AI/05-LangChain4j核心/26-rag-prompt-log.png)

图 5-20 用户消息格式为“用户问题 + `Answer using the following information:` + 检索片段”。

日志中的格式可概括为：

```text
用户问题

Answer using the following information:
检索出来的知识片段
```

这说明 RAG 并没有改变模型本身，只是改变了发给模型的 Prompt。

### 8.5 核心 API

完整入库链路：

```text
文档
  → Document Loader（加载）
  → Document Parser（解析非纯文本）
  → Document
  → Document Splitter（切分）
  → TextSegment
  → EmbeddingModel（向量化）
  → Embedding
  → EmbeddingStore（入库）
```

其中分割、向量化、入库的调用被 `EmbeddingStoreIngestor` 封装；开发者主要选择“用哪种加载器、解析器、分割器、向量模型、向量库”。

![RAG 核心 API 流程](file:///D:/Java/data/AI/05-LangChain4j核心/17-rag-core-api-flow.gif)

图 5-21 RAG 核心 API 全景：文档加载器、解析器、分割器、向量模型、向量库操作对象，以及把它们串起来的 `EmbeddingStoreIngestor`。

| 组件 | 作用 | 常用实现 |
| --- | --- | --- |
| `DocumentLoader` | 从磁盘/类路径/URL 加载文档 | `FileSystemDocumentLoader`、`ClassPathDocumentLoader`、`UrlDocumentLoader` |
| `DocumentParser` | 把 PDF/Office 等解析成纯文本 | `ApachePdfBoxDocumentParser`、`ApachePoiDocumentParser`、`ApacheTikaDocumentParser` |
| `DocumentSplitter` | 把长文档切成片段 | `DocumentSplitters.recursive(...)` 等 |
| `EmbeddingModel` | 文本转向量 | 内置内存模型、`text-embedding-v3` |
| `EmbeddingStore` | 向量库操作 | `InMemoryEmbeddingStore`、`RedisEmbeddingStore` |
| `EmbeddingStoreIngestor` | 串起切分、向量化、入库 | 构建时传入上述组件 |
| `ContentRetriever` | 在线检索 | `EmbeddingStoreContentRetriever` |

#### 8.5.1 文档加载器

| 加载器 | 加载位置 |
| --- | --- |
| `FileSystemDocumentLoader` | 本地磁盘绝对路径 |
| `ClassPathDocumentLoader` | 类路径（`resources` 下） |
| `UrlDocumentLoader` | URL 地址 |

把类路径加载换成文件系统加载：

```java
List<Document> documents = FileSystemDocumentLoader.loadDocuments(
        "C:/ideaProjects/consultant/src/main/resources/content");
```

> 打包成 jar 后，`resources` 中的文件在 jar 内部，`FileSystemDocumentLoader` 不能按普通磁盘路径访问；需要外部可更新知识库时，把文档放到 jar 外，用文件系统加载。

#### 8.5.2 文档解析器

| 解析器 | 适用格式 |
| --- | --- |
| `TextDocumentParser` | 纯文本 |
| `ApachePdfBoxDocumentParser` | PDF |
| `ApachePoiDocumentParser` | DOC、PPT、XLS |
| `ApacheTikaDocumentParser` | 默认，几乎支持所有格式 |

默认的 Tika 解析器通用性强，但解析 PDF 时可能不够理想。可以显式换成 PDFBox：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-document-parser-apache-pdfbox</artifactId>
    <version>1.0.1-beta6</version>
</dependency>
```

```java
List<Document> documents = ClassPathDocumentLoader.loadDocuments(
        "content", new ApachePdfBoxDocumentParser());
```

#### 8.5.3 文档分割器

| 分割器 | 切分依据 |
| --- | --- |
| `DocumentByParagraphSplitter` | 段落 |
| `DocumentByLineSplitter` | 行 |
| `DocumentBySentenceSplitter` | 句子 |
| `DocumentByWordSplitter` | 词 |
| `DocumentByCharacterSplitter` | 固定字符数 |
| `DocumentByRegexSplitter` | 正则表达式 |
| `DocumentSplitters.recursive(...)` | 默认，递归：段落 → 行 → 句子 → 词 |

![按段落分割与片段组合](file:///D:/Java/data/AI/05-LangChain4j核心/18-document-splitter.gif)

图 5-22 分割器先按段落切分，再按字符容量组合成文本片段；放不下的段落会继续递归切分。

默认递归分割器的单个片段上限是 300 字符。可以自定义：

```java
DocumentSplitter documentSplitter = DocumentSplitters.recursive(
        500,   // 每个片段最大字符数
        100    // 相邻片段重叠字符数
);
```

为什么要重叠：

![片段重叠](file:///D:/Java/data/AI/05-LangChain4j核心/19-chunk-overlap.png)

图 5-23 相邻片段保留重叠内容，避免上一段末尾的“高考”语义在下一段完全丢失。

如果第一个片段结尾讲“高考”，第二个片段开头完全没有“高考”字样，那么检索“高考”时第二个片段可能召不回来。让上一段末尾与下一段开头重复一部分，可以保持语义连贯。

配置分割器：

```java
EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
        .embeddingStore(store)
        .documentSplitter(documentSplitter)
        .build();
```

#### 8.5.4 向量模型

`EmbeddingModel` 负责把文本片段或用户问题转成向量：

```java
public interface EmbeddingModel {
    Response<Embedding> embed(String text);
    Response<Embedding> embed(TextSegment textSegment);
    Response<List<Embedding>> embedAll(List<TextSegment> textSegments);
    int dimension();
}
```

easy-rag 内置了一个内存版向量模型，快速入门时由 `EmbeddingStoreIngestor` 默认使用。它的维度有限，检索精度通常不如云端向量模型。

![EmbeddingModel 的常用实现](file:///D:/Java/data/AI/05-LangChain4j核心/20-embedding-model-classes.png)

图 5-24 `EmbeddingModel` 的常见实现，包括内置 ONNX 模型与 OpenAI 兼容模型。

替换为百炼 `text-embedding-v3`：

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

starter 会自动注入 `EmbeddingModel`，把它同时交给入库器和检索器：

```java
@Autowired
private EmbeddingModel embeddingModel;

@Bean
public EmbeddingStore store() {
    List<Document> documents = ClassPathDocumentLoader.loadDocuments(
            "content", new ApachePdfBoxDocumentParser());

    InMemoryEmbeddingStore<TextSegment> store = new InMemoryEmbeddingStore<>();
    DocumentSplitter ds = DocumentSplitters.recursive(500, 100);

    EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
            .embeddingStore(store)
            .documentSplitter(ds)
            .embeddingModel(embeddingModel)
            .build();
    ingestor.ingest(documents);

    return store;
}

@Bean
public ContentRetriever contentRetriever(EmbeddingStore store) {
    return EmbeddingStoreContentRetriever.builder()
            .embeddingStore(store)
            .minScore(0.5)
            .maxResults(3)
            .embeddingModel(embeddingModel)
            .build();
}
```

> 入库和检索必须使用同一个嵌入模型。换模型后，旧向量要重新生成，否则向量空间不一致，检索结果不可靠。

#### 8.5.5 向量数据库操作对象

`EmbeddingStore` 是向量库的统一操作接口，核心能力是两类：

| 方法 | 作用 |
| --- | --- |
| `add(...)` / `addAll(...)` | 添加单个或批量向量及对应文本片段 |
| `search(EmbeddingSearchRequest)` | 按查询向量做相似度检索 |

`InMemoryEmbeddingStore` 操作内存向量库，重启即丢失，而且每次启动都要重新向量化，既耗时又会产生 embedding 调用费用。

![EmbeddingStore 的接口与内存实现](file:///D:/Java/data/AI/05-LangChain4j核心/21-embedding-store-classes.png)

图 5-25 `EmbeddingStore` 接口与 `InMemoryEmbeddingStore` 实现。

外部向量库可选 Milvus、Chroma、Pinecone、RedisSearch、pgvector 等：

![常见向量数据库](file:///D:/Java/data/AI/05-LangChain4j核心/08-vector-database-options.png)

图 5-26 知识库通常落在向量数据库：Milvus、Chroma、Pinecone，或 RedisSearch、pgvector 等扩展方案。

课程使用 RedisSearch：

```bash
docker stop redis          # 停止普通 Redis
docker rm redis            # 删除普通 Redis
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

> 这里的 `langchain4j.community.redis` 与第 7 章会话记忆的 `spring.data.redis` 是两套配置，互不相干。

starter 自动注入 `RedisEmbeddingStore`，把它交给入库器和检索器：

```java
@Autowired
private RedisEmbeddingStore redisEmbeddingStore;

@Bean
public EmbeddingStore store() {
    List<Document> documents = ClassPathDocumentLoader.loadDocuments(
            "content", new ApachePdfBoxDocumentParser());

    DocumentSplitter ds = DocumentSplitters.recursive(500, 100);

    EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
            .embeddingStore(redisEmbeddingStore)
            .documentSplitter(ds)
            .embeddingModel(embeddingModel)
            .build();
    ingestor.ingest(documents);

    return redisEmbeddingStore;
}

@Bean
public ContentRetriever contentRetriever() {
    return EmbeddingStoreContentRetriever.builder()
            .embeddingStore(redisEmbeddingStore)
            .minScore(0.5)
            .maxResults(3)
            .embeddingModel(embeddingModel)
            .build();
}
```

#### 8.5.6 参数调优

> 补充（非原 PPT）：以下是把课程参数放回工程场景后的调参要点，不改变原文结论。

| 参数 | 常用起点 | 调大 | 调小 |
| --- | --- | --- | --- |
| 片段大小 | 300–800 字符 | 上下文更完整，但检索粒度变粗 | 定位更精准，但语义可能被切碎 |
| 片段重叠 | 50–150 字符 | 语义连贯性更好，但存储和 token 增加 | 存储更省，但跨片段语义容易丢失 |
| `minScore` | 0.5 左右 | 召回更精准，可能漏召回 | 召回更多，噪声增加 |
| `maxResults` | 3–5 | 上下文更全，token 成本上升 | 成本更低，可能缺少关键依据 |
| 向量维度 | 按模型默认 | 表达更细，计算存储更重 | 更轻量，精度可能下降 |

### 8.6 收尾工作

把所有 PDF 放进 `resources/content/`，启动一次，让向量库写入全部数据。确认无误后，把 `store()` 方法上的 `@Bean` 注释掉：

```java
// @Bean
public EmbeddingStore store() {
    // 加载、切分、向量化、入库
    return redisEmbeddingStore;
}
```

原因：`@Bean` 方法每次启动都会执行。如果保留，程序每次启动都会重新加载文档、重新调用 embedding 模型，既慢又花钱。Redis 中已经存好向量后，只需让检索器继续使用 `RedisEmbeddingStore` 即可。

| 问题 | 做法 |
| --- | --- |
| 每次启动重复向量化 | 首次入库后注释 `store()` 的 `@Bean` |
| 新增知识 | 临时恢复 `@Bean`，入库完成后再次注释 |
| 换嵌入模型 | 清空旧集合，按新模型重新入库 |
| 向量库连不上 | 确认 RedisSearch 镜像和端口，而不是普通 Redis |

### 8.7 常见坑

- `InMemoryEmbeddingStore` 重启即丢，生产环境要换外部向量库。
- 入库和检索必须使用同一个 embedding 模型。
- `minScore` 设得过高会检索不到任何片段，模型只能凭空回答。
- `maxResults` 过大不仅费 token，还会把低相关片段塞进上下文，干扰生成。
- `ClassPathDocumentLoader` 读取的是类路径；需要外部更新知识文件时改用 `FileSystemDocumentLoader`。
- PDF 解析效果差时，显式引入 PDFBox 解析器。
- RedisSearch 需要 `redislabs/redisearch` 镜像，普通 `redis` 镜像没有向量检索能力。
- `@Bean` 的入库方法不要一直保留，否则每次启动都重复向量化。

## 9. Tools 工具调用

### 9.1 场景与原理

志愿填报顾问回答完后，会引导用户预约一对一指导。用户提供姓名、性别、电话、沟通时间、省份、预估分数后，程序需要往 MySQL 的预约表写一条记录。

这类“让模型决定调用哪个本地函数”的能力叫 Tools，早期也叫 Function Calling。

![Function Calling 时序](file:///D:/Java/data/AI/05-LangChain4j核心/22-function-calling-sequence.png)

图 5-27 AI 应用把函数名称、作用、入参写进 Prompt；模型返回要调用的函数和参数；应用执行后把结果拼回 Prompt，循环直到任务完成。

流程：

1. 应用把所有可调用函数的“名称、作用、入参”描述给模型。
2. 模型结合用户问题判断是否需要调用函数。
3. 需要调用时，模型返回函数名和参数。
4. 应用执行本地函数，把执行结果追加到上下文。
5. 再次请求模型；如果还需要调用其他函数，继续循环。
6. 模型不再调用函数时，返回最终自然语言答案。

一次任务可能调用多个函数，所以这是一个循环，而不是单次调用。

### 9.2 最小实现

LangChain4j 用 `@Tool` 描述方法作用，用 `@P` 描述参数：

```java
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

挂到 `@AiService`：

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

| 注解/属性 | 作用 |
| --- | --- |
| `@Tool` | 描述方法作用，供模型判断何时调用 |
| `@P` | 描述参数含义，帮助模型生成正确参数 |
| `tools` | 指定包含工具方法的 Bean 名称，可配置多个 |

打开日志后，可以看到请求体中的 `tools` 数组，包含 `name`、`description`、`parameters`：

![Tools 请求日志](file:///D:/Java/data/AI/05-LangChain4j核心/23-tools-json-log.png)

图 5-28 LangChain4j 把 `@Tool` / `@P` 反射成 JSON Schema，放在请求的 `tools` 字段中。

预约对话的效果：

![预约信息收集](file:///D:/Java/data/AI/05-LangChain4j核心/27-reservation-dialog.png)

图 5-29 模型先回答业务问题，再引导预约并收集六项信息，最终触发 `addReservation`。

完整的数据库建表、实体、Mapper、Service 和 Tool 实现要点，见 [[04-LangChain4J与通义千问]] 的 Tools 章节（含补充实现）。

> 补充（非原 PPT）：Tools 的三条工程原则：
>
> - **描述面向意图**：`@Tool` 写“什么时候该用”，而不是“内部怎么实现”；参数描述写清格式和取值范围。
> - **副作用要可控**：写库、发消息、扣款这类工具必须做参数校验、幂等和确认，不能让模型随意触发。
> - **返回值要可序列化**：优先返回 DTO、`Map` 或字符串；不要返回带懒加载代理的 JPA 实体，否则序列化容易失败。

## 10. 核心 API 与配置速查

### 10.1 依赖速查

| 依赖 | 用途 |
| --- | --- |
| `langchain4j-open-ai` | 非 Spring 项目直接构建 `OpenAiChatModel` |
| `langchain4j-open-ai-spring-boot-starter` | Spring Boot 自动配置聊天/流式/嵌入模型 |
| `langchain4j-spring-boot-starter` | `@AiService` 声明式支持 |
| `langchain4j-reactor` | 流式返回 `Flux` |
| `langchain4j-easy-rag` | 内存向量库、内存向量模型、快速 RAG |
| `langchain4j-document-parser-apache-pdfbox` | PDF 解析 |
| `langchain4j-community-redis-spring-boot-starter` | RedisSearch 向量库 |
| `spring-boot-starter-data-redis` | 会话记忆持久化到 Redis |
| `spring-boot-starter-webflux` | 流式响应所需的 Reactor 支持 |

### 10.2 配置速查

| 配置前缀 | 作用 |
| --- | --- |
| `langchain4j.open-ai.chat-model` | 阻塞式聊天模型 |
| `langchain4j.open-ai.streaming-chat-model` | 流式聊天模型 |
| `langchain4j.open-ai.embedding-model` | 向量模型 |
| `langchain4j.community.redis` | RedisSearch 向量库连接 |
| `spring.data.redis` | 会话记忆使用的 Redis 连接 |

### 10.3 注解速查

| 注解 | 标注位置 | 作用 |
| --- | --- | --- |
| `@AiService` | 接口 | 声明 AI 服务，自动创建代理 |
| `@SystemMessage` | 接口方法 | 设置系统消息，可用 `fromResource` |
| `@UserMessage` | 接口方法 | 包装用户消息，支持 `{{it}}` / `{{变量}}` |
| `@V` | 方法参数 | 给参数命名，供用户消息模板引用 |
| `@MemoryId` | 方法参数 | 标记会话记忆 ID |
| `@Tool` | 工具方法 | 描述可被模型调用的函数 |
| `@P` | 工具方法参数 | 描述函数参数 |

### 10.4 核心类速查

| 类/接口 | 作用 |
| --- | --- |
| `OpenAiChatModel` | 阻塞式聊天模型 |
| `OpenAiStreamingChatModel` | 流式聊天模型 |
| `AiServices` | 为接口创建 AI 服务代理 |
| `ChatMemory` | 会话记忆接口 |
| `MessageWindowChatMemory` | 按消息条数淘汰的记忆实现 |
| `ChatMemoryProvider` | 按 `memoryId` 创建记忆对象 |
| `ChatMemoryStore` | 记忆的底层存储接口 |
| `DocumentLoader` | 文档加载 |
| `DocumentParser` | 文档解析 |
| `DocumentSplitter` | 文档切分 |
| `EmbeddingModel` | 文本向量化 |
| `EmbeddingStore` | 向量库操作 |
| `EmbeddingStoreIngestor` | 切分、向量化、入库流水线 |
| `ContentRetriever` | 在线检索器 |
| `EmbeddingStoreContentRetriever` | 基于向量库的检索器 |

## 11. 面试题与答案要点

### 11.1 LangChain4j 和直接 HTTP 调用有什么区别？

- 直接 HTTP 需要自己拼 JSON、解析响应、处理流式数据和历史消息。
- LangChain4j 提供模型对象、AiServices、消息注解、会话记忆、RAG、Tools 等封装。
- 简单调用可以用 HTTP；复杂应用用 LangChain4j 更省事，也更易维护。

### 11.2 AiServices 的作用是什么？

- 把 Java 接口声明成 AI 服务，底层用动态代理调用模型。
- 通过注解配置系统提示词、用户消息、记忆、检索器、工具。
- 业务代码面向接口，减少手动拼 Prompt 和解析响应。
- 声明式 `@AiService` 可自动注册到 IOC 容器。

### 11.3 流式调用怎么实现？

- 引入 `spring-boot-starter-webflux` 和 `langchain4j-reactor`。
- 配置 `streaming-chat-model`，接口返回 `Flux<String>`。
- `@AiService` 指定 `streamingChatModel`。
- Controller 设置 `produces = "text/html;charset=utf-8"` 避免中文乱码。

### 11.4 SystemMessage 和 UserMessage 有什么区别？

- `SystemMessage` 设定角色、规则、边界，优先级更高，适合放长期稳定的指令。
- `UserMessage` 包装用户输入，可在前后拼接内容，适合单次任务模板。
- 多参数方法必须用 `@UserMessage` 明确用户输入参数。
- 系统消息较长时用 `fromResource` 放到资源文件。

### 11.5 会话记忆如何隔离和持久化？

- 隔离：`ChatMemoryProvider` 按 `memoryId` 创建不同 `ChatMemory`，接口方法用 `@MemoryId` 接收。
- 持久化：实现 `ChatMemoryStore` 的 `getMessages`、`updateMessages`、`deleteMessages`，可存 Redis、MySQL 或文件。
- 临时方案：`MessageWindowChatMemory` 只保留最近 N 条消息。
- 默认内存 Store 重启即丢，生产环境必须换外部存储。

### 11.6 RAG 的完整链路是什么？

- 入库：Document Loader → Document Parser → Document → Document Splitter → TextSegment → EmbeddingModel → Embedding → EmbeddingStore。
- 检索：Query → EmbeddingModel → Query Embedding → EmbeddingStore 相似度检索 → Relevant Segments。
- 生成：Query + Relevant Segments → Prompt → LLM → 回答。
- 入库和检索必须使用同一个 embedding 模型。

### 11.7 为什么要给文本片段设置重叠？

- 防止语义被切断：上一段结尾的关键词可能不在下一段出现。
- 保持上下文连贯，提高跨片段问题的召回率。
- 重叠太大会增加存储和 token 成本，需要平衡。

### 11.8 Function Calling 的流程是什么？

- 应用把函数名称、作用、入参描述给模型。
- 模型判断需要调用时，返回函数名和参数。
- 应用执行本地函数，把结果追加到上下文。
- 循环直到模型不再调用函数，返回最终答案。

### 11.9 内存向量库和 RedisSearch 怎么选？

- 内存向量库：零部署，适合演示和测试；重启丢失，每次启动都要重新向量化。
- RedisSearch：持久化、支持多实例，适合已有 Redis 的项目。
- 大规模向量检索可选 Milvus、Qdrant；已有 PostgreSQL 可选 pgvector。
- 选择时综合考虑数据规模、部署方式、运维成本、混合搜索需求。

## 12. 易错点

- API-KEY 不要硬编码，优先环境变量；配置后记得重启 IDE。
- `@AiService` 使用 `EXPLICIT` 时，Bean 名称必须与容器中的实际名称一致。
- 流式接口返回 `Flux<String>`，需要 Reactor 依赖，并注意中文编码。
- `@UserMessage` 的 `{{it}}` 是固定写法；自定义名称要用 `@V`。
- 多参数方法必须显式标注 `@UserMessage`，否则框架不知道哪个是用户输入。
- 使用 `chatMemoryProvider` 时不要再配全局 `chatMemory`。
- `maxMessages(20)` 是消息条数，约等于 10 轮对话。
- 默认 `ChatMemoryStore` 是内存实现，重启即丢。
- `InMemoryEmbeddingStore` 重启即丢，且每次启动重复向量化会产生费用。
- 入库和检索必须使用同一个 embedding 模型。
- `minScore` 过高会检索不到内容，过低会引入噪声。
- `@Bean` 的入库方法不要长期保留，否则每次启动都重新入库。
- RedisSearch 要用 `redislabs/redisearch` 镜像，普通 Redis 镜像不支持向量检索。
- Tools 方法有副作用时要校验参数、保证幂等，并避免返回不可序列化的对象。
- 课程依赖版本为 `1.0.1` / `1.0.1-beta6`，升级版本后要核对包名、配置键和方法签名。

---

> 📎 **相关笔记**：[[04-LangChain4J与通义千问]] · [[02-大模型RAG开发]] · [[AI/AI 索引|AI 索引]]