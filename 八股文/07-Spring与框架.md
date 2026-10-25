# Spring 与框架

> 本笔记整理自八股文题库的「IOC/AOP、SpringMVC、SpringBoot、事务、循环依赖与自动装配」部分，保留原题表述与原文顺序。跨模块主笔记：[[SSM框架/SSM框架 索引|SSM]] · [[SpringBoot2/SpringBoot2 索引|SpringBoot2]]。

## Spring IOC

IOC 即控制反转，指的是将对象的控制权 交给了Spring容器， 容器负责创建和管理对象， 我们只需要接受容器注入的对象。

**优点：**

- 降低耦合：在非IOC的传统编程中，对象的创建和依赖管理硬编码在业务逻辑中，与具体实现类强绑定， 一旦要更换实现类，就需要改动业务代码， 而IOC模式下，在业务类里依赖接口，而非具体实现， 如果要更换实现类， 只需要在配置类中更换实现类。
- 不需要重复创建相同的对象， 浪费内存，Spring容器中的Bean对象默认是单例的

**高耦合示例**

```java
public class OrderService {
    // 直接依赖具体实现类 ,如果需要更换实现类 ,必须修改OrderService的代码
    private PaymentProcessor paymentProcessor = new AlipayProcessor();
    public void processOrder() {
        paymentProcessor.charge();
    }
}
```
**IOC解耦示例**

```java
public class OrderService {
    // 依赖接口 ，而非具体实现
    @Resource
    private PaymentProcessor paymentProcessor;
    public void processOrder() {
        paymentProcessor.charge();
    }
}
```
**如果要更换实现类，在这修改**

```java
@Configuration
public class AppConfig {
    @Bean
    public PaymentProcessor paymentProcessor() {
        return new WechatPayProcessor(); //修改这行代码， 更换实现
    }
}
```

## Spring AOP

AOP 即面向切面编程，用作无侵入式的代码增强， 一般对公共的行为或者逻辑进行抽取，将横切逻辑和业务逻辑分离，提升代码复用性和可维护性。

**应用场景：**

- 权限验证
- 记录操作日志
- Spring事务的实现即AOP

实现方式：动态代理

- JDK动态代理：基于接口，生成接口的代理类。
- CGLIB代理：基于类， 通过继承目标类生成子类， 重写方法增强。

Spring AOP根据目标对象是否实现接口， 选择不同的代理机制：如果目标类实现了接口，则使用JDK动态代理

如果目标类未实现接口，则使用CGLIB代理

## Spring 常见注解

| 注解 | 说明 |
| --- | --- |
| @Component、@Controller、 @Service、@Repository | 使用在类上用于实例化Bean |
| @Autowired | 使用在字段上用于根据类型依赖注入 |
| @Qualifier | 结合@Autowired一起使用 用于根据名称进行依赖注入 |
| @Scope | 标注Bean的作用范围 |
| @Configuration | 指定当前类是一个spring配置类， 当创建容器时会从该类上加载注解 |
| @Componentscan | 用于指定spring在初始化容器时要扫描的包 |
| @Bean | 使用在方法上，标注将该方法的返回值存储到Spring容器中 |
| @lmport | 使用@lmport导入的类会被Spring加载到IOC容器中 |
| @Aspect、@Before、@After、 @Around、@Pointcut | 用于切面编程（Aop) |

## SpringMVC

| 注解 | 说明 |
| --- | --- |
| @RequestMapping | 用于映射请求路径， 可以定义在类上和方法上，用于类上，则表示类中的所有的方法都是以该地址作为父路径 |
| @Requestbody | 注解实现接收Http请求的Json数据，将Json转换为Java对象 |
| @RequestParam | 指定请求参数的名称 |
| @PathVariable | 从请求路径下中获取请求参数，传递给方法的形式参数 |
| @ResponseBody | 注解实现将Controller方法返回对象转化为Json对象响应给客户端 |
| @RequestHeader | 获取指定的请求头数据 |
| @RestController | @Controller+@ResponseBody |

## SpringBoot

