# JUC 并发

> 本笔记整理自八股文题库的「线程、线程池、锁、CAS、JMM、ThreadLocal、原子类与并发工具」部分，保留原题表述与原文顺序。跨模块主笔记：[[JUC/JUC 索引|JUC]]。

## 线程的状态及流转

Java中在Thread类里有一个枚举Enum类明确规定了Java线程的六种状态

1. 创建线程对象 --> 新建状态 (NEW)
2. 调用start方法 --> 就绪状态（Runnable），就绪状态如果抢到CPU的执行权则变为运行（但在Java中状态表示依然是就绪状态Runnable）
3. （从运行中） 遇到无法获取锁对象时 --> 阻塞状态（Blocked）
4. （从运行中） 遇到wait方法时 --> 等待状态（Waiting）
5. （从运行中） 遇到sleep方法时 --> 计时等待状态（Timed_Waiting）
6. 本身的 Run 方法执行完毕后 --> 结束状态（Terminated）

## 创建线程的方式

1. 继承Thread类
2. 实现Runnable接口
3. 实现Callable接口结合FutureTask， 适用于执行有返回值的任务
4. 通过线程池创建线程

## 多线程的应用

- 软件中的耗时操作：
  - 拷贝、迁移大文件
  - 加载大量的资源文件
- 所有的聊天软件
- 所有的后台服务器

## 线程问题

**A线程里启动一个B线程，A线程需要等待B线程执行完之后才去执行，都有那些方法可以实现这种场景？**

方法一： Thread.join() 方法

方法二： 并发工具类：原理：调用 b.join() 后，A 线程会阻塞， 直到 B 线程完全运行结束。

```java
public class JoinDemo {
    public static void main(String [] args) throws InterruptedException {
        // 当前线程， 即A 线程（ 主线程）
        Thread aThread = Thread.currentThread();
        // 创建  B 线程
        Thread bThread = new Thread(() -> {
            System.out.println("B 线程开始执行");
            try {
                Thread.sleep(2000); // 模拟业务耗时
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            System.out.println("B 线程执行完毕");
        });
        // A 线程启动  B 线程
        bThread.start();
        // A 线程阻塞，等待  B 线程执行完
        bThread.join();
        // B 执行完后，A 才会执行这里
        System.out.println("A 线程继续执行");
    }
}

```

**CountDownLatch**

原理：初始化计数器为 1， B 执行完计数器减为 0，A 解除阻塞。

```java
import java.util.concurrent.CountDownLatch;
public class CountDownLatchDemo {
    public static void main(String [] args) throws InterruptedException {
        // 计数器  = 1，等待  1 个线程
        CountDownLatch latch = new CountDownLatch(1);
        Thread bThread = new Thread(() -> {
            System.out.println("B 线程开始执行");
            try {
                Thread.sleep(2000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            System.out.println("B 线程执行完毕");
            latch.countDown(); // B 执行完，计数器  -1
        });
        bThread.start();
        latch.await(); // A 线程阻塞，直到计数器为  0
        System.out.println("A 线程继续执行");
    }
}

```

方法三： CompletableFuture

```java
import java.util.concurrent.CompletableFuture;
public class CompletableFutureDemo {
    public static void main(String [] args) {
        System.out.println("A 线程启动  B 线程");
        // 启动  B 线程，并等待它完成
        CompletableFuture.runAsync(() -> {
            System.out.println("B 线程执行");
            try { Thread.sleep(2000); } catch (InterruptedException e) {}
            System.out.println("B 线程执行完毕");
        }).join(); // 阻塞  A 线程，等待  B 完成       (注意这里)
        System.out.println("A 线程继续执行");
    }
}

```

## 线程池

### 使用线程池的好处

通过使用线程池起到资源管理、线程复用的效果， 避免频繁地创建和销毁线程带来的性能开销。

具体解释：线程的创建和销毁是一项开销较大的操作，频繁地创建和销毁线程会耗费大量的系统

资源。通过使用线程池， 可以事先创建一定数量的线程， 并将它们放入池中， 需要执行任务时直接

从池子中获取复用线程。这样可以避免频繁地创建和销毁线程，提高系统的资源利用率。

### 线程池的七个参数

- 参数一：核心线程数量
- 参数二： 最大线程数量
- 参数三：临时线程最大存活时间
- 参数四：临时线程最大存活时间的单位
- 参数五：任务阻塞队列
- 参数六：线程工厂，用于创建线程的工厂类
- 参数七：任务的拒绝策略

### 线程池提交任务的流程

1. 提交任务时，会先让核心线程去执行任务
2. 如果核心线程都在工作，则先将任务放到阻塞队列
3. 如果阻塞队列满了，则会创建临时线程去执行任务（核心线程+临时线程 不能超过最大线程参数值）
4. 如果达到最大线程数，就会触发拒绝策略

### 任务拒绝策略有哪些， 怎么选择？

