---
aliases:
  - 指令级并行
  - CPU 缓存
  - volatile
  - final
---

# CPU 与 volatile

> 来源：JUC/并发编程_原理.docx（只读原文）。本篇包括：指令级并行原理、CPU 缓存结构原理、volatile 原理、final 原理。
>
> 入口：[[JUC/JUC 索引|JUC 索引]]
>
> 前置：[[JUC/并发编程基础/03-共享模型-内存与无锁|共享模型之内存与无锁]]；后续：[[JUC/并发编程原理/02-synchronized与等待通知|synchronized 与等待通知]]。

## 指令级并行原理

### 1. 名词

**Clock Cycle Time**

主频的概念大家接触的比较多，而 CPU 的 Clock Cycle Time （时钟周期时间），等于主频的倒数，意思是 CPU 能够识别的最小时间单位，比如说 4G 主频的 CPU 的 Clock Cycle Time 就是0.25 ns，作为对比，我们墙上挂钟的 Cycle Time 是 1s

例如，运行一条加法指令一般需要一个时钟周期时间

**CPI**

有的指令需要更多的时钟周期时间，所以引出了 CPI（Cycles Per Instruction）指令平均时钟周期数

**IPC**

IPC（Instruction Per Clock Cycle）即 CPI 的倒数，表示每个时钟周期能够运行的指令数

**CPU 执行时间**

程序的 CPU 执行时间，即我们前面提到的 user + system 时间，可以用下面的公式来表示

```text
程序  CPU 执行时间  = 指令数  * CPI * Clock Cycle Time
```

### 2. 鱼罐头的故事

加工一条鱼需要 50 分钟，只能一条鱼、一条鱼顺序加工...