| 注解 | 说明 |
| --- | --- |
| @SpringBootConfiguration | 组合了多种注解 |
| @EnableAutoConfiguration | 开启自动装配功能 |
| @Componentscan | Spring 组件扫描 |

事务管理在系统开发中是不可缺少的一部分，Spring提供了很好事务管理机制，主要分为编程式事务和声明式事务两种。

## 编程式事务

基于底层的APl 如 PlatformTransactionManager、TransactionDefinition 和

TransactionTemplate 等核心接口， 开发者完全可以通过编程的方式来进行事务管理。

编程式事务方式需要是开发者在代码中手动的管理事务的开启、提交、回滚等操作。

## 声明式事务

Spring 支持声明式事务管理， 即@Transactional注解，声明式事务管理建立在AOP之上。

其本质是通过AOP功能，对加了@Transactional注解的方法前后进行拦截，

在执行目标方法之前开启事务，在执行完目标方法之后根据执行情况提交事务或者回滚事务。

### 声明式事务的优点

声明式事务帮助我们节省了很多代码，他会自动帮我们进行事务的开启、提交以及回滚等操作， 把程序员从事务管理中解放出来。

声明式事务管理使用了 AOP 实现的，本质就是在目标方法执行前后进行拦截。在目标方法执行前加入或创建一个事务，在执行方法执行后，根据实际情况选择提交或是回滚事务。

使用这种方式，对代码没有侵入性， 方法内只需要写业务逻辑就可以了。

### 声明式事务的粒度问题

首先，声明式事务有一个局限，那就是他的最小粒度要作用在方法上。

即 如果想要给一部分代码块增加事务的话，那就需要把这个部分代码块单独独立出来作为一个方法。

因为声明式事务是通过注解的， 这就会导致一个问题，那就是这个事务有可能被开发者忽略。

事务被忽略了有什么问题呢？如果开发者没有注意到一个方法是被事务嵌套的，那么就可能会在方法中加入一些如 RPC远程调用、消息发送、缓存更新、文件写入等操作。

**这些操作如果被包在事务中，有两个问题：**

1. 这些操作自身是无法回滚的， 这就会导致数据的不一致。可能RPC调用成功了，但是本地事务回滚了， 可是RPC调用无法回滚了
2. 在事务中有远程调用，就会拉长整个事务。那么就会导致本事务的数据库连接一直被占用，那么如果类似操作过多，就会导致数据库连接池耗尽。
如果是编程式事务的话，业务代码中就会清清楚楚看到什么地方开启事务，什么地方提交，什么

时候回滚。这样有人改这段代码的时候，就会强制他考虑要加的代码是否应该在方法事务内。

> 注：有些人可能会说， 已经有了声明式事务，但是写代码的人没注意， 这能怪谁 话虽然是这么说，但是我们还是希望可以通过一些机制或者规范， 降低这些问题发生的概率。 因为有些时候，声明式事务确实不够明显。

## Spring Bean 的作用域

理论上来说作用域只有 两种

1. Singleton 单例作用域：
  - 每一次从IOC容器获取指定Bean对象时，都会返回同一个实例对象
  - 适用场景：无状态Bean， 如工具类、配置类、服务类等

2. Prototype 原型作用域：
  - 每一次从IOC容器获取指定Bean对象时，都会返回一个新的实例对象
  - 适用场景：有状态Bean， 需要隔离状态的场景

但在基于Spring框架下的Web应用中，增加了三种作用域

1. Request 请求作用域：
  - 针对每一次HTTP请求都会创建一个新的Bean
  - 适用场景：HTTP请求级别的数据， 如表单提交、请求参数处理

2. Session 会话作用域：
  - 针对Session会话， 同一个Session共享同一个Bean实例，不同的Session则产生不同的Bean实例
  - 适用场景：用户会话数据， 如登录信息、用户偏好设置

3. Application 应用作用域：
  - 整个Web应用中共享一个实例， 类似于 ServletContext 级别
  - 适用场景：全局共享的配置或资源， 如缓存、应用级配置

## SpringBoot 自动装配原理