1. AbortPolicy：这是默认的拒绝策略，会抛出RejectedExecutionException异常。新任务会被立即拒绝，不会加入到任务队列中，也不会执行。虽然它是默认策略，但实际场景中需谨慎使用。如果任务重要性高， 直接抛出异常可能导致关键任务丢失（如订单支付、消息通知）。通常更适合允许部分任务失败的场景。
2. DiscardPolicy：会丢弃新的任务而且不会抛出异常。新任务提交后会被默默地丢弃，不会有任何提示或执行。适用场景更偏向允许丢失少量任务且不影响系统整体逻辑的轻量级任务（如心跳上报、临时缓存更新）
3. DiscardOldestPolicy：会先尝试将任务队列中最早/旧的任务删除，然后再尝试提交新任务。这个策略适用于一些实时性要求较高的场景， 适用场景应强调新任务比旧任务更重要（如实时数据处理场景中，新数据比旧数据更有价值）
4. CallerRunsPolicy：这个策略将任务回退给调用线程， 而不会抛出异常。调用线程会尝试执行任务。这个策略可以降低任务提交速度， 适合不希望任务丢失且能接受任务执行延迟的场景

### 核心线程数和最大线程数怎么设定？

应用类型

- CPU密集型：对于CPU密集型的任务 (如计算密集型任务)，线程数公式：CPU核数+1， 因为这些任务主要消耗CPU资源，CPU并不空闲无法切换线程上下文，所以线程数不需要这么

多。

- I/O密集型：对于任务涉及大量网络IO或磁盘IO，则可以配置更多的线程，线程数公式：

2*CPU核数， 因为线程在IO阻塞等待时，CPU可以切换线程上下文去处理其他任务。

上述两个公式其实来源于这个公式： 线程数 = CPU核数 * （1 + 线程等待时间 / 线程运行总时间）

CPU密集型中线程等待时间无限趋近于0，则线程数 = CPU核数 上面说的CPU核数+1（备用线程）

IO密集型中线程等待时间无限趋近于线程总运行时间，所以线程数 = CPU核数 * (1+1)

这些公式只是推荐值，但是不建议硬套公式， 因为一个应用中， 可能有很多个线程池， 除了线程池 也还有很多其他线程， 再者说有很多请求涉及到IO操作和计算型操作，所以先根据公式/推荐值大致的设置一个数值， 再进行压测 (例如多线程并发去请求对应的接口，查看执行完毕所有请求的耗时)， 结合实际业务情况来实践优化， 最终达到一个相对合理的值， 目标：尽可能让CPU达到更高的利用率， 能够较快处理大量并发请求。

压测过程中，确定核心线程数的值， 另外可以在压测效果差不多的情况下， 选定最大线程数的值。

注意：设置的线程数并不是越多越好，频繁的线程上下文切换， 反而可能导致系统性能降低

### 上线后你会关注线程池的哪些指标？

一、运行时状态指标

1. 核心线程数： 当前活跃的核心线程数量，用于判断是否达到配置的阈值
  - 异常表现：若长期低于配置值， 可能线程池被过度回收；若长期等于配置值且任务堆积，可能需调整增大核心线程数

2. 活跃线程数： 当前正在执行任务的线程数量
  - 关注点：若持续接近或等于最大线程数，说明线程池负载高， 可能需扩容或优化任务处理逻辑。

3. 队列大小：任务队列中等待执行的任务数量
  - 关注点：若队列长期满载， 可能是任务处理速度慢， 可能需增大队列容量或优化任务处理速度

二、任务处理效率指标

1. 任务提交速率：单位时间内提交到线程池的任务数量
  - 关注点：结合任务完成速率判断系统吞吐量是否饱和

2. 任务完成速率：单位时间内线程池完成的任务数量
  - 关注点：完成速率应接近提交速率， 否则存在任务堆积风险

3. 任务平均耗时：单个任务从提交到完成的平均时间
  - 关注点：耗时突增可能代码存在性能问题（如慢 SQL、死锁）

4. 任务等待时间：任务在队列中等待执行的平均时间
  - 关注点：太长的原因可能是配置的核心线程数不足， 或任务执行耗时增加

三、资源占用指标

1. CPU 使用率：线程池所在节点的 CPU 占用情况
  - 关注点：
    - 若 CPU 使用率高但任务吞吐量低， 可能存在计算密集型任务或锁竞争
    - 若 CPU 使用率低但队列堆积， 可能 I/O 阻塞或线程数不足

2. 内存占用： 线程池任务占用的堆内存或直接内存
  - 关注点：任务中若有大对象或内存泄漏， 可能引发 OOM

四、异常情况指标

1. 拒绝任务数： 因队列满且线程数达上限被拒绝的任务数量
  - 处理策略：调整 最大线程数/核心线程数 或队列容量

2. 线程创建/销毁频率：单位时间内线程的创建和销毁次数
  - 关注点：频繁线程创建销毁（线程池震荡） 可能因 临时线程存活时间 过短或任务突发性⾼

3. 线程阻塞时间：线程因 I/O、锁等待或资源竞争被阻塞的时间占比
  - 工具支持：通过 APM 工具（如 SkyWalking） 或 ThreadMXBean 监控

4. 死锁检测：监控线程池中是否发生死锁（通过 ThreadMXBean.findDeadlockedThread s()）
  - 关注点：避免任务中嵌套同步锁或长时间占用共享资源

### 为什么不推荐使用 jdk 的 Executors 创建线程池？

Executors 是一个工厂类， 它提供了用于创建不同类型线程池的静态方法

线程池不允许使用 Executors 去创建， 而是通过ThreadPoolExecutor的方式，规避资源耗尽的风险

Executors 返回的线程池对象的弊端如下：

- newFixedThreadPool() 和 newSingleThreadPool()
  - 允许的请求队列长度为 Integer.MAX_VALUE， 可能会堆积大量的请求，从而导致 OOM
- newCachedThreadPool()
  - 允许的创建线程数量为 Integer.MAX VALUE， 可能会创建大量的线程，从而导致 OOM