![原文图片：加工一条鱼需要 50 分钟，只能一条鱼、一条鱼顺序加工.](file:///D:/Java/data/JUC/01-CPU与volatile/image-001.jpeg)

可以将每个鱼罐头的加工流程细分为 5 个步骤：

- 去鳞清洗 10分钟
- 蒸煮沥水 10分钟
- 加注汤料 10分钟
- 杀菌出锅 10分钟
- 真空封罐 10分钟

![原文图片：真空封罐 10分钟](file:///D:/Java/data/JUC/01-CPU与volatile/image-002.jpeg)

即使只有一个工人，最理想的情况是：他能够在 10 分钟内同时做好这 5 件事，因为对第一条鱼的真空装罐，不会影响对第二条鱼的杀菌出锅...

### 3. 指令重排序优化

事实上，现代处理器会设计为一个时钟周期完成一条执行时间最长的 CPU 指令。为什么这么做呢？可以想到指令还可以再划分成一个个更小的阶段，例如，每条指令都可以分为： 取指令 - 指令译码 - 执行指令 - 内存访问 - 数据写回这 5 个阶段

![原文图片：事实上，现代处理器会设计为一个时钟周期完成一条执行时间最](file:///D:/Java/data/JUC/01-CPU与volatile/image-003.png)

**术语参考：**

- instruction fetch (IF)
- instruction decode (ID)
- execute (EX)
- memory access (MEM)
- register write back (WB)

在不改变程序结果的前提下，这些指令的各个阶段可以通过重排序和组合来实现指令级并行，这一技术在 80's 中叶到 90's 中叶占据了计算架构的重要地位。

**提示：**

分阶段，分工是提升效率的关键！

指令重排的前提是，重排指令不能影响结果，例如

```java
// 可以重排的例子
int a = 10; // 指令1
int b = 20; // 指令2
System.out.println( a + b );
// 不能重排的例子
int a = 10; // 指令1
int b = a - 5; // 指令2
```

参考： Scoreboarding and the Tomasulo algorithm (which is similar to scoreboarding but makes use of register renaming) are two of the most common techniques for implementing out-of-order execution and instruction-level parallelism.

### 4. 支持流水线的处理器

现代 CPU 支持多级指令流水线，例如支持同时执行取指令 - 指令译码 - 执行指令 - 内存访问 - 数据写回的处理器，就可以称之为五级指令流水线。这时 CPU 可以在一个时钟周期内，同时运行五条指令的不同阶段（相当于一条执行时间最长的复杂指令）， IPC = 1，本质上，流水线技术并不能缩短单条指令的执行时间，但它变相地提高了指令地吞吐率。

**提示：**

奔腾四（Pentium 4）支持高达 35 级流水线，但由于功耗太高被废弃

![原文图片：奔腾四（Pentium 4）支持高达 35 级流水线，但](file:///D:/Java/data/JUC/01-CPU与volatile/image-004.jpeg)

### 5. SuperScalar 处理器

大多数处理器包含多个执行单元，并不是所有计算功能都集中在一起，可以再细分为整数运算单元、浮点数运算单元等，这样可以把多条指令也可以做到并行获取、译码等， CPU 可以在一个时钟周期内，执行多于一条指令， IPC > 1

![原文图片：大多数处理器包含多个执行单元，并不是所有计算功能都集中在](file:///D:/Java/data/JUC/01-CPU与volatile/image-005.jpeg)

![原文图片：大多数处理器包含多个执行单元，并不是所有计算功能都集中在](file:///D:/Java/data/JUC/01-CPU与volatile/image-006.jpeg)

## CPU 缓存结构原理

### 1. CPU 缓存结构

![原文图片：1. CPU 缓存结构](file:///D:/Java/data/JUC/01-CPU与volatile/image-007.jpeg)

查看 cpu 缓存

```bash
⚡  root@yihang01 ~ lscpu
Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                1
On-line CPU(s) list:   0
Thread(s) per core:    1
Core(s) per socket:    1
Socket(s):             1
NUMA node(s):          1
Vendor ID:             GenuineIntel
CPU family:            6
Model:                 142
Model name:            Intel(R) Core(TM) i7-8565U CPU @ 1.80GHz
Stepping:              11
CPU MHz:               1992.002
BogoMIPS:              3984.00
Hypervisor vendor:     VMware
Virtualization type:   full
L1d cache:             32K
L1i cache:             32K
L2 cache:              256K
L3 cache:              8192K
NUMA node0 CPU(s):     0
```

速度比较

| 从 cpu 到 | 大约需要的时钟周期 |
| --- | --- |
| 寄存器 | 1 cycle |
| L1 | 3~4 cycle |
| L2 | 10~20 cycle |
| L3 | 40~45 cycle |
| 内存 | 120~240 cycle |

查看 cpu 缓存行

```bash
⚡  root@yihang01 ~ cat /sys/devices/system/cpu/cpu0/cache/index0/coherency_line_size 64
```

cpu 拿到的内存地址格式是这样的

![原文图片：cpu 拿到的内存地址格式是这样的](file:///D:/Java/data/JUC/01-CPU与volatile/image-008.jpeg)

### 2. CPU 缓存读

读取数据流程如下

- 根据低位，计算在缓存中的索引
- 判断是否有效
- 0 去内存读取新数据更新缓存行
- 1 再对比高位组标记是否一致
- 一致，根据偏移量返回缓存数据
- 不一致，去内存读取新数据更新缓存行

### 3. CPU 缓存一致性

MESI 协议

1. E、S、 M 状态的缓存行都可以满足 CPU 的读请求
2. E 状态的缓存行，有写请求，会将状态改为 M，这时并不触发向主存的写3. E 状态的缓存行，必须监听该缓存行的读操作，如果有，要变为 S 状态

![原文图片：2. E 状态的缓存行，有写请求，会将状态改为 M，这时](file:///D:/Java/data/JUC/01-CPU与volatile/image-009.jpeg)

4. M 状态的缓存行，必须监听该缓存行的读操作，如果有，先将其它缓存（S 状态）中该缓存行变成 I 状态（即6. 的流程），写入主存，自己变为 S 状态
5. S 状态的缓存行，有写请求，走4. 的流程
6. S 状态的缓存行，必须监听该缓存行的失效操作，如果有，自己变为I 状态
7. I 状态的缓存行，有读请求，必须从主存读取

![原文图片：7. I 状态的缓存行，有读请求，必须从主存读取](file:///D:/Java/data/JUC/01-CPU与volatile/image-010.jpeg)

### 4. 内存屏障

Memory Barrier（Memory Fence）

- 可见性
- 写屏障（sfence）保证在该屏障之前的，对共享变量的改动，都同步到主存当中
- 而读屏障（lfence）保证在该屏障之后，对共享变量的读取，加载的是主存中最新数据
- 有序性
- 写屏障会确保指令重排序时，不会将写屏障之前的代码排在写屏障之后
- 读屏障会确保指令重排序时，不会将读屏障之后的代码排在读屏障之前

## volatile 原理

volatile 的底层实现原理是内存屏障， Memory Barrier（Memory Fence）

- 对 volatile 变量的写指令后会加入写屏障
- 对 volatile 变量的读指令前会加入读屏障

### 1. 如何保证可见性

- 写屏障（sfence）保证在该屏障之前的，对共享变量的改动，都同步到主存当中

```java
public void actor2(I_Result r) { num = 2;
    ready = true; // ready 是  volatile 赋值带写屏障// 写屏障
}
```

- 而读屏障（lfence）保证在该屏障之后，对共享变量的读取，加载的是主存中最新数据

```java
public void actor1(I_Result r) {
    // 读屏障
    // ready 是  volatile 读取值带读屏障
    if(ready) {
        r.r1 = num + num; } else {
        r.r1 = 1; }
}
```

### 2. 如何保证有序性

- 写屏障会确保指令重排序时，不会将写屏障之前的代码排在写屏障之后

```java
public void actor2(I_Result r) { num = 2;
    ready = true; // ready 是  volatile 赋值带写屏障// 写屏障
}
```

- 读屏障会确保指令重排序时，不会将读屏障之后的代码排在读屏障之前

```java
public void actor1(I_Result r) {
    // 读屏障
    // ready 是  volatile 读取值带读屏障
    if(ready) {
        r.r1 = num + num; } else {
        r.r1 = 1; }
}
```

还是那句话，不能解决指令交错：

- 写屏障仅仅是保证之后的读能够读到最新的结果，但不能保证读跑到它前面去
- 而有序性的保证也只是保证了本线程内相关代码不被重排序

### 3. double-checked locking 问题

以著名的 double-checked locking 单例模式为例

```java
public final class Singleton { private Singleton() { }
    private static Singleton INSTANCE = null;
    public static Singleton getInstance() {
        if(INSTANCE == null) { // t2
            // 首次访问会同步 ，而之后的使用没有  synchronized
            synchronized(Singleton.class) {  if (INSTANCE == null) { // t1
                    INSTANCE = new Singleton(); }
            }
        }
        return INSTANCE; }
}
```

以上的实现特点是：

- 懒惰实例化
- 首次使用 getInstance() 才使用 synchronized 加锁，后续使用时无需加锁
- 有隐含的，但很关键的一点：第一个 if 使用了 INSTANCE 变量，是在同步块之外

但在多线程环境下，上面的代码是有问题的， getInstance 方法对应的字节码为：

```java
0: getstatic     #2
// Field INSTANCE:Lcn/itcast/n5/Singleton;
3: ifnonnull     37
6: ldc           #3
// class cn/itcast/n5/Singleton
8: dup
9: astore 0
10: monitorenter
11: getstatic     #2


// Field INSTANCE:Lcn/itcast/n5/Singleton;
14: ifnonnull     27
17: new           #3
// class cn/itcast/n5/Singleton
20: dup
21: invokespecial #4
// Method "<init>":()V
24: putstatic     #2
// Field INSTANCE:Lcn/itcast/n5/Singleton;
27: aload_0
28: monitorexit
29: goto          37
32: astore 1
33: aload_0
34: monitorexit
35: aload_1
36: athrow
37: getstatic     #2
40: areturn


// Field INSTANCE:Lcn/itcast/n5/Singleton;
```

其中

```java
17 表示创建对象，将对象引用入栈 // new Singleton .  20 表示复制一份对象引用  // 引用地址
```

- 21 表示利用一个对象引用，调用构造方法
- 24 表示利用一个对象引用，赋值给 static INSTANCE

也许 jvm 会优化为：先执行24，再执行 21。如果两个线程 t1，t2 按如下时间序列执行：

```java
17: new

20: dup

24: putstatic(给  INSTANCE 赋值)
0: getstatic(获取  INSTANCE 引用)
3: ifnonnull 37(判断不为空 , 跳转  37 行)

37: getstatic(获取  INSTANCE 引用)
40: areturn(返回)

使用对象

21: invokespecial(调用构造方法)


t1                     INSTANCE                    t2                        t1                     INSTANCE                    t2
```

关键在于 0: getstatic 这行代码在 monitor 控制之外，它就像之前举例中不守规则的人，可以越过 monitor 读取INSTANCE 变量的值

这时 t1 还未完全将构造方法执行完毕，如果在构造方法中要执行很多初始化操作，那么 t2 拿到的是将是一个未初始化完毕的单例

对 INSTANCE 使用 volatile 修饰即可，可以禁用指令重排，但要注意在 JDK 5 以上的版本的 volatile 才会真正有效

### 4. double-checked locking 解决

```java
public final class Singleton { private Singleton() { }
    private static volatile Singleton INSTANCE = null; public static Singleton getInstance() {
        // 实例没创建 ，才会进入内部的  synchronized代码块
        if (INSTANCE == null) {
            synchronized (Singleton.class) { // t2
                // 也许有其它线程已经创建实例 ，所以再判断一次if (INSTANCE == null) { // t1
                INSTANCE = new Singleton(); }
        }
    }
    return INSTANCE; }
}
```

字节码上看不出来 volatile 指令的效果

```java
// -------------------------------------> 加入对  INSTANCE 变量的读屏障
0: getstatic     #2                  // Field INSTANCE:Lcn/itcast/n5/Singleton;

3: ifnonnull     37
6: ldc           #3                  // class cn/itcast/n5/Singleton
8: dup
9: astore_0
10: monitorenter      > 保证原子性、可见性
11: getstatic     #2                  // Field INSTANCE:Lcn/itcast/n5/Singleton;
14: ifnonnull     27
17: new           #3                  // class cn/itcast/n5/Singleton
20: dup
21: invokespecial #4                  // Method "<init>":()V
24: putstatic     #2                  // Field INSTANCE:Lcn/itcast/n5/Singleton;
//      > 加入对  INSTANCE 变量的写屏障
27: aload_0
28: monitorexit      > 保证原子性、可见性
29: goto          37
32: astore_1
33: aload_0
34: monitorexit
35: aload_1
36: athrow
37: getstatic     #2                  // Field INSTANCE:Lcn/itcast/n5/Singleton;
40: areturn
```

如上面的注释内容所示，读写 volatile 变量时会加入内存屏障（Memory Barrier（Memory Fence）），保证下面两点：

- 可见性
- 写屏障（sfence）保证在该屏障之前的t1 对共享变量的改动，都同步到主存当中
- 而读屏障（lfence）保证在该屏障之后 t2 对共享变量的读取，加载的是主存中最新数据
- 有序性
- 写屏障会确保指令重排序时，不会将写屏障之前的代码排在写屏障之后
- 读屏障会确保指令重排序时，不会将读屏障之后的代码排在读屏障之前
- 更底层是读写变量时使用 lock 指令来多核 CPU 之间的可见性与有序性

```java
17: new

20: dup

21: invokespecial(调用构造方法)

0: getstatic(获取  INSTANCE 引用, 带读屏障)
24: putstatic(给  INSTANCE 赋值, 带写屏障)
3: ifnonnull 37(判断不为空, 跳转  37 行)

37: getstatic(获取  INSTANCE 引用)
40: areturn(返回)

使用对象


t1                    INSTANCE                    t2                       t1                       t2                    INSTANCE
```

## final 原理

### 1. 设置 final 变量的原理

理解了 volatile 原理，再对比 final 的实现就比较简单了

```java
public class TestFinal { final int a = 20;
}
```

**字节码**

```text
0: aload_0
1: invokespecial #1 // Method java/lang/Object."<init>":()V
4: aload_0
5: bipush 20
7: putfield #2 // Field a:I
<-- 写屏障
10: return
```

发现 final 变量的赋值也会通过 putfield 指令来完成，同样在这条指令之后也会加入写屏障，保证在其它线程读到它的值时不会出现为 0 的情况

### 2. 获取 final 变量的原理

> 原文此处无正文，《并发编程_原理》PDF 同样只有标题、没有展开内容。

---

> 📎 **相关笔记**：[[JUC/并发编程原理/02-synchronized与等待通知|synchronized 与等待通知]] · [[JUC/并发编程基础/03-共享模型-内存与无锁|内存与无锁]] · [[JUC/JUC 索引|JUC 索引]]