1. 在SpringBoot项目的引导类上有一个注解叫 @SpringBootApplication，
在这个注解的里面， 又有一个注解叫做：@EnableAutoConfiguration 即触发了自动装配

2. @EnableAutoConfiguration 是实现自动化配置的核心注解。
该注解里面 通过 @Import 注解导入了一个 自动配置导入选择器类AutoConfigurationImportSelector

在 自动配置导入选择器类 里会读取（该项目和该项目引用的）Jar 包的 META- INF/spring.factories文件

在这些文件中记录了配置类的全类名， 通过全类名找到对应的配置类， 配置类中定义了Bean，

再判断定义的Bean是否加了条件注解是否生效决定是否将其Bean的实例加载到Spring容器中

（条件注解例如@ConditionalOnClass(xx)判断是否有对应的class文件(依赖)， 如果有则加载该Bean）

**解释：**

例如一个配置类中定义了Bean， 同时上面有

```java
@ConditionalOnClass(name = "org.apache.kafka.clients.producer.Producer")

```

则此时需要判断 org.apache.kafka.clients.producer.Producer 类是否已引入 （依赖是否引入）未引入则无需将该Bean加入Spring容器， 已引入则需要将该Bean加入Spring容器

```java
@Configuration
public class FeatureConfig {
    @Bean
    @ConditionalOnClass(name = "org.apache.kafka.clients.producer.Producer" )
    public KafkaProducer kafkaProducer() {
        // 仅当  Kafka Producer 类存在时注册该  Bean
    }
}
```