### 动态线程池 (扩展内容,待新增)

前面说到一个应用中的情况是非常复杂的，很多的线程池，请求处理过程是IO和计算混合的所以我们需要动态线程池， 能够在线上运行服务的同时灵活去调整配置进行调优

思路：把几个核心参数暴露出来，将线程池的参数从代码中迁移到分布式配置中心上， 实现线程池参数可动态配置和即时生效，根据线上线程池的监控， 需要时去调整核心参数

## 怎么理解线程安全

### 线程安全的本质

线程安全的核心是：在多线程并发访问共享资源（变量、对象、文件等） 时，程序的执行结果始终符合预期，且不会出现数据错乱或逻辑错误。其根源在于以下三个层面的问题：

- 原子性：操作是否不可分割。
- 可见性：线程对共享变量的修改是否对其他线程立即可见。
- 有序性：代码执行顺序是否可能被编译器和 CPU 重排序。

## 对 i++ 问题的深入分析

例如 简单的 i++， 它虽然只有一行代码，但它却并不是原子性的操作， i++ 被翻译为字节码后， 可以发现其实是有 四条字节码指令

**字节码分解（以 JVM 为例）**

```sql
// i++ 对应以下步骤：
getstatic i    // 读取静态变量  i 到操作数栈
iconst_1       // 将常量  1 压入操作数栈
iadd           // 栈顶两个值相加（ i+1）
putstatic i    // 将结果写回静态变量  i

```

那么多线程的情况下，每个线程分别执行自己的四条字节码指令，且多线程是抢占式得到CPU执行权

线程切换可能发生在任意字节码指令之间， 导致操作被 “切割 ”，即多个线程的多条字节码指令存在交叉执行。

即使某些操作看似单行代码（如 i++），也可能因底层非原子性引发线程安全问题。

```properties
i=0线程安全问题：

```

假设线程 A 和线程 B 同时执行 i++ （初始值）：

- 线程 A 读取 i=0， 线程 B 也读取 i=0。
- 线程 A 计算 i+1=1， 线程 B 计算 i+1=1。

2. c. 线程 A 写回 i=1， 线程 B 写回 i=1。
- 最终结果： i=1 （期望值为， 出现错误。

解决方案：使用synchronized或lock或原子类

## ThreadLocal

ThreadLocal 提供了一种线程级别的数据存储机制。每个线程都拥有自己独立的 ThreadLocal，意味着每个线程都可以独立地、安全地操作这些变量， 而不会影响其他线程。

### 使用场景/作用典型使用场景

- 用户身份信息存储：在请求的拦截器/过滤器中鉴权校验用户身份， 把用户信息(如用户ID、权限)存入 ThreadLocal 中，在请求的后续链路中如果需要获取用户信息的， 直接在

ThreadLocal 中获取即可

- 线程安全：ThreadLocal 可以用来存储一些需要并发安全处理的成员变量， 比如

SimpleDateFormat， 由于 SimpleDateFormat 不是线程安全的， 可以使用 ThreadLocal 为每个线程创建一个独立的 SimpleDateFormat实例，从而避免线程安全问题

- 日志上下文存储：在常见的日志框架中， 经常使用 ThreadLocal 来存储与当前线程相关的日志上下文。这允许开发者在打印日志消息时包含特定于线程的信息， 如用户ID， 这对于调试和监控是非常有用的（相当于为了打印每条日志时能看到用户ID或其他信息）
- traceld 存储：和上面存储日志上下文类似，在分布式链路追踪中， 需要存储本次请求的traceld， 通常也都是基于 ThreadLocal 存储的
- 数据库 Session：很多ORM框架， 如Hibernate、Mybatis，都是使用 ThreadLocal 来存储和管理数据库会话的这样可以确保每个线程都有自己的会话实例， 避免了在多线程环境中出现的线程安全问题

**主要的两个作用：**

1. 在线程中传递数据，在同一个线程执行过程中，ThreadLocal 的数据一直在，所以可以在前面把数据放到 ThreadLocal 中，在后面需要时再取出来用，就可以避免数据通过参数在多层方法传递
2. 解决并发问题

### 实现原理

1. Thread 类对象中 维护了 ThreadLocalMap 成员变量
2. ThreadLocalMap 类对象中 维护了 Entry 数组， Entry数组中的每一个元素都是一个Entry对象
- 每个Entry对象中存储着 一个ThreadLocal对象与其要存入的数据value值
- 每个Entry对象在Entry数组中的位置是通过ThreadLocal对象的threadLocalHash Code计算出来的， 以此来快速定位Entry对象在Entry数组中的位置

