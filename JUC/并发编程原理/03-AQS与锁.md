---
aliases:
  - AQS
  - ReentrantLock
  - 读写锁
  - Semaphore
---

# AQS 与锁

> 来源：JUC/并发编程_原理.docx（只读原文）。本篇包括：AQS 原理、ReentrantLock 原理、读写锁原理、Semaphore 原理。
>
> 入口：[[JUC/JUC 索引|JUC 索引]]
>
> 前置：[[JUC/并发编程原理/02-synchronized与等待通知|synchronized 与等待通知]]；后续：[[JUC/并发编程原理/04-并发容器|并发容器]]。

## AQS 原理

### 1. 概述

全称是 AbstractQueuedSynchronizer，是阻塞式锁和相关的同步器工具的框架特点：

- 用 state 属性来表示资源的状态（分独占模式和共享模式），子类需要定义如何维护这个状态，控制如何获取锁和释放锁
- getState - 获取 state 状态
- setState - 设置 state 状态
- compareAndSetState - cas 机制设置 state 状态
- 独占模式是只有一个线程能够访问资源，而共享模式可以允许多个线程访问资源
- 提供了基于 FIFO 的等待队列，类似于 Monitor 的 EntryList
- 条件变量来实现等待、唤醒机制，支持多个条件变量，类似于 Monitor 的 WaitSet

子类主要实现这样一些方法（默认抛出 UnsupportedOperationException）

- tryAcquire
- tryRelease
- tryAcquireShared
- tryReleaseShared
- isHeldExclusively

获取锁的姿势

```java
// 如果获取锁失败
if (!tryAcquire(arg)) {
    // 入队 , 可以选择阻塞当前线程    park unpark }
```

释放锁的姿势

```java
// 如果释放锁成功
if (tryRelease(arg)) {
    // 让阻塞线程恢复运行 }
```

### 2. 实现不可重入锁

#### 自定义同步器

```java
final class MySync extends AbstractQueuedSynchronizer { @Override
    protected boolean tryAcquire(int acquires) { if (acquires == 1){
            if (compareAndSetState(0, 1)) {
                setExclusiveOwnerThread(Thread.currentThread()); return true;
            }
        }
        return false; }

    @Override
    protected boolean tryRelease(int acquires) { if(acquires == 1) {
            if(getState() == 0) {
                throw new IllegalMonitorStateException(); }
            setExclusiveOwnerThread(null);
            setState(0);
            return true; }
        return false; }

    protected Condition newCondition() {
        return new ConditionObject();
    }

    @Override
    protected boolean isHeldExclusively() { return getState() == 1;

    } }
```

#### 自定义锁

有了自定义同步器，很容易复用 AQS，实现一个功能完备的自定义锁

```java
class MyLock implements Lock {

    static MySync sync = new MySync();

    @Override
    // 尝试，不成功，进入等待队列
    public void lock() { sync.acquire(1);
    }

    @Override
    // 尝试，不成功，进入等待队列，可打断
    public void lockInterruptibly() throws InterruptedException { sync.acquireInterruptibly(1);
    }

    @Override
    // 尝试一次，不成功返回，不进入队列
    public boolean tryLock() {
        return sync.tryAcquire(1);
    }

    @Override
    // 尝试，不成功，进入等待队列，有时限
    public boolean tryLock(long time, TimeUnit unit) throws InterruptedException { return sync.tryAcquireNanos(1, unit.toNanos(time));
    }

    @Override
    // 释放锁
    public void unlock() { sync.release(1);
    }

    @Override
    // 生成条件变量
    public Condition newCondition() { return sync.newCondition();
    }
}
```

测试一下

```java
MyLock lock = new MyLock();
```

```java
new Thread(() -> { lock.lock();  try {
        log.debug("locking..."); sleep(1);
    } finally {
        log.debug("unlocking..."); lock.unlock();
    }
},"t1").start();

new Thread(() -> { lock.lock();  try {
        log.debug("locking..."); } finally {
        log.debug("unlocking..."); lock.unlock();
    }
},"t2").start();
```

输出

```text
22:29:28.727 c.TestAqs
[t1] - locking...
22:29:29.732 c.TestAqs
[t1] - unlocking...
22:29:29.732 c.TestAqs
[t2] - locking...
22:29:29.732 c.TestAqs
[t2] - unlocking...
```

不可重入测试

如果改为下面代码，会发现自己也会被挡住（只会打印一次 locking）

```java
lock.lock();
log.debug("locking..."); lock.lock();
log.debug("locking...");
```

### 3. 心得

#### 起源

早期程序员会自己通过一种同步器去实现另一种相近的同步器，例如用可重入锁去实现信号量，或反之。这显然不够优雅，于是在 JSR166（java 规范提案）中创建了AQS，提供了这种通用的同步器机制。

#### 目标

AQS 要实现的功能目标

- 阻塞版本获取锁 acquire 和非阻塞的版本尝试获取锁tryAcquire
- 获取锁超时机制
- 通过打断取消机制
- 独占机制及共享机制
- 条件不满足时的等待机制要实现的性能目标

Instead, the primary performance goal here is scalability: to predictably maintain efficiency even, or especially, when synchronizers are contended.

#### 设计

AQS 的基本思想其实很简单获取锁的逻辑

```java
while(state 状态不允许获取) { if(队列中还没有此线程) {
        入队并阻塞 }
}
当前线程出队
```

释放锁的逻辑

```java
if(state 状态允许了) {恢复阻塞的线程 (s)
}
```

要点

- 原子维护 state 状态
- 阻塞及恢复线程
- 维护队列

##### 1) state 设计

- state 使用 volatile 配合 cas 保证其修改时的原子性
- state 使用了 32bit int 来维护同步状态，因为当时使用 long 在很多平台下测试的结果并不理想

##### 2) 阻塞恢复设计

早期的控制线程暂停和恢复的 api 有 suspend 和 resume，但它们是不可用的，因为如果先调用的 resume那么 suspend 将感知不到

- 解决方法是使用 park & unpark 来实现线程的暂停和恢复，具体原理在之前讲过了，先 unpark 再 park 也没问题
- park & unpark 是针对线程的，而不是针对同步器的，因此控制粒度更为精细 . park 线程还可以通过 interrupt 打断

##### 3) 队列设计

- 使用了 FIFO 先入先出队列，并不支持优先级队列
- 设计时借鉴了 CLH 队列，它是一种单向无锁队列

队列中有 head 和 tail 两个指针节点，都用 volatile 修饰配合 cas 使用，每个节点有 state 维护节点状态入队伪代码，只需要考虑 tail 赋值的原子性

```java
do {
    // 原来的  tail
    Node prev = tail;
    // 用  cas 在原来  tail 的基础上改为  node } while(tail.compareAndSet(prev, node))
```

出队伪代码

```java
// prev 是上一个节点
while((Node prev=node.prev).state != 唤醒状态) { }
// 设置头节点
head = node;
```

CLH 好处：

- 无锁，使用自旋
- 快速，无阻塞

AQS 在一些方面改进了 CLH

```java
private Node enq(final Node node) { for (;;) {
        Node t = tail;
        // 队列中还没有元素  tail 为  null
        if (t == null) {
            // 将  head 从  null -> dummy
            if (compareAndSetHead(new Node()))
            tail = head; } else {
            // 将  node 的  prev 设置为原来的  tail
            node.prev = t;
            // 将  tail 从原来的  tail 设置为  node
            if (compareAndSetTail(t, node)) {
                // 原来  tail 的  next 设置为  node
                t.next = node;
                return t; }
        }
    }
}
```

##### 主要用到 AQS 的并发工具类