![SpringBoot 自动装配原理](file:///D:/Java/data/八股文/07-Spring与框架/96f513224212.png)

## Spring MVC 的执行流程

1.用户发出请求到前端控制器DispatcherServlet

2.DispatcherServlet收到请求调用HandlerMapping（处理器映射器）

3.HandlerMapping找到具体的处理器， 返回处理器执行链（包括处理器和拦截器） 给DispatcherServlet

4.DispatcherServlet调用HandlerAdapter（处理器适配器）

5.HandlerAdapter经过适配调用具体的处理器（Handler即Controller的某个方法）

6.在方法上添加了@ResponseBody， 因此通过HttpMessageConverter来返回结果转换为JSON并响应

**面试问题引入：**

当面试官问到你了解哪些设计模式，也可以选择说 学习过Spring的源码， 其中就用了什么设计模式

## Spring 中的设计模式

### 单例模式

默认情况下，Spring IOC 容器中会确保每个 Bean 只有一个实例，该实例在整个应用中被共享使⽤

(当然Spring Bean 也有其他的作用域，则不是单例模式)

好处：对象复用，避免了频繁创建和销毁对象的开销，减少内存占用和 GC 压力

**实现原理：**

1. 在Spring容器启动时，会创建 非懒加载的 Bean， 并且将其存入缓存
(ConcurrentHashMap) 中，后续对 Bean 的请求会从缓存中获取。是一种饿汉式的单例实现。

2. 而如果使用了 @Lazy 注解或在 Bean 定义中设置 lazy-init=true，那么该 Bean 只有在第一次被使用时才会初始化，称为懒加载。是一种懒汉式的单例实现。

### 工厂模式

Spring IOC 容器就像是一个工厂， 封装了创建对象的细节

我们通过（id或name或类型） getBean 方法从工厂(容器)中获取对象

好处：解除了耦合，对象的创建和使用分离；且集中管理对象的生命周期

### 代理模式

Spring AOP 面向切面编程 使用了代理模式

当配置了一个切面，Spring会创建目标对象的代理，拦截对应的方法调用，在方法执行前后进行增强

好处：无侵入式的代码增强

### 责任链模式

我们知道 SpringMVC 的执行流程中，会涉及到 DispatcherServlet、HandlerExecutionChain 处理器执行链等等。HandlerExecutionChain 处理器执行链 中封装了包括 拦截器、处理器

例如一个请求过程中， 可能经过 很多拦截器(实现前置处理、后置处理)，每个拦截器做的事情不一样， 这就是责任链，Spring MVC 通过责任链模式将请求处理流程拆解为多个可插拔的拦截器节点好处：我们可以灵活的动态扩展处理流程，若将所有拦截逻辑硬编码在单一处理流程中，会导致代码臃肿、难以维护， 而责任链模式每个节点只需关注自己的职责。

### 模板方法模式

模版方法模式： (抽象)父类定义一个操作中的算法骨架，将具体步骤实现延迟到子类中，调用时调用父类的骨架方法， 具体步骤则是调用子类的方法。

Spring 提供了许多模板类，例如 JdbcTemplate(数据库操作)、RestTemplate(HTTP客户端操作)好处：简化了我们对于技术的使用。

### 观察者模式

观察者模式，也称为发布-订阅模式，Spring 中也有对应的机制： 事件发布-监听机制

存在着一对多的关系， 多个观察者监听(订阅)某个事件， 当这个事件被发布时， 多个观察者就能监听到， 进而去做观察者的逻辑

好处：使用该机制可以将相互耦合的代码解耦，从而方便功能的拓展和调整。

主逻辑只需要执行关键路径， 附带的(不断扩展的)操作可以由观察者监听事件发布后完成

## SpringBoot 的启动流程

面试官问法：SpringBoot的程序是怎么启动起来的 或者 SpringBoot启动过程中做了哪些事情

1. 入口启动、初始化配置
  - 执行 main 方法，调用 SpringApplication.run(主类.class, args)
  - 加载 META-INF/spring.factories 中配置的初始化器（ApplicationContext Initialize r） 和监听器（ApplicationListener）

2. 创建应用程序上下文，createApplicationContext，创建 bean工厂对象
3. 刷新应用程序上下文
- 核心方法 refresh()：

```java
a. 配置工厂对象， 包括上下文类加载器，对象发布处理器， beanFactoryPostProcessor
b. 注册并实例化bean工厂发布处理器， 并且调用这些处理器，对包扫描（主要是class文件）
c. 注册并实例化bean发布处理器 beanPostProcessor
d. 初始化一些与上下文有特别关系的bean对象（创建tomcat服务器）
e. 实例化所有bean工厂缓存的bean对象 (剩下的)
f. 发布通知-上下文刷新完成（启动tomcat服务器）

```

4. 启动完成
  - 发布 ApplicationReadyEvent 事件， 通知监听者启动程序已完成

参考文档：https://www.cnblogs.com/Narule/p/14253754.html

## 循环依赖问题

在Spring框架中，循环依赖是指两个或多个bean之间相互依赖，形成了一个循环引用的情况。如果不加以处理这种情况会导致应用程序启动失败。

```java
@Service
public class ServiceA{
    @Autowired
    private ServiceB serviceB;
}
@Service
public class ServiceB{
    @Autowired
    private ServiceA serviceA;
}

```

在Spring中，解决循环依赖的方式就是引入了三级缓存。但是，Spring解决循环依赖是有一定限制的

1. 要求互相依赖的Bean必须要是单例的Bean
2. 依赖注入的方式不能都是构造函数注入的方式
![循环依赖问题](file:///D:/Java/data/八股文/07-Spring与框架/add4bedcf346.png)

## 三级缓存 && 解决原理

Spring 通过三级缓存机制提前暴露未完全初始化的Bean实例，解决单例模式下的循环依赖问题。

三级缓存结构

1. 一级缓存（singletonObjects）：存储完全初始化后的单例Bean， 可直接使用。
2. 二级缓存（earlySingletonObjects）：保存实例化但未完成初始化的Bean早期引用。
3. 三级缓存（singletonFactories）：存储Bean的创建工厂ObjectFactory， 通过调用其
GetObject 方法， 可以获取到早期暴露出去的 Bean；在该 Bean 要被其他 Bean 引用时，

Spring 就会用工厂对象创建出该 Bean 的实例对象， 最终当该 Bean 完成构造的所有步骤后就会将该 Bean 放入到一级缓存中

Spring 中 Bean 的创建过程其实可以分成两步，第一步叫做实例化，第二步叫做初始化。

- 实例化的过程只需要调用构造函数把对象创建出来并给他分配内存空间
- 而初始化则是给对象的属性进行赋值

而 Spring 之所以可以解决循环依赖就是因为对象的初始化是可以延后的，也就是说， 当我创建一个Bean ServiceA的时候，会先把这个对象实例化出来，然后再初始化其中的serviceB属性。

而当一个对象只进行了实例化，但是还没有进行初始化时， 我们称之为半成品对象。所以，所谓半成品对象， 其实只是 bean 对象的一个空壳子， 还没有进行属性注入和初始化。

当两个Bean在初始化过程中互相依赖的时候， 如初始化A发现他依赖了B， 继续去初始化B，发现他又依赖了A。此时的解决流程（以A依赖B，B依赖A为例）

1. 创建Bean A：
  - 实例化A（调用构造函数），将A的ObjectFactory存入三级缓存。

2. 填充A的属性：
  - 发现需要注入B，触发B的创建。

3. 创建Bean B：
  - 实例化B， 并将B的ObjectFactory存入三级缓存。

4. 填充B的属性：
  - 发现需要注入A，此时从三级缓存获取A的ObjectFactory，生成早期对象并移至二级缓存。

5. B完成初始化：
  - B的早期对象注入A后， B继续完成属性填充和初始化， 最终存入一级缓存。

6. A完成初始化：
  - A获取到B实例后完成初始化，存入一级缓存，移除二、三级缓存中的记录。

这两个注解都是用于实现依赖注入 （Dependency Injection, DI）。

它告诉Spring容器在创建bean的时候， 自动注入相关的依赖。

## 不同点

### byName 和 byType 匹配顺序不同

Autowired 在获取 Bean 的时候， 先是 byType 即类型查找的方式， 再是 byName 即 Bean 名称查找的方式。

即先在 Spring 容器中找以 Bean 为类型的 Bean 实例

如果找不到或者找到多个 Bean，则会通过 fieldName 来找。

```java
@Component("beanOne")
class Beanone implements Bean {}
@Component("beanTwo")
class BeanTwo implements Bean {}
@Service
class Test {
    // 此时会报错，先byType找到两个bean: beanone和beanTwo
    // 然后通过byName(bean)仍然没办法匹配
    @Autowired
    private Bean bean;
    // 先byType找到两个bean，然后通过byName确认最后要注入的bean
    @Autowired
    private Bean beanOne;
    // 先byType找到两个bean，然后通过byName确认最后要注入的bean
    @Autowired
    @Qualifier("beanOne")
    private Bean bean;
}

```

Resource 在获取 Bean 的时候， 和 Autowired 恰好相反， 先是 byName 即 Bean 名称查找的方式， 然后再是 byType 即类型查找的方式。当然我们也可以通过注解中的参数显示指定通过哪种方式。

```java
@Component("beanOne")
class Beanone implements Bean {}
@Component("beanTwo")
class BeanTwo implements Bean {}
@Service
class Test {
    // 此时会报错，先byName，发现没有找到bean
    // 然后通过byType找到了两个Bean:beanone和beanTwo，仍然没办法匹配
    @Resource
    private Bean bean;
    //先byName直接找到了beanOne，然后注入
    @Resource
    private Bean beanOne;
    //显式指定通过byType注入 ，能注入成功
    @Resource(type = Beanone.class)
    private Bean bean;
}

```

### 作用域不同

- Autowired 可以作用在 构造器， 字段，Setter 方法上
- Resource 只可以使用在 字段，Setter 方法上，不支持构造器注入

### 支持方不同

- Autowired 是 Spring 提供的自动注入注解， 只有Spring容器会支持， 如果不使用Spring容器， 改成其他的， 是需要修改代码的
- Resource 是 JDK 官方提供的自动注入注解。它等于说是一个标准或者约定，所有的IOC容器都会支持这个注解。假如系统容器从 Spring 迁移到其他 IOC 容器中， 是不需要修改代码的

## 事务失效的原因

```java
@Transactional 定义的声明式事务，在以下几个场景中会导致事务失效

```

1. @Transactional 应用在非 public 修饰的方法上，例如是 private 修饰
private方法， 只会在当前对象中的其他方法中调用，也就是会进行对象的自调用， 这种情况是用 this调用的， 并不会走到代理对象， 而@Transactional是基于动态代理实现的，所以代理会失效。则事务也会失效

2. final、static 方法
由于AOP是通过创建代理对象来实现的， 而无法对final方法进行子类化和覆盖，所以无法拦截这些方法。

还有就是调用static方法， 因为这类方法是属于这个类的， 并不是对象的，所以无法被AOP

3. 异常被catch捕获导致@Transactional失效
因为异常被捕获，所以就没办法基于异常进行rolback了，所以事务会失效

```java
public class MyService{
    @Transactional
    public void dosomething(){
        try{
            doInternal();
        }catch(Exception e){
            logger.error(e);
        }
}
}

```

4. 事务中用了多线程

```java
@Transactional 的事务管理使用的是 ThreadLocal 机制来存储事务上下文， 而 ThreadLocal 变量是线程隔离的， 即每个线程都有自己的事务上下文副本。因此，在多线程环境下，Spring 的声

```

明式事务会失效， 即新线程中的操作不会被包含在原有的事务中。

5. @Transactional 注解属性 rollbackFor 设置错误

```java
public class MyService{
@Transactional(rollbackFor = RuntimeException.class)
private void doInternal(){
System.out.println("Doing internal work...");
}
}
```

以上， 如果发生 非RuntimeException的异常，则事务不会回滚， 即导致事务失效。所以需要指定为(rollbackFor =Exception.class)

在Web应用开发中，确保应用可以平稳可靠的关闭是至关重要的。在我们常用的Spring Boot中其实提供了内置功能来优雅地处理应用程序的关闭的能力。

优雅停机：是以受控方式终止应用程序的过程， 允许它完成任何正在进行的任务，释放资源， 并确保数据的完整性。与突然终止应用程序不同，优雅停机确保所有进程都得到优雅停止， 以防止潜在的数据损坏或丢失。

从Spring Boot 2.3开始，SpringBoot内置了优雅停机的功能。想要启用优雅停机很简单， 只需在application.properties 文件中添加一行代码

```yaml
server.shutdown=gracefu

```

通过这个设置， 当停止服务器时， 它将不再接受新的请求。并且服务器也不会立即关闭， 而是等待正在进行的请求处理完。这个等待的时间我们是可以自定义的:

```yaml
spring.lifecycle.timeout-per-shutdown-phase=2m

```

默认的等待时长是30秒， 通过以上配置可以将这个等待时长延长到 2分钟

### AOT 编译

Ahead-Of-Time， 即预先编译， 这是相对于我们熟知的 Just-In-Time (JIT， 即时编译) 来说的。

相比于JT编译，AOT指的是在程序运行前编译， 这样就可以避免在运行时的编译性能消耗和内存消耗， 可以在程序运行初期就达到最高性能、也可以显著的加快程序的启动。

AOT的引入， 意味着Spring生态正式引入了提前编译技术，相比于JIT编译，AOT有助于优化Spring框架启动慢占用内存多、以及垃圾无法被回收等问题。

### Spring Native

在新版本中引入了 Spring Native，有了 Spring Native，Spring 可以不再依赖 Java 虚拟机， 而是基于 GraalVM 将 Spring 应用程序编译成原生镜像（native image），提供了一种新的方式来部署 Spring 应用， 这种部署 Spring 的方式是云原生友好的。

Spring Native 的优点是编译出来的原生 Spring 应用可以作为一个独立的可执行文件进行部署，而不需要安装 JVM， 而且启动时间非常短并且消耗更少的资源， 它的缺点就是构建时长要比JVM更长一些。

---

> 📎 **相关笔记**：[[SSM框架/SSM框架 索引|SSM]] · [[SpringBoot2/SpringBoot2 索引|SpringBoot2]] · [[八股文/10-设计模式与AI|设计模式]]