3. 所以，在Thread中， 可以存储多个ThreadLocal对象
![实现原理](file:///D:/Java/data/八股文/02-JUC并发/b8b07eb9dc0b.png)

ThreadLocal 的 set 方法实现：获取当前线程， 获取当前线程的ThreadLocalMap，调用其set方法，存入的 key 是this(即ThreadLocal对象本身)，value是要存入的数据

![实现原理](file:///D:/Java/data/八股文/02-JUC并发/d867472839ff.png)

ThreadLocal 的 get 方法实现：获取当前线程， 获取当前线程的ThreadLocalMap，调用其get方法， 通过this(即ThreadLocal对象本身) 获取到之前存入的数据

![实现原理](file:///D:/Java/data/八股文/02-JUC并发/19135eef88b1.png)

### 内存泄漏

> 注：内存泄漏指：存在无法回收的对象

假设我们单独开启一个线程， 并且将数据存储到ThreadLocal中， 当 Thread 线程执行任务结束退出时， 线程对象被销毁，那么Thread 线程与 ThreadLocalMap 实例对象之间的引用关系就不存在，在 GC 时 ThreadLocalMap 对象、ThreadLocal 对象、之前存储的数据 都会被回收掉，所以其实不存在内存泄漏

![内存泄漏](file:///D:/Java/data/八股文/02-JUC并发/e836cd009513.png)

但是如果使用线程池的方式，核心线程是会反复使用的， 线程中对应的 ThreadLocalMap 会被线程 强引用

所以 ThreadLocalMap 不能被 GC 自动回收，而 ThreadLocalMap 中包含一个 Entry 数组

> 注：Entry 数组中含有多个< Key 为 ThreadLocal， value为存储的数据 > 的Entry对象

虽然 Entry 对象中的 Key 是弱引用，能够被 GC 自动回收

但 value 是强引用，不能被 GC 自动回收，所以，在线程池中使用ThreadLocal会存在内存泄露的风险

![内存泄漏](file:///D:/Java/data/八股文/02-JUC并发/99b652fb8150.png)

**ThreadLocal---ThreadLocalMap**

```java
public class ThreadLocal<T>{
    static class ThreadLocalMap {
        static class Entry extends WeakReference<ThreadLocal<?>> {
            /** The value associated with this ThreadLocal. */
            Object value;
            -             Entry(ThreadLocal<?> k, Object v) {
                super(k);
                value = v;
            }
        }
    }
}

```

强引用: Java中默认的引用类型， 一个对象如果具有强引用那么只要这种引用还存在就不会被回收。比如String str = new String("Hello ThreadLocal"); 其中 str 就是一个强引用， 当然， 一旦强引用出了其作用域，那么强引用随着方法弹出线程栈，那么它所指向的对象将在合适的时机被JVM垃圾收集器回收

软引用： 如果一个对象具有软引用，在JVM发生内存溢出之前 (即内存充足够使用)， 是不会GC这个对象的；只有到JVM内存不足的时候才会调用垃圾回收期回收掉这个对象。软引用和一个引用队列联合使用， 如果软引用所引用的对象被回收之后，该引用就会加入到与之关联的引用队列中

弱引用： 这里讨论ThreadLocalMap中的Entry类的重点， 如果一个对象只具有弱引用，那么这个对象就会被垃圾回收器回收掉 (被弱引用所引用的对象只能生存到下一次GC之前， 当发生GC时候， 无论当前内存是否足够弱引用所引用的对象都会被回收掉)。弱引用也是和一个引用队列联合使用， 如果弱引用的对象被垃圾回收期回收掉，JVM会将这个引用加入到与之关联的引用队列

中。弱引用的对象可以通过弱引用的get方法得到， 当引用的对象被回收掉之后， 再调用get方法就会返回null

虚引用： 虚引用是所有引用中最弱的一种引用， 其存在就是为了将关联虚引用的对象在被GC掉之后收到一个通知

**如何避免内存泄漏（解决方案）**

在使用完ThreadLocal对象中保存的数据后， 一般在拦截器过滤器的后置处理中，在 finally{} 代码块中调用 ThreadLocal 的 remove() 方法

![内存泄漏](file:///D:/Java/data/八股文/02-JUC并发/4792952d72ce.png)

## Synchronized

**背景知识**

- 每个Java对象头部都有一个MarkWord，存储着对象的运行时数据， 如哈希码、锁状态信息、 GC分代年龄等，锁状态信息标志了Synchronized的状态

### Synchronized 的原理

Java的同步机制是分层抽象的。

1. 在语言层面，synchronized 是一个关键字
2. 在JVM字节码层面，synchronized 对应的是 monitorenter 和 monitorexit 两条字节码指令，表示进入临界区， 告诉JVM在此处需要加锁和解锁。
3. 在JVM逻辑层面，JVM内部通过 Monitor（监视器）来管理线程的竞争和等待
- 每个锁对象都关联一个Monitor， 内部通过三个逻辑区域管理线程竞争
  - Owner： 当前持有锁的线程
  - EntryList：等待锁的阻塞线程队列
  - WaitSet：调用 obj.wait() 后进入等待状态的线程队列 // 这行可以不说
- 具体流程：
  - 当线程执行 monitorenter 时，JVM会检查 锁对象 的Monitor
    - 若 Owner 为空， 线程成为 Owner
    - 若 Owner 被占用， 线程进入 EntryList 阻塞
  - 当线程执行 monitorexit 时，JVM释放锁， 并唤醒 EntryList 中的线程，让它们去竞争锁
  - 调用 obj.wait() 的线程会释放锁并进入 WaitSet， 等待 obj.notify() 唤醒 // 这行可以不说

4. 在操作系统层面， 需要从用户态切换到内核态， 向操作系统底层申请互斥量mutex，性能开销很大， 因此称其为重量级锁。

### 锁升级过程

synchronized 由于涉及到操作系统层面申请互斥量mutex， 还涉及到线程的阻塞和唤醒都需要从用户态切换到内核态，性能开销很大， 因此称其为重量级锁

在JDK1.6 考虑不同竞争强度的场景 对synchronized进行了优化无锁->偏向锁->轻量级锁(自旋锁)->重量级锁

无锁->偏向锁

最初是无锁的状态， 当一个synchronized代码块被线程首次进入时，JVM会将锁标记为偏向锁，

且会在锁对象头中记录下该线程的ID。如果该线程再次请求同一把锁（即重入锁）， 通过比较线程ID它会直接获得锁， 是为了没有锁竞争且需要重入的场景而引入的。

偏向锁->轻量级锁

如果有其他线程来请求获取锁，此时偏向锁就会被撤销，两个线程会通过CAS的方式自旋尝试获取锁， 获取锁后JVM会将锁标记为轻量级锁。获取锁的流程：

1. 将锁对象头中的Mark Word复制到线程栈中的锁记录结构中。
2. 尝试通过CAS操作将锁对象头的Mark Word的内容更新为指向锁记录的指针。如果这个更新操作成功，那么这个线程就成功获取了这个对象的轻量级锁。
轻量级锁->重量级锁

当有较多线程短时间内请求获取锁， 意味着当前竞争比较激烈， 而轻量级锁使用的CAS的方式会占用CPU， 因此此时会发生锁膨胀，JVM将锁标记为重量级锁， 重量级锁中竞争失败的锁会陷入阻塞，不会占用CPU， 而重量级锁的原理：（请看上方Synchronized的原理）

总结：锁升级的过程/设计思路 其实是为了适配不同竞争强度下的场景

Lock 是接口， ReentrantLock 是其实现类，底层实现是AQS。

## AQS

AQS是阻塞式锁和相关的同步器工具的框架。AQS主要由两部分组成，分别是 state属性 和 FIFO的等待队列(双向链表)。

- 用 state 属性来表示共享资源的状态（分为独占模式和共享模式），不同的子类实现中对于state的值有不同的涵义
  - 独占模式是只有一个线程能够访问资源， 而共享模式可以允许多个线程同时访问资源。
  - 使用CAS机制更新state属性 : 保证对于state值的修改的线程安全
- FIFO的等待队列(双向链表)：用于存储等待获取锁的线程， 因为有些线程可以抢占到锁， 而有些线程无法抢占到锁，此时，没有竞争到锁的线程就会被打包为一个Node节点，按照顺序组成一个双向链表。当释放锁时，会唤醒双向链表中的第一个Node节点。

独占模式：只有一个线程能够访问资源。例 ReentrantLock 就是独占模式的实现共享模式：允许多个线程同时访问资源。例 CountDownLatch 就是共享模式的实现

在不同的子类实现中， state 的含义可能不同：

- 在 ReentrantLock 中：
  - state = 0：表示当前资源没有被加锁。
  - state = 1：表示当前资源已经被加锁。
  - state > 1：表示当前资源已经被加了多把锁（可重入锁）。
- 在 CountDownLatch 中：
  - state 表示剩余的计数。

## ReentrantLock

ReentrantLock 是 Java 并发包（java.util.concurrent.locks） 中的一个类。

ReentrantLock 提供了比 synchronized 关键字更灵活的锁机制， 支持 公平锁 和 非公平锁， 并且可以 中断、超时 等高级特性。

ReentrantLock 和 Synchronized 的比较

|  | ReentrantLock | Synchronized |
| --- | --- | --- |
| 特性 | JDK提供的一个类 | Java内置关键字 |
| 实现层面 | 在JDK代码层面实现 | 在JVM层面(操作系统)层面实现 |
| 用法区别 | lock()和unlock()加锁解锁，非常灵活 | 一般修饰在方法/代码块上 |
| 公平锁 | 提供了公平锁和非公平锁 | 是非公平锁，不支持公平锁 |
| 可重入性 | 可重入 | 可重入 |
| 使用场景 | 适合复杂场景 | 适合简单场景 |

### ReentrantLock 如何实现公平锁和非公平锁

**首先解释公平和非公平的概念：**

- 公平：竞争锁资源的线程 严格 按照请求的顺序来分配锁
- 非公平：竞争锁资源的线程 允许 插队来尝试抢占锁资源

ReentrantLock 默认是非公平锁

底层AQS的实现 当线程没有抢占到锁时，会将其打包为Node节点加入到 FIFO 的双向链表在上述背景的情况下：

- 公平锁的实现： 当线程在竞争锁资源时，会判断双向链表中是否有线程在等待， 如果有就加入到链表的尾部进行等待。
- 非公平的实现： 当线程在竞争锁资源时，不管双向链表中是否有线程在等待，都会去尝试抢占

锁资源， 如果抢占不到， 再加入双向链表。

公平和非公平其实是相对于在双向链表中等待的线程而言的。

## CAS

CAS 原理

Compare And Swap（比较再交换）：在更新前检查数据是否被修改，若未被修改则更新， 否则自旋重试

**具体解释：**

主存中有一个共享变量， 当线程想要去修改这个变量的值的时候， 需要先把这个变量的值拷贝到线程的工作内存中，然后进行计算操作，得到一个新的值。然后线程带着旧值和新值再次找到主存中的共享变量。

先比较旧值和现在主存中的共享变量是否相同。

- 若相同，说明在这期间没有其他线程修改过主存中的共享变量， 是线程安全的。因此把新值写入主存的共享变量中。
- 若不同，说明在这期间有其他线程修改过主存中的共享变量，不是线程安全的。因此此时需要自旋重试
  - 自旋：再次取得主存中共享变量的值。回到线程的工作内存进行计算操作得到新值。再次比较旧值和主存中的共享变量的值是否相同。又回到刚刚的逻辑。直至自旋成功。

CAS 的应用场景

- AQS中大量使用到CAS来实现基本操作。
- JUC包下的原子类中（例如Atomic Integer） 大量使用到CAS + volatile来保证线程安全。

CAS 的优劣点

优点：不加锁， 无锁并发保存线程安全。

缺点： 自旋占用CPU。

## 乐观锁与悲观锁

### 定义和区别

乐观锁：持乐观态度，认为并发冲突的概率较低，在提交时检查数据是否被修改，若未被修改则提交， 否则重试或抛出异常。

- 例如 版本号法、CAS（compare and swap）， 即乐观锁实现
- 应用场景：
  - 适合读多写少(并发冲突的概率低)， 可以降低锁定带来的性能开销
  - 系统能够容忍或者处理 失败的情况， 因为乐观锁可能会因为并发冲突导致执行失败。
  - 并发性能高

悲观锁：持悲观态度，认为并发冲突的概率高，每次操作数据时都加锁，确保线程安全。

- 例如 synchronized， 即悲观锁实现
- 应用场景：
  - 适合写多读少(并发冲突的概率高)， 避免频繁冲突导致的多次重试
  - 数据一致性要求极高， 如金融系统
  - 并发性能低（串行化操作）

### 如何实现乐观锁版本号机制：

- 为数据添加版本号字段（如 version）。
- 更新时检查版本号是否匹配， 匹配则更新并递增版本号。

```sql
- 在执行更新之前，先查询目标记录的版本号
SELECT value, version FROM table WHERE id = 1; 3
- 执行更新时，检查目前的版本号和之前查到的版本号是否一致
UPDATE table SET value = new_value, version = version + 1
WHERE id = 1 AND version = current_version;

```

## JMM

### 背景知识

MESI 协议（Modified Exclusive Shared Or Invalid） 是各处理器访问缓存时都遵循的一致性协议，保证了每个缓存中使用的共享变量的副本是一致的。核心思想是：

- 当CPU写数据时， 如果发现操作的变量是共享变量， 即在其他CPU中也存在该变量的副本，会发出信号通知其他CPU将该变量的缓存行置为无效状态， 因此当其他CPU需要读取这个变量时，发现自己缓存中缓存该变量的缓存行是无效的，那么它就会从内存重新读取。

### 定义

多线程程序中由于多线程通过共享内存进行通信时可能出现的原子性、可见性、有序性问题JMM（Java Memory Model Java内存模型） 是一套规范/规则。

目的就是在多线程读写共享数据时，保证可见性、有序性和原子性。

### 核心概念

在Java内存模型中，存在 主内存 和 工作内存 的概念。

- 主内存是线程共享的内存区域， 其中存储了所有的共享变量。所有线程都可以访问主内存中的共享变量。主内存是多个线程之间进行数据通信的桥梁。
- 工作内存是每个线程独占的内存区域。每个线程都有自己的工作内存，用于存储它的局部变量、操作结果以及对主内存中的共享变量的拷贝副本。

工作模式：线程对共享变量的操作不直接在主内存中进行， 而是首先将共享变量从主内存中拷贝到自己的工作内存中，然后对工作内存中的副本进行操作，在操作完成后再将最新值刷新回主内存。

另外 JMM 提供了一系列和并发处理相关的关键字， 如 volatile、synchronized， 这些就是Java内存模型封装了底层的实现后提供给我们使用的关键字。

### 原子性

原子性的问题是：例如多线程情况下的i++， 如果不加控制由于不是原子性的都会发生线程安全问题

**请看《怎么理解线程安全》对 i++的分析解决方案：使用synchronized关键字**

### 可见性

可见性的问题是： 对于共享变量，A线程可能感知不到B线程对于共享变量的修改，A线程拿到的还是旧值

可见性问题出现的可能原因有两个

- B线程修改变量时， 只把新值更新到工作内存的缓存里， 并没有马上把主内存中的共享变量的值更新
- A线程把共享变量的值存放到线程工作内存的高速缓存中，在读取时直接从高速缓存中获取，而不从主存中获取
- 这是为了提升效率，但是却造成了线程无法感知其他线程修改了共享变量的值的情况。

解决方案：volatile 关键字可以保证可见性

当一个共享变量被volatile修饰时， 它会保证线程对于共享变量修改的值立即被其他线程可见

**原理：**

当对volatile修饰的变量进行写操作的时候，

- JVM会向处理器发送一条lock前缀的指令， 它会锁定当前内存区域的缓存， 并且立即将当前缓存行数据写回主内存。
- 并且在写回主内存时， 通过MESI缓存一致性协议使得其他线程对于该共享变量的缓存失效，其他线程发现缓存失效， 需要重新去主内存中重新读取数据。

所以 volatile 可以保证可见性。

### 有序性

有序性的问题是： 虚拟机在进行代码编译时，对改变顺序后不会对最终结果造成影响的代码，虚拟机不一定会按我们写的代码顺序运行，有可能进行重排序。实际上重排序后在多线程下有可能会造成线程安全问题。（例如单例模式中的懒汉式的双重检查锁实现， 如果不加volatile则有可能因为重排序导致出现未初始化的对象被外界使用的情况）

解决方案：volatile 关键字可以保证有序性

当一个共享变量被volatile修饰时，对于该变量的操作禁止指令重排序

**原理：**

volatile 是通过插入内存屏障（一个CPU指令），在内存屏障前后自动禁止重排序优化， 以此实现有序性。

(单纯扩展，不需要这么底层)

编译器在生成字节码时，会在指令序列中插入内存屏障来禁止特定类型的处理器重排

- 在每个volatile写操作的前面插入一个StoreStore屏障
- 在每个volatile写操作的后面插入一个StoreLoad屏障
- 在每个volatile读操作的后面插入一个LoadLoad屏障
- 在每个volatile读操作的后面插入一个LoadStore屏障

## 多线程交替打印 1-100

2个线程交替打印0-100 Java

```java
public class Main {
    private static final Object LOCK = new Object();
    private static volatile int count = 0;
    private static final int MAX = 100;
    public static void main(String [] args) {
        Thread thread = new Thread(new Seq(0));
        Thread thread1 = new Thread(new Seq(1));
        thread.start();
        thread1.start();
        static class Seq implements Runnable {
            private final int index;
            public Seq(int index) {
                this.index = index;
            }
            @Override
            public void run() {
                // Run方法只要执行结束了 ,线程就结束了
                while (count < MAX) {
                    // 同步代码块 ,一个时刻只能有一个线程获取到锁
                    synchronized (LOCK) {
                        // 获取到锁就进来判断， 当前是否轮到该线程打印
                        while (count % 2 != index) {
                            // 不是当前线程打印 ,那么就让当前线程去wait,它会自动释放锁 ,所以其他线程可以进来
                            try {
                                LOCK.wait();
                                // 当线程被唤醒时，会尝试重新进入synchronized代码块
                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                            // 是当前线程打印 , 但count>MAX
                            if (count > MAX) {
                                LOCK.notifyAll();
                                return;
                            }
                            System.out.println("Thread-" + index + ":" + count);
                            count++;
                            LOCK.notifyAll();
                        }
                    }
                }
            }
        }
        public class Main {
            private static final Object LOCK = new Object();
            private static volatile int count = 0;
            private static final int MAX = 100;
            public static void main(String [] args) {
                Thread thread = new Thread(new Seq(0));
                Thread thread1 = new Thread(new Seq(1));
                Thread thread2 = new Thread(new Seq(2));
                thread.start();
                thread1.start();
                thread2.start();
                static class Seq implements Runnable {
                    private final int index;
                    public Seq(int index) {
                        this.index = index;
                    }
                    @Override
                    public void run() {
                        // Run方法只要执行结束了 ,线程就结束了
                        while (count < MAX) {
                            // 同步代码块 ,一个时刻只能有一个线程获取到锁
                            synchronized (LOCK) {
                                // 获取到锁就进来判断， 当前是否轮到该线程打印
                                while (count % 3 != index) {
                                    // 不是当前线程打印 ,那么就让当前线程去wait,它会自动释放锁 ,所以其他线程可以进来
                                    try {
                                        LOCK.wait();
                                        // 当线程被唤醒时，会尝试重新进入synchronized代码块
                                    } catch (Exception e) {
                                        e.printStackTrace();
                                    }
                                    // 是当前线程打印 , 但count>MAX
                                    if (count > MAX) {
                                        LOCK.notifyAll();
                                        return;
                                    }
                                    System.out.println("Thread-" + index + ":" + count);
                                    count++;LOCK.notifyAll();}}}}}

```

## 多线程交替打印 ABC

```java
import java.util.concurrent.Semaphore;
// 多线程打印ABC
public class Printer {
    private final Semaphore semA = new Semaphore(1); // 信号量A设置为1,从A开始打印
    private final Semaphore semB = new Semaphore(0);
    private final Semaphore semC = new Semaphore(0);
    private static int n = 3;   // 打印轮次
    public static void main(String [] args) {
        Printer printer = new Printer();
        new Thread(()->printer.print( 'A',printer.semA,printer.semB)).start ();
        new Thread(()->printer.print( 'B',printer.semB,printer.semC)).start ();
        new Thread(()->printer.print( 'C',printer.semC,printer.semA)).start ();
    }
    public void print(char ch, Semaphore current, Semaphore next) {
        try {
            for (int i = 0; i < n; i++) {
                current.acquire();  // 获取当前信号量
                System.out.println(Thread.currentThread().getName() + ": " + ch);
                next.release();     // 释放下一个信号量
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}

```

## 多线程的上下文切换

### 多线程的上下文切换 · 定义

上下文切换是指 CPU 从一个线程转到另一个线程时， 需要保存当前线程的上下文状态，恢复另一个线程的上下文状态， 以便于下一次恢复执行该线程时能够正确地运行。

在多线程编程中，上下文切换是一种常见的操作，上下文切换通常是指在一个CPU 上， 由于多个线程共享 CPU时间片， 当一个线程的时间片用完后， 需要切换到另一个线程运行。此时需要保存当前线程的状态信息， 包括程序计数器、寄存器、栈指针等， 以便下次继续执行该线程时能够恢复到正确的执行状态。同时， 需要将切换到的线程的状态信息恢复， 以便于该线程能够正确运行。

在多线程中，上下文切换的开销比直接用单线程大， 因为在多线程中， 需要保存和恢复更多的上下文信息。过多的上下文切换会降低系统的运行效率， 因此需要尽可能减少上下文切换的次数。

### 什么时候会发生上下文切换

**多线程的上下文切换通常由以下情况触发：**

1. 时间片耗尽：操作系统为每个线程分配固定的CPU时间片 （如10ms）， 当时间片用完后， 强制切换至其他就绪线程。
2. 线程主动阻塞：例如线程等待I/O操作（如文件读写）、获取锁失败
（如 synchronized 或 ReentrantLock）、调用 sleep() 或 wait() 方法。线程主动让出CPU，触发调度器执行其他线程。

3. 高优先级线程抢占：操作系统支持抢占式调度， 且更高优先级线程进入就绪状态。当前线程被中断，CPU立即执行高优先级任务。
4. 线程主动让出：例如Java中 Thread.yield() 可能让当前线程回到就绪队列， 允许其他线程运行。
5. 中断处理：硬件事件（如磁盘I/O完成、网络数据到达） 引发中断，CPU暂停当前线程，执行中断服务程序（ISR）。
6. 线程终止： 线程执行完毕或异常退出时，释放CPU资源，调度器选择新线程运行。

### 如何减少上下文切换

1. 减少线程数：可以通过合理的线程池管理来减少线程的创建和销毁， 线程数不是越多越好，合理的线程数可以避免线程过多导致频繁的上下文切换
2. 使用无锁并发编程：无锁并发编程可以避免线程因等待锁而进入阻塞状态，从而减少上下文切换的发生
3. 使用CAS算法：CAS算法可以避免线程的阻塞和唤醒操作，从而减少上下文切换
4. 使用虚拟线程（协程）：协程是一种用户态线程， 其切换不需要操作系统的参与， 因此可以避免上下文切换。(避免的是操作系统级别的上下文切换，但是仍然需要在JVM层面做一些保存和恢复线程的状态，但是也成本低得多)
5. 合理地使用锁：在使用锁的过程中， 需要避免过多地使用同步块或同步方法，尽量缩小同步块或同步方法的范围，从而减少线程的等待时间， 避免上下文切换的发生

## 原子类

Java 原子类是 java.util.concurrent.atomic 包下的一组工具类

（如 AtomicInteger、 AtomicLong、 AtomicReference 等）， 通过 无锁编程和 CAS机制实现线程安全的无锁的变量操作。

提供了十几个原子类，分为4种类型，分别是：

- 原子更新基本类型
- 原子更新数组
- 原子更新引用
- 原子更新属性

### 原理

**为什么原子类的操作是原子性的？**

原子类的核心是 CAS（Compare-And-Swap） 操作， 直接依赖 CPU的原子指令（如x86的 CM PXCHG 指令）。原子类基本都是使用 Unsafe 实现的包装类。 从原理上来说就是：

1. Atomic 包的类的实现大多数都是调用的 unsafe 方法
2. 而 unsafe 底层实际上是调用C代码，C代码调用汇编
3. 最后生成出一条 CPU 的原子指令 cmpxchg， 直接操作内存完成操作，CPU的原子指令是原子性的
**原子类里的代码**

```java
public final int incrementAndGet() {
    // Unsafe类的getAndAddInt()内部通过循环CAS实现
    return unsafe.getAndAddInt(this, valueOffset, 1) + 1;
}

```

CAS原理： 当需要修改一个共享变量时，CAS会检查当前值是否与预期值一致。如果一致，则更新为新值；否则， 操作失败（需重试）。

```c
// 伪代码描述CAS操作
boolean compareAndSwap(int* address, int expectedValue, int newValue) {
if (*address == expectedValue) {
*address = newValue;
return true;
}
return false;
}

```

### 使用场景

什么时候使用原子类？ 当我们只是需要一个简单的、高效、线程安全的递增或者递减方案：简单：操作简单，底层实现简单

高效： 占用资源少， 操作速度快

安全：在高并发和多线程环境下要保证数据的正确性

例如：计数器或统计

**例如统计请求次数、在线用户数：**

```java
AtomicInteger requestCount = new AtomicInteger(0);
requestCount.incrementAndGet();

```

当然也可以使用synchronized或lock实现，但这个场景下原子类更合适

- 原子类是基于CAS（无锁） 的，仅适用于简单变量的原子操作、代码更简洁

## Unsafe

Unsafe 是 CAS 的核心类。因为 Java 无法直接访问底层操作系统， 而是通过本地 (native) 方法来访问。不过尽管如此，JVM 还是开了一个后门，JDK 中有一个类 Unsafe， 它提供了硬件级别的原子操作。

Unsafe 是 Java 中一个底层类， 包含了很多基础的操作， 比如数组操作、对象操作、内存操作、 CAS操作、线程 (park) 操作、栅栏 (Fence) 操作，JUC包、一些三方框架都使用 Unsafe 类来保证并发安全。

Unsafe 类在 JDK 源码的多个类中用到， 这个类的提供了一些 绕开 JVM 的、更底层的功能， 基于它的实现可以提高效率。但是， 它是一把双刃剑：正如它的名字所预示的那样， 它是 Unsafe的， 它所分配的内存需要手动 free (不被 GC 回收)。

Unsafe 类提供了硬件级别的原子操作， 主要提供了以下功能：

1. 通过 Unsafe 类可以分配内存， 可以释放内存
2. 可以定位对象某字段的内存位置，也可以修改对象的字段值， 即使它是私有的
3. 将线程进行挂起与恢复
4. CAS操作
**背景知识：**

---

> 📎 **相关笔记**：[[八股文/01-JavaSE基础与集合|JavaSE]] · [[JUC/JUC 索引|JUC]] · [[八股文/03-JVM|JVM]]