![原文图片：主要用到 AQS 的并发工具类](file:///D:/Java/data/JUC/03-AQS与锁/image-021.jpeg)

## ReentrantLock 原理

![原文图片：ReentrantLock 原理](file:///D:/Java/data/JUC/03-AQS与锁/image-022.jpeg)

### 1. 非公平锁实现原理

#### 加锁解锁流程

先从构造器开始看，默认为非公平锁实现

```java
public ReentrantLock() {
    sync = new NonfairSync();
}
```

NonfairSync 继承自 AQS没有竞争时

![原文图片：NonfairSync 继承自 AQS没有竞争时](file:///D:/Java/data/JUC/03-AQS与锁/image-023.jpeg)

第一个竞争出现时

![原文图片：第一个竞争出现时](file:///D:/Java/data/JUC/03-AQS与锁/image-024.jpeg)

Thread-1 执行了

1. CAS 尝试将 state 由 0 改为 1，结果失败
2. 进入 tryAcquire 逻辑，这时 state 已经是1，结果仍然失败
3. 接下来进入 addWaiter 逻辑，构造 Node 队列

- 图中黄色三角表示该 Node 的 waitStatus 状态，其中 0 为默认正常状态
- Node 的创建是懒惰的
- 其中第一个 Node 称为 Dummy （哑元）或哨兵，用来占位，并不关联线程

![原文图片：其中第一个 Node 称为 Dummy （哑元）或哨兵，](file:///D:/Java/data/JUC/03-AQS与锁/image-025.jpeg)

当前线程进入 acquireQueued 逻辑

1. acquireQueued 会在一个死循环中不断尝试获得锁，失败后进入 park 阻塞
2. 如果自己是紧邻着 head （排第二位），那么再次 tryAcquire 尝试获取锁，当然这时 state 仍为 1，失败
3. 进入 shouldParkAfterFailedAcquire 逻辑，将前驱 node，即 head 的 waitStatus 改为 -1，这次返回 false

![原文图片：3. 进入 shouldParkAfterFailedA](file:///D:/Java/data/JUC/03-AQS与锁/image-026.jpeg)

4. shouldParkAfterFailedAcquire 执行完毕回到 acquireQueued，再次 tryAcquire 尝试获取锁，当然这时state 仍为 1，失败
5. 当再次进入 shouldParkAfterFailedAcquire 时，这时因为其前驱 node 的 waitStatus 已经是 -1，这次返回true
6. 进入 parkAndCheckInterrupt，Thread-1 park （灰色表示）

![原文图片：6. 进入 parkAndCheckInterrupt，](file:///D:/Java/data/JUC/03-AQS与锁/image-027.jpeg)

再次有多个线程经历上述过程竞争失败，变成这个样子

![原文图片：再次有多个线程经历上述过程竞争失败，变成这个样子](file:///D:/Java/data/JUC/03-AQS与锁/image-028.jpeg)

Thread-0 释放锁，进入 tryRelease 流程，如果成功

- 设置 exclusiveOwnerThread 为 null . state = 0

![原文图片：设置 exclusiveOwnerThread 为 nu](file:///D:/Java/data/JUC/03-AQS与锁/image-029.jpeg)

当前队列不为 null，并且 head 的 waitStatus = -1，进入 unparkSuccessor 流程

找到队列中离 head 最近的一个 Node（没取消的）， unpark 恢复其运行，本例中即为Thread-1回到 Thread-1 的 acquireQueued 流程

![原文图片：找到队列中离 head 最近的一个 Node（没取消的）](file:///D:/Java/data/JUC/03-AQS与锁/image-030.jpeg)

如果加锁成功（没有竞争），会设置

- exclusiveOwnerThread 为 Thread-1，state = 1
- head 指向刚刚Thread-1 所在的 Node，该 Node 清空 Thread
- 原本的 head 因为从链表断开，而可被垃圾回收

如果这时候有其它线程来竞争（非公平的体现），例如这时有 Thread-4 来了

![原文图片：如果这时候有其它线程来竞争（非公平的体现），例如这时有 ](file:///D:/Java/data/JUC/03-AQS与锁/image-031.jpeg)

如果不巧又被 Thread-4 占了先

- Thread-4 被设置为 exclusiveOwnerThread，state = 1
- Thread-1 再次进入 acquireQueued 流程，获取锁失败，重新进入 park 阻塞

#### 加锁源码

```java
// Sync 继承自  AQS
static final class NonfairSync extends Sync {
    private static final long serialVersionUID = 7316153563782823691L;

    // 加锁实现

    final void lock() {
        // 首先用  cas 尝试（仅尝试一次）将  state 从  0 改为  1, 如果成功表示获得了独占锁
        if (compareAndSetState(0, 1))
        setExclusiveOwnerThread(Thread.currentThread());
    else
        // 如果尝试失败，进入  H
        acquire(1); }
    // H  AQS 继承过来的方法 , 方便阅读 , 放在此处
    public final void acquire(int arg) {
        // 口  tryAcquire
        if (
        !tryAcquire(arg) &&
        // 当  tryAcquire 返回为  false 时 , 先调用  addWaiter 四 , 接着  acquireQueued 田
        acquireQueued(addWaiter(Node.EXCLUSIVE), arg) ) {
            selfInterrupt(); }
    }
    // 口  进入  白
    protected final boolean tryAcquire(int acquires) { return nonfairTryAcquire(acquires);
    }
    // 白  Sync 继承过来的方法 , 方便阅读 , 放在此处
    final boolean nonfairTryAcquire(int acquires) {
        final Thread current = Thread.currentThread(); int c = getState();
        // 如果还没有获得锁
        if (c == 0) {
            // 尝试用  cas 获得 , 这里体现了非公平性 : 不去检查  AQS 队列
            if (compareAndSetState(0, acquires)) { setExclusiveOwnerThread(current);
                return true; }
        }
        // 如果已经获得了锁 , 线程还是当前线程 , 表示发生了锁重入
    else if (current == getExclusiveOwnerThread()) {
            // state++
            int nextc = c + acquires;
            if (nextc < 0) // overflow
            throw new Error("Maximum lock count exceeded"); setState(nextc);
            return true; }
        // 获取失败 , 回到调用处
        return false; }
    // 四  AQS 继承过来的方法 , 方便阅读 , 放在此处
    private Node addWaiter(Node mode) {

        // 将当前线程关联到一个  Node 对象上 , 模式为独占模式
        Node node = new Node(Thread.currentThread(), mode);
        // 如果  tail 不为  null, cas 尝试将  Node 对象加入  AQS 队列尾部
        Node pred = tail;
        if (pred != null) {  node.prev = pred;
            if (compareAndSetTail(pred, node)) {
                // 双向链表
                pred.next = node;
                return node; }
        }
        // 尝试将  Node 加入  AQS, 进入  ㈥
        enq(node);
        return node; }
    // ㈥  AQS 继承过来的方法 , 方便阅读 , 放在此处
    private Node enq(final Node node) { for (;;) {
            Node t = tail;
            if (t == null) {
                // 还没有 , 设置  head 为哨兵节点（不对应线程，状态为  0 ）
                if (compareAndSetHead(new Node())) { tail = head;
                }
            } else {
                // cas 尝试将  Node 对象加入  AQS 队列尾部
                node.prev = t;
                if (compareAndSetTail(t, node)) { t.next = node;
                    return t; }
            }
        }
    }
    // ㈤  AQS 继承过来的方法 , 方便阅读 , 放在此处
    final boolean acquireQueued(final Node node, int arg) { boolean failed = true;
        try {
            boolean interrupted = false;
            for (;;) {
                final Node p = node.predecessor();
                // 上一个节点是  head, 表示轮到自己（当前线程对应的  node ）了 , 尝试获取
                if (p == head && tryAcquire(arg)) {
                    // 获取成功 , 设置自己（当前线程对应的  node）为  head
                    setHead(node);
                    // 上一个节点  help GC
                    p.next = null;
                    failed = false;
                    // 返回中断标记 false
                    return interrupted;

                }
                if (
                // 判断是否应当  park, 进入  ㈦
                shouldParkAfterFailedAcquire(p, node) &&
                // park 等待 , 此时  Node 的状态被置为  Node.SIGNAL ㈧
                parkAndCheckInterrupt() ) {
                    interrupted = true; }
            }
        } finally {
            if (failed)
            cancelAcquire(node); }
    }
    // ㈦  AQS 继承过来的方法 , 方便阅读 , 放在此处
    private static boolean shouldParkAfterFailedAcquire(Node pred, Node node) {
        // 获取上一个节点的状态
        int ws = pred.waitStatus;
        if (ws == Node.SIGNAL) {
            // 上一个节点都在阻塞 , 那么自己也阻塞好了
            return true;
        }
        // > 0 表示取消状态
        if (ws > 0) {
            // 上一个节点取消 , 那么重构删除前面所有取消的节点 , 返回到外层循环重试
            do {
                node.prev = pred = pred.prev; } while (pred.waitStatus > 0);
            pred.next = node; } else {
            // 这次还没有阻塞
            // 但下次如果重试不成功 , 则需要阻塞，这时需要设置上一个节点状态为  Node.SIGNAL
            compareAndSetWaitStatus(pred, ws, Node.SIGNAL); }
        return false; }
    // ㈧  阻塞当前线程
    private final boolean parkAndCheckInterrupt() { LockSupport.park(this);
        return Thread.interrupted(); }
}
```

##### 加锁源码 · 注意

- 是否需要 unpark 是由当前节点的前驱节点的 waitStatus == Node.SIGNAL 来决定，而不是本节点的waitStatus 决定

#### 解锁源码

```java
// Sync 继承自  AQS
static final class NonfairSync extends Sync {
    // 解锁实现
    public void unlock() { sync.release(1);
    }
    // AQS 继承过来的方法 , 方便阅读 , 放在此处
    public final boolean release(int arg) {
        // 尝试释放锁 , 进入  ㈠
        if (tryRelease(arg)) {
            // 队列头节点  unpark
            Node h = head;
            if (
            // 队列不为  null
            h != null &&
            // waitStatus == Node.SIGNAL 才需要  unpark
            h.waitStatus != 0 ) {
                // unpark AQS 中等待的线程 , 进入  ㈡
                unparkSuccessor(h); }
            return true; }
        return false; }
    // ㈠  Sync 继承过来的方法 , 方便阅读 , 放在此处
    protected final boolean tryRelease(int releases) {
        // state--
        int c = getState() - releases;
        if (Thread.currentThread() != getExclusiveOwnerThread())
        throw new IllegalMonitorStateException(); boolean free = false;
        // 支持锁重入 , 只有  state 减为  0, 才释放成功
        if (c == 0) {
            free = true;
            setExclusiveOwnerThread(null); }
        setState(c);
        return free; }
    // ㈡  AQS 继承过来的方法 , 方便阅读 , 放在此处
    private void unparkSuccessor(Node node) {
        // 如果状态为  Node.SIGNAL 尝试重置状态为  0
        // 不成功也可以
        int ws = node.waitStatus;
        if (ws < 0) {
            compareAndSetWaitStatus(node, ws, 0);
        }

        // 找到需要  unpark 的节点 , 但本节点从  AQS 队列中脱离 , 是由唤醒节点完成的

        Node s = node.next;
        // 不考虑已取消的节点 , 从 AQS 队列从后至前找到队列最前面需要  unpark 的节点
        if (s == null || s.waitStatus > 0) { s = null;
            for (Node t = tail; t != null && t != node; t = t.prev) if (t.waitStatus <= 0)
            s = t; }
        if (s != null)
        LockSupport.unpark(s.thread); }
}
```

### 2. 可重入原理

```java
static final class NonfairSync extends Sync {
    // ...
    // Sync 继承过来的方法 , 方便阅读 , 放在此处
    final boolean nonfairTryAcquire(int acquires) {
        final Thread current = Thread.currentThread(); int c = getState();
        if (c == 0) {
            if (compareAndSetState(0, acquires)) { setExclusiveOwnerThread(current);
                return true; }
        }
        // 如果已经获得了锁 , 线程还是当前线程 , 表示发生了锁重入
    else if (current == getExclusiveOwnerThread()) {
            // state++
            int nextc = c + acquires;
            if (nextc < 0) // overflow
            throw new Error("Maximum lock count exceeded"); setState(nextc);
            return true; }
        return false; }
    // Sync 继承过来的方法 , 方便阅读 , 放在此处
    protected final boolean tryRelease(int releases) {
        // state--
        int c = getState() - releases;
        if (Thread.currentThread() != getExclusiveOwnerThread())
        throw new IllegalMonitorStateException(); boolean free = false;
        // 支持锁重入 , 只有  state 减为  0, 才释放成功
        if (c == 0) {
            free = true;
            setExclusiveOwnerThread(null); }

        setState(c); return free;
    } }
```

### 3. 可打断原理

#### 不可打断模式

在此模式下，即使它被打断，仍会驻留在 AQS 队列中，一直要等到获得锁后方能得知自己被打断了

```java
// Sync 继承自  AQS
static final class NonfairSync extends Sync {
    // ...

    private final boolean parkAndCheckInterrupt() {
        // 如果打断标记已经是  true, 则  park 会失效
        LockSupport.park(this);
        // interrupted 会清除打断标记
        return Thread.interrupted(); }

    final boolean acquireQueued(final Node node, int arg) { boolean failed = true;
        try {
            boolean interrupted = false;
            for (;;) {
                final Node p = node.predecessor();
                if (p == head && tryAcquire(arg)) { setHead(node);
                    p.next = null;
                    failed = false;
                    // 还是需要获得锁后 , 才能返回打断状态
                    return interrupted; }
                if (
                shouldParkAfterFailedAcquire(p, node) && parkAndCheckInterrupt()
            ) {
                    // 如果是因为  interrupt 被唤醒 , 返回打断状态为  true
                    interrupted = true; }
            }
        } finally {
            if (failed)
            cancelAcquire(node); }
    }


    public final void acquire(int arg) {

        if (
        !tryAcquire(arg) &&
        acquireQueued(addWaiter(Node.EXCLUSIVE), arg) ) {
            // 如果打断状态为  true
            selfInterrupt(); }
    }

    static void selfInterrupt() {
        // 重新产生一次中断
        Thread.currentThread().interrupt(); }
}
```

#### 可打断模式

```java
static final class NonfairSync extends Sync {
    public final void acquireInterruptibly(int arg) throws InterruptedException { if (Thread.interrupted())
        throw new InterruptedException();
        // 如果没有获得到锁 , 进入  ㈠
        if (!tryAcquire(arg))
        doAcquireInterruptibly(arg); }
    // ㈠  可打断的获取锁流程
    private void doAcquireInterruptibly(int arg) throws InterruptedException { final Node node = addWaiter(Node.EXCLUSIVE);
        boolean failed = true;
        try {
            for (;;) {
                final Node p = node.predecessor();
                if (p == head && tryAcquire(arg)) { setHead(node);
                    p.next = null; // help GC failed = false;
                    return; }
                if (shouldParkAfterFailedAcquire(p, node) && parkAndCheckInterrupt()) {
                    // 在  park 过程中如果被  interrupt 会进入此// 这时候抛出异常 , 而不会再次进入  for (;;)
                    throw new InterruptedException(); }
            }
        } finally {
            if (failed)
            cancelAcquire(node); }
    }
}
```

### 4. 公平锁实现原理

```java
static final class FairSync extends Sync {
    private static final long serialVersionUID = -3000897897090466540L;

    final void lock() {
        acquire(1);
    }
    // AQS 继承过来的方法 , 方便阅读 , 放在此处
    public final void acquire(int arg) { if (
        !tryAcquire(arg) &&
        acquireQueued(addWaiter(Node.EXCLUSIVE), arg) ) {
            selfInterrupt(); }
    }
    // 与非公平锁主要区别在于  tryAcquire 方法的实现
    protected final boolean tryAcquire(int acquires) { final Thread current = Thread.currentThread(); int c = getState();
        if (c == 0) {
            // 先检查 AQS 队列中是否有前驱节点 , 没有才去竞争
            if (!hasQueuedPredecessors() &&
            compareAndSetState(0, acquires)) { setExclusiveOwnerThread(current);
                return true; }
        }
    else if (current == getExclusiveOwnerThread()) { int nextc = c + acquires;
            if (nextc < 0)
            throw new Error("Maximum lock count exceeded"); setState(nextc);
            return true; }
        return false; }
    // ㈠  AQS 继承过来的方法 , 方便阅读 , 放在此处
    public final boolean hasQueuedPredecessors() { Node t = tail;
        Node h = head;
        Node s;
        // h != t 时表示队列中有  Node
        return h != t && (
        // (s = h.next) == null 表示队列中还有没有老二
        (s = h.next) == null ||

        // 或者队列中老二线程不是此线程
        s.thread != Thread.currentThread() );
    }
}
```

### 5. 条件变量实现原理

每个条件变量其实就对应着一个等待队列，其实现类是 ConditionObject

#### await 流程

开始 Thread-0 持有锁，调用 await，进入 ConditionObject 的 addConditionWaiter 流程创建新的 Node 状态为 -2（Node.CONDITION），关联 Thread-0，加入等待队列尾部

![原文图片：开始 Thread-0 持有锁，调用 await，进入 ](file:///D:/Java/data/JUC/03-AQS与锁/image-032.jpeg)

接下来进入 AQS 的 fullyRelease 流程，释放同步器上的锁

![原文图片：接下来进入 AQS 的 fullyRelease 流程，](file:///D:/Java/data/JUC/03-AQS与锁/image-033.jpeg)

unpark AQS 队列中的下一个节点，竞争锁，假设没有其他竞争线程，那么 Thread-1竞争成功

![原文图片：unpark AQS 队列中的下一个节点，竞争锁，假设没](file:///D:/Java/data/JUC/03-AQS与锁/image-034.jpeg)

park 阻塞 Thread-0

![原文图片：park 阻塞 Thread-0](file:///D:/Java/data/JUC/03-AQS与锁/image-035.jpeg)

#### signal 流程

假设 Thread-1 要来唤醒 Thread-0

![原文图片：假设 Thread-1 要来唤醒 Thread-0](file:///D:/Java/data/JUC/03-AQS与锁/image-036.jpeg)

进入 ConditionObject 的 doSignal 流程，取得等待队列中第一个 Node，即 Thread-0 所在 Node

![原文图片：进入 ConditionObject 的 doSigna](file:///D:/Java/data/JUC/03-AQS与锁/image-037.jpeg)

执行 transferForSignal 流程，将该 Node 加入 AQS 队列尾部，将 Thread-0 的 waitStatus 改为 0，Thread-3 的waitStatus 改为 -1

![原文图片：执行 transferForSignal 流程，将该 N](file:///D:/Java/data/JUC/03-AQS与锁/image-038.jpeg)

Thread-1 释放锁，进入 unlock 流程，略

#### 源码

```java
public class ConditionObject implements Condition, java.io.Serializable {
    private static final long serialVersionUID = 1173984872572414699L;
    // 第一个等待节点
    private transient Node firstWaiter;
    // 最后一个等待节点
    private transient Node lastWaiter;

    public ConditionObject() { }
    // ㈠  添加一个  Node 至等待队列
    private Node addConditionWaiter() { Node t = lastWaiter;
        // 所有已取消的  Node 从队列链表删除 , 见  ㈡

        if (t != null && t.waitStatus != Node.CONDITION) { unlinkCancelledWaiters();
            t = lastWaiter; }
        // 创建一个关联当前线程的新  Node, 添加至队列尾部
        Node node = new Node(Thread.currentThread(), Node.CONDITION);
        if (t == null)
        firstWaiter = node;
    else
        t.nextWaiter = node; lastWaiter = node;
        return node; }
    // 唤醒  - 将没取消的第一个节点转移至  AQS 队列
    private void doSignal(Node first) { do {
            // 已经是尾节点了
            if ( (firstWaiter = first.nextWaiter) == null) { lastWaiter = null;
            }
            first.nextWaiter = null; } while (
        // 将等待队列中的  Node 转移至  AQS 队列 , 不成功且还有节点则继续循环  曰
        !transferForSignal(first) &&
        // 队列还有节点
        (first = firstWaiter) != null );
    }
    // 外部类方法 , 方便阅读 , 放在此处
    // 曰  如果节点状态是取消 , 返回  false 表示转移失败 , 否则转移成功
    final boolean transferForSignal(Node node) {
        // 如果状态已经不是  Node.CONDITION, 说明被取消了
        if (!compareAndSetWaitStatus(node, Node.CONDITION, 0)) return false;
        // 加入 AQS 队列尾部
        Node p = enq(node);
        int ws = p.waitStatus;
        if (
        // 上一个节点被取消
        ws > 0 ||
        // 上一个节点不能设置状态为  Node.SIGNAL
        !compareAndSetWaitStatus(p, ws, Node.SIGNAL) ) {
            // unpark 取消阻塞 , 让线程重新同步状态
            LockSupport.unpark(node.thread); }
        return true; }

    // 全部唤醒  - 等待队列的所有节点转移至  AQS 队列

    private void doSignalAll(Node first) { lastWaiter = firstWaiter = null;  do {
            Node next = first.nextWaiter;
            first.nextWaiter = null;
            transferForSignal(first);
            first = next;
        } while (first != null);
    }
    // ㈡
    private void unlinkCancelledWaiters() {
        // ...
    }
    // 唤醒  - 必须持有锁才能唤醒 , 因此  doSignal 内无需考虑加锁
    public final void signal() { if (!isHeldExclusively())
        throw new IllegalMonitorStateException(); Node first = firstWaiter;
        if (first != null)
        doSignal(first); }
    // 全部唤醒  - 必须持有锁才能唤醒 , 因此  doSignalAll 内无需考虑加锁
    public final void signalAll() { if (!isHeldExclusively())
        throw new IllegalMonitorStateException(); Node first = firstWaiter;
        if (first != null)
        doSignalAll(first); }
    // 不可打断等待  - 直到被唤醒
    public final void awaitUninterruptibly() {
        // 添加一个  Node 至等待队列 , 见  ㈠
        Node node = addConditionWaiter();
        // 释放节点持有的锁 , 见  四
        int savedState = fullyRelease(node);
        boolean interrupted = false;
        // 如果该节点还没有转移至 AQS 队列 , 阻塞
        while (!isOnSyncQueue(node)) {
            // park 阻塞
            LockSupport.park(this);
            // 如果被打断 , 仅设置打断状态
            if (Thread.interrupted())
            interrupted = true; }
        // 唤醒后 , 尝试竞争锁 , 如果失败进入  AQS 队列
        if (acquireQueued(node, savedState) || interrupted) selfInterrupt();
    }

    // 外部类方法 , 方便阅读 , 放在此处
    // 四  因为某线程可能重入，需要将  state 全部释放
    final int fullyRelease(Node node) {
        boolean failed = true;
        try {
            int savedState = getState();
            if (release(savedState)) {
                failed = false;
                return savedState; } else {
                throw new IllegalMonitorStateException(); }
        } finally {
            if (failed)
            node.waitStatus = Node.CANCELLED; }
    }
    // 打断模式  - 在退出等待时重新设置打断状态
    private static final int REINTERRUPT =  1;
    // 打断模式  - 在退出等待时抛出异常
    private static final int THROW_IE    = -1;
    // 判断打断模式
    private int checkInterruptWhileWaiting(Node node) { return Thread.interrupted() ?
        (transferAfterCancelledWait(node) ? THROW_IE : REINTERRUPT) : 0;
    }
    // ㈤  应用打断模式
    private void reportInterruptAfterWait(int interruptMode) throws InterruptedException {
        if (interruptMode == THROW_IE)
        throw new InterruptedException(); else if (interruptMode == REINTERRUPT)
        selfInterrupt(); }
    // 等待  - 直到被唤醒或打断
    public final void await() throws InterruptedException { if (Thread.interrupted()) {
            throw new InterruptedException(); }
        // 添加一个  Node 至等待队列 , 见  ㈠
        Node node = addConditionWaiter();
        // 释放节点持有的锁
        int savedState = fullyRelease(node);
        int interruptMode = 0;
        // 如果该节点还没有转移至 AQS 队列 , 阻塞
        while (!isOnSyncQueue(node)) {
            // park 阻塞
            LockSupport.park(this);

            // 如果被打断 , 退出等待队列
            if ((interruptMode = checkInterruptWhileWaiting(node)) != 0) break;
        }
        // 退出等待队列后 , 还需要获得  AQS 队列的锁
        if (acquireQueued(node, savedState) && interruptMode != THROW_IE)
        interruptMode = REINTERRUPT;
        // 所有已取消的  Node 从队列链表删除 , 见  ㈡
        if (node.nextWaiter != null)
        unlinkCancelledWaiters();
        // 应用打断模式 , 见  ㈤
        if (interruptMode != 0)
        reportInterruptAfterWait(interruptMode); }
    // 等待  - 直到被唤醒或打断或超时
    public final long awaitNanos(long nanosTimeout) throws InterruptedException { if (Thread.interrupted()) {
            throw new InterruptedException(); }
        // 添加一个  Node 至等待队列 , 见  ㈠
        Node node = addConditionWaiter();
        // 释放节点持有的锁
        int savedState = fullyRelease(node);
        // 获得最后期限
        final long deadline = System.nanoTime() + nanosTimeout;
        int interruptMode = 0;
        // 如果该节点还没有转移至 AQS 队列 , 阻塞
        while (!isOnSyncQueue(node)) {
            // 已超时 , 退出等待队列
            if (nanosTimeout <= 0L) {
                transferAfterCancelledWait(node);
                break; }
            // park 阻塞一定时间 , spinForTimeoutThreshold 为  1000 ns
            if (nanosTimeout >= spinForTimeoutThreshold)
            LockSupport.parkNanos(this, nanosTimeout);
            // 如果被打断 , 退出等待队列
            if ((interruptMode = checkInterruptWhileWaiting(node)) != 0) break;
            nanosTimeout = deadline - System.nanoTime(); }
        // 退出等待队列后 , 还需要获得  AQS 队列的锁
        if (acquireQueued(node, savedState) && interruptMode != THROW_IE)
        interruptMode = REINTERRUPT;
        // 所有已取消的  Node 从队列链表删除 , 见  ㈡
        if (node.nextWaiter != null)
        unlinkCancelledWaiters();
        // 应用打断模式 , 见  ㈤
        if (interruptMode != 0)
        reportInterruptAfterWait(interruptMode); return deadline - System.nanoTime();
    }

    // 等待  - 直到被唤醒或打断或超时 , 逻辑类似于  awaitNanos
    public final boolean awaitUntil(Date deadline) throws InterruptedException {
        // ...
    }
    // 等待  - 直到被唤醒或打断或超时 , 逻辑类似于  awaitNanos
    public final boolean await(long time, TimeUnit unit) throws InterruptedException {
        // ...
    }
    // 工具方法  省略  ...
}
```

## 读写锁原理

### 1. 图解流程

读写锁用的是同一个 Sycn 同步器，因此等待队列、 state 等也是同一个

#### t1 w.lock ，t2 r.lock

1）t1 成功上锁，流程与 ReentrantLock 加锁相比没有特殊之处，不同是写锁状态占了 state 的低 16 位，而读锁使用的是 state 的高 16 位

![原文图片：1）t1 成功上锁，流程与 ReentrantLock ](file:///D:/Java/data/JUC/03-AQS与锁/image-039.jpeg)

2）t2 执行 r.lock，这时进入读锁的 sync.acquireShared(1) 流程，首先会进入 tryAcquireShared 流程。如果有写锁占据，那么 tryAcquireShared 返回 -1 表示失败

tryAcquireShared 返回值表示

- -1 表示失败
- 0 表示成功，但后继节点不会继续唤醒
- 正数表示成功，而且数值是还有几个后继节点需要唤醒，读写锁返回 1

![原文图片：正数表示成功，而且数值是还有几个后继节点需要唤醒，读写锁](file:///D:/Java/data/JUC/03-AQS与锁/image-040.jpeg)

3）这时会进入 sync.doAcquireShared(1) 流程，首先也是调用 addWaiter 添加节点，不同之处在于节点被设置为Node.SHARED 模式而非 Node.EXCLUSIVE 模式，注意此时 t2 仍处于活跃状态

![原文图片：3）这时会进入 sync.doAcquireShared](file:///D:/Java/data/JUC/03-AQS与锁/image-041.jpeg)

4）t2 会看看自己的节点是不是老二，如果是，还会再次调用 tryAcquireShared(1) 来尝试获取锁

5）如果没有成功，在 doAcquireShared 内 for (;;) 循环一次，把前驱节点的 waitStatus 改为 -1，再 for (;;) 循环一次尝试 tryAcquireShared(1) 如果还不成功，那么在 parkAndCheckInterrupt() 处 park

![原文图片：5）如果没有成功，在 doAcquireShared 内](file:///D:/Java/data/JUC/03-AQS与锁/image-042.jpeg)

#### t3 r.lock ，t4 w.lock

这种状态下，假设又有 t3 加读锁和 t4 加写锁，这期间t1 仍然持有锁，就变成了下面的样子

![原文图片：这种状态下，假设又有 t3 加读锁和 t4 加写锁，这期](file:///D:/Java/data/JUC/03-AQS与锁/image-043.jpeg)

#### t1 w.unlock

这时会走到写锁的 sync.release(1) 流程，调用 sync.tryRelease(1) 成功，变成下面的样子

![原文图片：这时会走到写锁的 sync.release(1) 流程，](file:///D:/Java/data/JUC/03-AQS与锁/image-044.jpeg)

接下来执行唤醒流程 sync.unparkSuccessor，即让老二恢复运行，这时 t2 在 doAcquireShared 内parkAndCheckInterrupt() 处恢复运行

这回再来一次 for (;;) 执行 tryAcquireShared 成功则让读锁计数加一

![原文图片：这回再来一次 for (;;) 执行 tryAcquir](file:///D:/Java/data/JUC/03-AQS与锁/image-045.jpeg)

这时 t2 已经恢复运行，接下来 t2 调用 setHeadAndPropagate(node, 1)，它原本所在节点被置为头节点

![原文图片：这时 t2 已经恢复运行，接下来 t2 调用 setHe](file:///D:/Java/data/JUC/03-AQS与锁/image-046.jpeg)

事情还没完，在 setHeadAndPropagate 方法内还会检查下一个节点是否是shared，如果是则调用doReleaseShared() 将 head 的状态从 -1 改为 0 并唤醒老二，这时 t3 在 doAcquireShared 内

parkAndCheckInterrupt() 处恢复运行

![原文图片：parkAndCheckInterrupt() 处恢复运](file:///D:/Java/data/JUC/03-AQS与锁/image-047.jpeg)

这回再来一次 for (;;) 执行 tryAcquireShared 成功则让读锁计数加一

![原文图片：这回再来一次 for (;;) 执行 tryAcquir](file:///D:/Java/data/JUC/03-AQS与锁/image-048.jpeg)

这时 t3 已经恢复运行，接下来 t3 调用 setHeadAndPropagate(node, 1)，它原本所在节点被置为头节点

![原文图片：这时 t3 已经恢复运行，接下来 t3 调用 setHe](file:///D:/Java/data/JUC/03-AQS与锁/image-049.jpeg)

下一个节点不是 shared 了，因此不会继续唤醒 t4 所在节点

#### t2 r.unlock ，t3 r.unlock

t2 进入 sync.releaseShared(1) 中，调用 tryReleaseShared(1) 让计数减一，但由于计数还不为零

![原文图片：t2 进入 sync.releaseShared(1) ](file:///D:/Java/data/JUC/03-AQS与锁/image-050.jpeg)

t3 进入 sync.releaseShared(1) 中，调用 tryReleaseShared(1) 让计数减一，这回计数为零了，进入doReleaseShared() 将头节点从 -1 改为 0 并唤醒老二，即

![原文图片：t3 进入 sync.releaseShared(1) ](file:///D:/Java/data/JUC/03-AQS与锁/image-051.jpeg)

之后 t4 在 acquireQueued 中 parkAndCheckInterrupt 处恢复运行，再次 for (;;) 这次自己是老二，并且没有其他竞争，tryAcquire(1) 成功，修改头结点，流程结束

![原文图片：之后 t4 在 acquireQueued 中 park](file:///D:/Java/data/JUC/03-AQS与锁/image-052.jpeg)

### 2. 源码分析

#### 写锁上锁流程

```java
static final class NonfairSync extends Sync {
    // ... 省略无关代码
    // 外部类  WriteLock 方法 , 方便阅读 , 放在此处
    public void lock() { sync.acquire(1);
    }
    // AQS 继承过来的方法 , 方便阅读 , 放在此处
    public final void acquire(int arg) { if (
        // 尝试获得写锁失败
        !tryAcquire(arg) &&
        // 将当前线程关联到一个  Node 对象上 , 模式为独占模式// 进入 AQS 队列阻塞
        acquireQueued(addWaiter(Node.EXCLUSIVE), arg) ) {
            selfInterrupt(); }
    }
    // Sync 继承过来的方法 , 方便阅读 , 放在此处
    protected final boolean tryAcquire(int acquires) {
        // 获得低  16 位 , 代表写锁的  state 计数
        Thread current = Thread.currentThread();
        int c = getState();

        int w = exclusiveCount(c);

        if (c != 0) { if (
            // c != 0 and w == 0 表示有读锁 , 或者
            w == 0 ||
            // 如果  exclusiveOwnerThread 不是自己
            current != getExclusiveOwnerThread() ) {
                // 获得锁失败
                return false; }
            // 写锁计数超过低  16 位 , 报异常
            if (w + exclusiveCount(acquires) > MAX_COUNT)
            throw new Error("Maximum lock count exceeded");
            // 写锁重入 , 获得锁成功
            setState(c + acquires);
            return true; }
        if (
        // 判断写锁是否该阻塞 , 或者
        writerShouldBlock() ||
        // 尝试更改计数失败
        !compareAndSetState(c, c + acquires) ) {
            // 获得锁失败
            return false; }
        // 获得锁成功
        setExclusiveOwnerThread(current);
        return true; }
    // 非公平锁  writerShouldBlock 总是返回 false, 无需阻塞
    final boolean writerShouldBlock() { return false;
    }
}
```

#### 写锁释放流程

```java
static final class NonfairSync extends Sync {
    // ... 省略无关代码
    // WriteLock 方法 , 方便阅读 , 放在此处
    public void unlock() { sync.release(1);
    }
    // AQS 继承过来的方法 , 方便阅读 , 放在此处
    public final boolean release(int arg) {
        // 尝试释放写锁成功
```

```java
if (tryRelease(arg)) {
    // unpark AQS 中等待的线程
    Node h = head;
    if (h != null && h.waitStatus != 0)
    unparkSuccessor(h); return true;
}
return false; }
// Sync 继承过来的方法 , 方便阅读 , 放在此处
protected final boolean tryRelease(int releases) { if (!isHeldExclusively())
    throw new IllegalMonitorStateException(); int nextc = getState() - releases;
    // 因为可重入的原因 , 写锁计数为  0, 才算释放成功
    boolean free = exclusiveCount(nextc) == 0;
    if (free) {
        setExclusiveOwnerThread(null);
    }
    setState(nextc);
    return free; }
}
```

**读锁上锁流程**

```java
static final class NonfairSync extends Sync {
    // ReadLock 方法 , 方便阅读 , 放在此处
    public void lock() {
        sync.acquireShared(1);
    }
    // AQS 继承过来的方法 , 方便阅读 , 放在此处
    public final void acquireShared(int arg) {
        // tryAcquireShared 返回负数 , 表示获取读锁失败
        if (tryAcquireShared(arg) < 0) {
            doAcquireShared(arg);
        }
    }
    // Sync 继承过来的方法 , 方便阅读 , 放在此处
    protected final int tryAcquireShared(int unused) { Thread current = Thread.currentThread();
        int c = getState();
        // 如果是其它线程持有写锁 , 获取读锁失败
        if (
        exclusiveCount(c) != 0 &&
        getExclusiveOwnerThread() != current ) {
            return -1;
```

```java
}
int r = sharedCount(c);
if (
// 读锁不该阻塞 (如果老二是写锁，读锁该阻塞), 并且
!readerShouldBlock() &&
// 小于读锁计数 , 并且
r < MAX_COUNT &&
// 尝试增加计数成功
compareAndSetState(c, c + SHARED_UNIT) ) {
    // ... 省略不重要的代码
    return 1;
}
return fullTryAcquireShared(current); }
// 非公平锁  readerShouldBlock 看  AQS 队列中第一个节点是否是写锁// true 则该阻塞 , false 则不阻塞
final boolean readerShouldBlock() {
    return apparentlyFirstQueuedIsExclusive(); }
// AQS 继承过来的方法 , 方便阅读 , 放在此处
// 与  tryAcquireShared 功能类似 , 但会不断尝试  for (;;) 获取读锁 , 执行过程中无阻塞final int fullTryAcquireShared(Thread current) {
HoldCounter rh = null;
for (;;) {
    int c = getState();
    if (exclusiveCount(c) != 0) {
        if (getExclusiveOwnerThread() != current)
        return -1;
    } else if (readerShouldBlock()) {
        // ... 省略不重要的代码
    }
    if (sharedCount(c) == MAX_COUNT)
    throw new Error("Maximum lock count exceeded"); if (compareAndSetState(c, c + SHARED_UNIT)) {
        // ... 省略不重要的代码
        return 1; }
}
}
// AQS 继承过来的方法 , 方便阅读 , 放在此处
private void doAcquireShared(int arg) {
    // 将当前线程关联到一个  Node 对象上 , 模式为共享模式
    final Node node = addWaiter(Node.SHARED);
    boolean failed = true;
    try {
        boolean interrupted = false;
        for (;;) {
            final Node p = node.predecessor();

            if (p == head) {

                // 再一次尝试获取读锁
                int r = tryAcquireShared(arg);
                // 成功
                if (r >= 0) {
                    // ㈠
                    // r 表示可用资源数 , 在这里总是  1 允许传播
                    //（唤醒 AQS 中下一个  Share 节点）
                    setHeadAndPropagate(node, r);
                    p.next = null; // help GC
                    if (interrupted)
                    selfInterrupt(); failed = false;
                    return;
                }
            }
            if (
            // 是否在获取读锁失败时阻塞（前一个阶段 waitStatus == Node.SIGNAL ）
            shouldParkAfterFailedAcquire(p, node) &&
            // park 当前线程
            parkAndCheckInterrupt() ) {
                interrupted = true; }
        }
    } finally {
        if (failed)
        cancelAcquire(node); }
}
// ㈠  AQS 继承过来的方法 , 方便阅读 , 放在此处
private void setHeadAndPropagate(Node node, int propagate) { Node h = head; // Record old head for check below
    // 设置自己为  head
    setHead(node);
    // propagate 表示有共享资源（例如共享读锁或信号量）
    // 原  head waitStatus == Node.SIGNAL 或  Node.PROPAGATE
    // 现在  head waitStatus == Node.SIGNAL 或  Node.PROPAGATE
    if (propagate > 0 || h == null || h.waitStatus < 0 || (h = head) == null || h.waitStatus < 0) {
        Node s = node.next;
        // 如果是最后一个节点或者是等待共享读锁的节点
        if (s == null || s.isShared()) {
            // 进入  ㈡
            doReleaseShared(); }
    }
}
// ㈡  AQS 继承过来的方法 , 方便阅读 , 放在此处
private void doReleaseShared() {
    // 如果  head.waitStatus == Node.SIGNAL ==> 0 成功 , 下一个节点  unpark

    // 如果  head.waitStatus == 0 ==> Node.PROPAGATE, 为了解决  bug, 见后面分析
    for (;;) {
        Node h = head;
        // 队列还有节点
        if (h != null && h != tail) { int ws = h.waitStatus;
            if (ws == Node.SIGNAL) {
                if (!compareAndSetWaitStatus(h, Node.SIGNAL, 0)) continue;            // loop to recheck cases
                // 下一个节点  unpark 如果成功获取读锁
                // 并且下下个节点还是  shared, 继续  doReleaseShared
                unparkSuccessor(h); }
        else if (ws == 0 &&
            !compareAndSetWaitStatus(h, 0, Node.PROPAGATE)) continue;                // loop on failed CAS
        }
        if (h == head)                    // loop if head changed break;
    }
}
}
```

#### 读锁释放流程

```java
static final class NonfairSync extends Sync {
    // ReadLock 方法 , 方便阅读 , 放在此处
    public void unlock() {
        sync.releaseShared(1);
    }
    // AQS 继承过来的方法 , 方便阅读 , 放在此处
    public final boolean releaseShared(int arg) {
        if (tryReleaseShared(arg)) {
            doReleaseShared();
            return true; }
        return false; }
    // Sync 继承过来的方法 , 方便阅读 , 放在此处
    protected final boolean tryReleaseShared(int unused) {
        // ... 省略不重要的代码
        for (;;) {
            int c = getState();
            int nextc = c - SHARED_UNIT;
            if (compareAndSetState(c, nextc)) {
                // 读锁的计数不会影响其它获取读锁线程 , 但会影响其它获取写锁线程
                // 计数为  0 才是真正释放
                return nextc == 0; }

        }
    }
    // AQS 继承过来的方法 , 方便阅读 , 放在此处
    private void doReleaseShared() {
        // 如果  head.waitStatus == Node.SIGNAL ==> 0 成功 , 下一个节点  unpark // 如果  head.waitStatus == 0 ==> Node.PROPAGATE
        for (;;) {
            Node h = head;
            if (h != null && h != tail) { int ws = h.waitStatus;
                // 如果有其它线程也在释放读锁，那么需要将 waitStatus 先改为  0 // 防止  unparkSuccessor 被多次执行
                if (ws == Node.SIGNAL) {
                    if (!compareAndSetWaitStatus(h, Node.SIGNAL, 0)) continue;            // loop to recheck cases
                    unparkSuccessor(h); }
                // 如果已经是  0 了，改为  -3 ，用来解决传播性，见后文信号量  bug 分析
            else if (ws == 0 &&
                !compareAndSetWaitStatus(h, 0, Node.PROPAGATE)) continue;                // loop on failed CAS
            }
            if (h == head)                    // loop if head changed break;
        }
    }
}
```

## Semaphore 原理

### 1. 加锁解锁流程

Semaphore 有点像一个停车场， permits 就好像停车位数量，当线程获得了 permits 就像是获得了停车位，然后停车场显示空余车位减一

刚开始， permits（state）为 3，这时 5 个线程来获取资源

![原文图片：刚开始， permits（state）为 3，这时 5 ](file:///D:/Java/data/JUC/03-AQS与锁/image-053.jpeg)

假设其中 Thread-1，Thread-2，Thread-4 cas 竞争成功，而 Thread-0 和 Thread-3 竞争失败，进入 AQS 队列park 阻塞

![原文图片：假设其中 Thread-1，Thread-2，Threa](file:///D:/Java/data/JUC/03-AQS与锁/image-054.jpeg)

这时 Thread-4 释放了 permits，状态如下

![原文图片：这时 Thread-4 释放了 permits，状态如下](file:///D:/Java/data/JUC/03-AQS与锁/image-055.jpeg)

接下来 Thread-0 竞争成功， permits 再次设置为 0，设置自己为 head 节点，断开原来的 head 节点， unpark 接下来的 Thread-3 节点，但由于 permits 是 0，因此 Thread-3 在尝试不成功后再次进入 park 状态

![原文图片：接下来 Thread-0 竞争成功， permits 再](file:///D:/Java/data/JUC/03-AQS与锁/image-056.jpeg)

### Semaphore 原理 · 2. 源码分析

```java
static final class NonfairSync extends Sync {
    private static final long serialVersionUID = -2694183684443567898L;

    NonfairSync(int permits) {
        // permits 即  state
        super(permits); }
    // Semaphore 方法 , 方便阅读 , 放在此处
    public void acquire() throws InterruptedException { sync.acquireSharedInterruptibly(1);
    }
    // AQS 继承过来的方法 , 方便阅读 , 放在此处
    public final void acquireSharedInterruptibly(int arg)
    throws InterruptedException { if (Thread.interrupted())
        throw new InterruptedException(); if (tryAcquireShared(arg) < 0)
        doAcquireSharedInterruptibly(arg); }
    // 尝试获得共享锁
    protected int tryAcquireShared(int acquires) { return nonfairTryAcquireShared(acquires);
    }
    // Sync 继承过来的方法 , 方便阅读 , 放在此处
    final int nonfairTryAcquireShared(int acquires) { for (;;) {
            int available = getState();
            int remaining = available - acquires;
            if (
            // 如果许可已经用完 , 返回负数 , 表示获取失败 , 进入  doAcquireSharedInterruptibly
            remaining < 0 ||
            // 如果  cas 重试成功 , 返回正数 , 表示获取成功
            compareAndSetState(available, remaining)

        ) {
                return remaining; }
        }
    }
    // AQS 继承过来的方法 , 方便阅读 , 放在此处
    private void doAcquireSharedInterruptibly(int arg) throws InterruptedException { final Node node = addWaiter(Node.SHARED);
        boolean failed = true;
        try {
            for (;;) {
                final Node p = node.predecessor();
                if (p == head) {
                    // 再次尝试获取许可
                    int r = tryAcquireShared(arg);
                    if (r >= 0) {
                        // 成功后本线程出队（ AQS ）, 所在  Node设置为  head
                        // 如果  head.waitStatus == Node.SIGNAL ==> 0 成功 , 下一个节点  unpark // 如果  head.waitStatus == 0 ==> Node.PROPAGATE
                        // r 表示可用资源数 , 为  0 则不会继续传播
                        setHeadAndPropagate(node, r);
                        p.next = null; // help GC
                        failed = false;
                        return; }
                }
                // 不成功 , 设置上一个节点  waitStatus = Node.SIGNAL, 下轮进入  park 阻塞
                if (shouldParkAfterFailedAcquire(p, node) && parkAndCheckInterrupt())
                throw new InterruptedException(); }
        } finally {
            if (failed)
            cancelAcquire(node); }
    }
    // Semaphore 方法 , 方便阅读 , 放在此处
    public void release() {
        sync.releaseShared(1);
    }
    // AQS 继承过来的方法 , 方便阅读 , 放在此处
    public final boolean releaseShared(int arg) {
        if (tryReleaseShared(arg)) {
            doReleaseShared();
            return true; }
        return false; }

    // Sync 继承过来的方法 , 方便阅读 , 放在此处

    protected final boolean tryReleaseShared(int releases) { for (;;) {
            int current = getState();
            int next = current + releases;
            if (next < current) // overflow
            throw new Error("Maximum permit count exceeded"); if (compareAndSetState(current, next))
            return true; }
    }
}
```

### 3. 为什么要有 PROPAGATE

早期有 bug

- releaseShared 方法

```java
public final boolean releaseShared(int arg) {
    if (tryReleaseShared(arg)) {
        Node h = head;
        if (h != null && h.waitStatus != 0)
        unparkSuccessor(h); return true;
    }
    return false; }
```

- doAcquireShared 方法

```java
private void doAcquireShared(int arg) {
    final Node node = addWaiter(Node.SHARED); boolean failed = true;
    try {
        boolean interrupted = false;
        for (;;) {
            final Node p = node.predecessor();
            if (p == head) {
                int r = tryAcquireShared(arg);
                if (r >= 0) {
                    // 这里会有空档
                    setHeadAndPropagate(node, r);
                    p.next = null; // help GC
                    if (interrupted)
                    selfInterrupt(); failed = false;
                    return;
                }
            }
            if (shouldParkAfterFailedAcquire(p, node) &&
            parkAndCheckInterrupt())

            interrupted = true; }
    } finally {
        if (failed)
        cancelAcquire(node); }
}
```

- setHeadAndPropagate 方法

```java
private void setHeadAndPropagate(Node node, int propagate) { setHead(node);
    // 有空闲资源
    if (propagate > 0 && node.waitStatus != 0) { Node s = node.next;
        // 下一个
        if (s == null || s.isShared())
        unparkSuccessor(node); }
}
```

```text
假设存在某次循环中队列里排队的结点情况为  head(-1)->t1(-1)->t2(-1)
```

- 假设存在将要信号量释放的 T3 和 T4，释放顺序为先 T3 后 T4

#### 正常流程

![图片：Semaphore 传播正常流程时序图（PDF 第 79 页）](file:///D:/Java/data/JUC/03-AQS与锁/page-079-propagate.png)

> 图注：T3、T4 依次释放共享许可。每次 `releaseShared(1)` 都把 head 的 waitStatus 从 -1 改为 0，并 `unparkSuccessor(head)` 唤醒后继；被唤醒的 T1 获取许可后调用 `setHeadAndPropagate`，此时仍有剩余资源（propagate > 0），于是继续 `doReleaseShared()` 把唤醒向后传播，T2 也能被唤醒。图中 `head(-1)->t1(-1)->t2(0)` 是队列初始状态，`head(-1)->t2(0)` 表示 T1 出队后 T2 成为新的等待节点。

#### 产生 bug 的情况

修复前版本执行流程

1. T3 调用 releaseShared(1)，直接调用了 unparkSuccessor(head)，head 的等待状态从 -1 变为 0
2. T1 由于 T3 释放信号量被唤醒，调用tryAcquireShared，假设返回值为 0 （获取锁成功，但没有剩余资源量）
3. T4 调用 releaseShared(1)，此时 head.waitStatus 为 0（此时读到的 head 和 1 中为同一个head），不满足条件，因此不调用 unparkSuccessor(head)
4. T1 获取信号量成功，调用 setHeadAndPropagate 时，因为不满足 propagate > 0（2 的返回值也就是propagate（剩余资源量） == 0），从而不会唤醒后继结点， T2 线程得不到唤醒

#### bug 修复后

```java
private void setHeadAndPropagate(Node node, int propagate) { Node h = head; // Record old head for check below
    // 设置自己为  head
    setHead(node);
    // propagate 表示有共享资源（例如共享读锁或信号量）
    // 原  head waitStatus == Node.SIGNAL 或  Node.PROPAGATE
    // 现在  head waitStatus == Node.SIGNAL 或  Node.PROPAGATE
    if (propagate > 0 || h == null || h.waitStatus < 0 || (h = head) == null || h.waitStatus < 0) {
        Node s = node.next;
        // 如果是最后一个节点或者是等待共享读锁的节点
        if (s == null || s.isShared()) {
            doReleaseShared();
        }
    }
}

private void doReleaseShared() {
    // 如果  head.waitStatus == Node.SIGNAL ==> 0 成功 , 下一个节点  unpark // 如果  head.waitStatus == 0 ==> Node.PROPAGATE
    for (;;) {
        Node h = head;
        if (h != null && h != tail) {
            int ws = h.waitStatus;

            if (ws == Node.SIGNAL) {
                if (!compareAndSetWaitStatus(h, Node.SIGNAL, 0)) continue;            // loop to recheck cases
                unparkSuccessor(h); }
        else if (ws == 0 &&
            !compareAndSetWaitStatus(h, 0, Node.PROPAGATE)) continue;                // loop on failed CAS
        }
        if (h == head)                    // loop if head changed break;
    }
}
```

```text
doReleaseShared()不断尝试  ] head(-1->0), head(0->-3)
unparkSuccessor(head)
[ doReleaseShared()不断尝试  ] head(-1->0), head(0->-3)
```

1. T3 调用 releaseShared()，直接调用了 unparkSuccessor(head)，head 的等待状态从 -1 变为 0
2. T1 由于 T3 释放信号量被唤醒，调用tryAcquireShared，假设返回值为 0 （获取锁成功，但没有剩余资源量）
3. T4 调用 releaseShared()，此时 head.waitStatus 为 0（此时读到的 head 和 1 中为同一个 head），调用doReleaseShared() 将等待状态置为 PROPAGATE（-3）
4. T1 获取信号量成功，调用 setHeadAndPropagate 时，读到 h.waitStatus < 0，从而调用doReleaseShared() 唤醒 T2

---

> 📎 **相关笔记**：[[JUC/并发编程原理/02-synchronized与等待通知|synchronized 与等待通知]] · [[JUC/并发编程原理/04-并发容器|并发容器]] · [[JUC/并发编程基础/04-共享模型-不可变与工具|不可变与工具]]
