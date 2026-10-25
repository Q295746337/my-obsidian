# -*- coding: utf-8 -*-
import zipfile, json, re, os, hashlib, io, shutil
from collections import defaultdict
from lxml import etree
from PIL import Image

DOCX = '八股文/八股文.docx'
OUT = '八股文'
IMGROOT = r'D:/Java/data/八股文'
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'

z = zipfile.ZipFile(DOCX)
root = etree.fromstring(z.read('word/document.xml'))
body = root.find(W + 'body')
rels = etree.fromstring(z.read('word/_rels/document.xml.rels'))
relmap = {r.get('Id'): r.get('Target') for r in rels}
media_info = {}
for n in z.namelist():
    if n.startswith('word/media/'):
        name = n.replace('word/', '')
        data = z.read(n)
        try:
            im = Image.open(io.BytesIO(data))
            w, h = im.width, im.height
        except Exception:
            w = h = 0
        media_info[name] = (len(data), w, h, hashlib.sha256(data).hexdigest(), data)

CJK_CHAR = re.compile(r'[㐀-鿿]')

REPL = [
    ('您常', '异常'), ('您步', '异步'), ('Threal', 'Thread'), ('qet', 'get'), ('nuI', 'null'),
    ('Ful GC', 'Full GC'), ('FulGC', 'FullGC'), ('IVM', 'JVM'), ('Accpet', 'Accept'),
    ('Consitency', 'Consistency'), ('AnalvticDB', 'AnalyticDB'), ('Bu fer', 'Buffer'),
    ('finaly', 'finally'), ('干亿', '千亿'), ('数干', '数千'), ('无线', '无限'), ('Sate less', 'Stateless'),
    ('RocktMQ', 'RocketMQ'), ('Actomic', 'Atomic'), ('Sping', 'Spring'), ('TheadLocal', 'ThreadLocal'),
    ('3L的必胜', '30的必胜'), ('L-1 LL', '1-100'), ('1 LL 个', '100 个'), ('1 LL', '100'),
    ('Al 项目', 'AI 项目'), ('Al 生成', 'AI 生成'), ('A1生成', 'AI生成'), ('A1 生成', 'AI 生成'),
    ('Al 与', 'AI 与'), ('Al 技术', 'AI 技术'), ('差您', '差异'),
]


def fix_ocr(t):
    for a, b in REPL:
        t = t.replace(a, b)
    t = re.sub(r'(?<![A-Za-z])Al(?![A-Za-z])', 'AI', t)
    t = re.sub(r'(\d)\. (\d)', r'\1.\2', t)
    t = t.replace('ⅱ', 'ii')
    return t


def is_cjk(ch):
    return bool(CJK_CHAR.match(ch))


def clean_text(t, keep_lines=False):
    t = t.replace('​', '').replace('\xa0', ' ')
    if keep_lines:
        lines = [l.rstrip() for l in t.split('\n')]
        lines = [l for l in lines if l.strip() != '']
        t = '\n'.join(lines)
    else:
        lines = [l.strip() for l in t.split('\n')]
        out = ''
        for l in lines:
            if not l:
                continue
            if not out:
                out = l
                continue
            prev = out[-1]
            nxt = l[0]
            if is_cjk(prev) or is_cjk(nxt) or prev in '，。；：、（）《》！？':
                out += l
            else:
                out += ' ' + l
        t = out
    t = fix_ocr(t)
    t = re.sub(r'[ \t]{2,}', ' ', t)
    t = re.sub(r'\s+([，。；：、！？）】》])', r'\1', t)
    t = re.sub(r'([（【《])\s+', r'\1', t)
    t = re.sub(r'^[√✓]\s*', '', t)
    return t.strip()


def ptext(p):
    return ''.join(x.text or '' for x in p.iter(W + 't'))


def psize(p):
    ss = []
    for r in p.iter(W + 'r'):
        rpr = r.find(W + 'rPr')
        if rpr is not None:
            sz = rpr.find(W + 'sz')
            if sz is not None:
                try:
                    ss.append(int(sz.get(W + 'val')) / 2)
                except Exception:
                    pass
    return max(ss) if ss else None


def pimgs(p):
    out = []
    for blip in p.iter(A + 'blip'):
        rid = blip.get(R + 'embed')
        if rid and rid in relmap:
            out.append(relmap[rid])
    return out


blocks = []
pidx = 0
tidx = 0
for ch in body:
    if ch.tag == W + 'p':
        if pidx >= 165:
            blocks.append({'kind': 'p', 'pidx': pidx, 'size': psize(ch), 'text': ptext(ch), 'imgs': pimgs(ch)})
        pidx += 1
    elif ch.tag == W + 'tbl':
        rows = []
        for tr in ch.findall(W + 'tr'):
            cells = []
            for tc in tr.findall(W + 'tc'):
                cells.append('\n'.join(ptext(p) for p in tc.findall(W + 'p')))
            rows.append(cells)
        blocks.append({'kind': 'tbl', 'tidx': tidx, 'rows': rows})
        tidx += 1

BOUNDS = [(165, 11), (229, 1), (692, 2), (1379, 3), (2006, 4), (2584, 5), (3241, 6), (3541, 7),
          (3920, 8), (4744, 9), (5804, 10), (5917, 9), (6104, 11), (6133, 9), (6617, 10), (7388, 11)]


def cat_for(pidx):
    c = 11
    for b, cc in BOUNDS:
        if pidx >= b:
            c = cc
    return c


INSERTS = {
    1379: [('JVM 运行流程', 2)],
    1458: [('垃圾回收', 2)],
    1549: [('三色标记法', 2)],
    1617: [('类加载与双亲委派', 2)],
    1957: [('如何选择垃圾回收器', 2)],
    398: [('反射', 2)],
    911: [('ThreadLocal', 2)],
    1072: [('CAS', 2)],
    1119: [('JMM', 2)],
    1093: [('乐观锁与悲观锁', 2)],
    1294: [('多线程的上下文切换', 2)],
    1363: [('Unsafe', 2)],
    2461: [('主从复制', 3)],
    2092: [('索引', 2)],
    2536: [('查询关键字的执行顺序', 3)],
    2553: [('聚簇索引和非聚簇索引', 3)],
    3182: [('Redis 是单线程还是多线程', 3)],
    3189: [('Redis 为什么使用单线程执行命令', 3)],
    3197: [('Redis 6.0 为什么引入多线程', 3)],
    3222: [('Redis 是 AP 还是 CP', 3)],
    3231: [('Redis 支持事务/回滚吗', 3)],
    3417: [('如何保证消息不重复消费', 3)],
    3436: [('如何保证消息顺序消费', 3)],
    3447: [('Rebalance 机制', 3)],
    3465: [('自动提交 offset', 3)],
    3475: [('消息堆积的处理', 3)],
    3487: [('消息队列的作用与选型', 2)],
    3505: [('消息队列对比与技术选型', 3)],
    3517: [('ISR 机制', 2)],
    3647: [('Spring Bean 的作用域', 2)],
    3667: [('SpringBoot 自动装配原理', 2)],
    3690: [('Spring MVC 的执行流程', 2)],
    3702: [('Spring 中的设计模式', 2)],
    4169: [('TCP 粘包与拆包', 3)],
    4372: [('HTTP 状态码', 2)],
    4386: [('GET 和 POST 请求的区别', 2)],
    4479: [('进程、线程与协程', 2)],
    4515: [('内存管理', 2)],
    4544: [('死锁', 2)],
    4577: [('IO 多路复用', 2)],
    4593: [('Linux 常用命令', 2)],
    4620: [('中断', 2)],
    4633: [('孤儿进程与僵尸进程', 2)],
    4658: [('用户态与内核态', 2)],
    4677: [('进程调度算法', 2)],
    4744: [('CAP 与 BASE', 2)],
    4783: [('微服务调用链日志追踪', 2)],
    4801: [('负载均衡', 2)],
    4970: [('与外部服务交互的稳定性', 2)],
    5917: [('分库分表', 2)],
    5943: [('分片键选择', 3)],
    5970: [('分片算法', 3)],
    6044: [('分库分表的常见问题', 2)],
    7393: [('问题自查表', 3)],
    7283: [('RAG', 2)],
    7004: [('Multi-Agent', 2)],
}
OVERRIDES = {889: ('对 i++ 问题的深入分析', 2, 'h24'), 1327: ('原子类', 2, 'h24'),
             3574: ('Spring 常见注解', 2, 'h21'), 6091: ('分库分表后的全局分布式 ID', 3, 'h18')}
H2_RESET = {'AQS', 'ReentrantLock', '循环依赖问题', '三级缓存 && 解决原理', '不同点',
            'Redis 主从（非重点）', 'Redis 哨兵（非重点）', 'Redis Cluster （ 重点）',
            'Codis (非重点内容，拓展， 可不看)', '排序算法', '数据一致性', '了解 Function Calling 吗',
            '了解 MCP 吗', 'Agent Skill 从使用到原理全面解析'}
H2_RESET_N = {re.sub(r'\s+', '', x) for x in H2_RESET}
H24_PROMOTE = {'Hot100', '数据一致性', '排序算法'}
H21_INSERTS = {'JVM 运行流程', '反射'}

CATS = {
    1: ('01-JavaSE基础与集合', 'JavaSE 基础与集合', '[[JavaSE/JavaSE 索引|JavaSE]]',
        '[[八股文/02-JUC并发|JUC 并发]] · [[JavaSE/JavaSE 索引|JavaSE]] · [[八股文/03-JVM|JVM]]',
        '集合、泛型、反射、动态代理、JDK 新特性、String、异常与 IO'),
    2: ('02-JUC并发', 'JUC 并发', '[[JUC/JUC 索引|JUC]]',
        '[[八股文/01-JavaSE基础与集合|JavaSE]] · [[JUC/JUC 索引|JUC]] · [[八股文/03-JVM|JVM]]',
        '线程、线程池、锁、CAS、JMM、ThreadLocal、原子类与并发工具'),
    3: ('03-JVM', 'JVM', '[[JVM/JVM 索引|JVM]]',
        '[[八股文/02-JUC并发|JUC]] · [[JVM/JVM 索引|JVM]] · [[八股文/09-场景设计与算法|场景设计]]',
        '运行时数据区、对象分配、垃圾回收、类加载、JIT 与 JVM 调优'),
    4: ('04-MySQL', 'MySQL', '[[MySQL/MySQL 索引|MySQL]]',
        '[[八股文/05-Redis|Redis]] · [[MySQL/MySQL 索引|MySQL]] · [[八股文/09-场景设计与算法|场景设计]]',
        '事务与 MVCC、索引与 B+ 树、日志、执行计划、SQL 优化、存储引擎'),
    5: ('05-Redis', 'Redis', '[[Redis/Redis 索引|Redis]]',
        '[[八股文/04-MySQL|MySQL]] · [[Redis/Redis 索引|Redis]] · [[八股文/09-场景设计与算法|场景设计]]',
        '数据类型与底层结构、分布式锁、持久化、淘汰策略、缓存三兄弟、高可用'),
    6: ('06-Kafka与消息队列', 'Kafka 与消息队列', '[[微服务/微服务 索引|微服务]]',
        '[[微服务/微服务 索引|微服务]] · [[八股文/05-Redis|Redis]] · [[八股文/09-场景设计与算法|场景设计]]',
        'Kafka 体系结构、消息不丢失/不重复/顺序、Rebalance、ISR 与 MQ 选型'),
    7: ('07-Spring与框架', 'Spring 与框架', '[[SSM框架/SSM框架 索引|SSM]] · [[SpringBoot2/SpringBoot2 索引|SpringBoot2]]',
        '[[SSM框架/SSM框架 索引|SSM]] · [[SpringBoot2/SpringBoot2 索引|SpringBoot2]] · [[八股文/10-设计模式与AI|设计模式]]',
        'IOC/AOP、SpringMVC、SpringBoot、事务、循环依赖与自动装配'),
    8: ('08-计算机网络与操作系统', '计算机网络与操作系统', '[[JavaWeb/JavaWeb 索引|JavaWeb]] · [[JVM/JVM 索引|JVM]]',
        '[[JavaWeb/JavaWeb 索引|JavaWeb]] · [[JVM/JVM 索引|JVM]] · [[八股文/09-场景设计与算法|场景设计]]',
        'HTTP/HTTPS、TCP、CDN、进程线程、内存、死锁、IO 多路复用与 Linux'),
    9: ('09-场景设计与算法', '场景设计与算法', '[[MySQL/MySQL 索引|MySQL]] · [[Redis/Redis 索引|Redis]] · [[JUC/JUC 索引|JUC]]',
        '[[八股文/04-MySQL|MySQL]] · [[八股文/05-Redis|Redis]] · [[JUC/JUC 索引|JUC]]',
        '分布式理论、QPS 预估、秒杀、RPC、分库分表、排序与智力题'),
    10: ('10-设计模式与AI', '设计模式与 AI', '[[AI/AI 索引|AI]] · [[SSM框架/SSM框架 索引|SSM]]',
         '[[AI/AI 索引|AI]] · [[SSM框架/SSM框架 索引|SSM]] · [[八股文/09-场景设计与算法|场景设计]]',
         '单例/策略/观察者、大模型、Agent、Function Calling、MCP、Skill 与 RAG'),
    11: ('11-面试经验与简历', '面试经验与简历', '[[面试/面试 索引|面试]]',
         '[[面试/面试 索引|面试]] · [[八股文/八股文 索引|八股文索引]] · [[八股文/09-场景设计与算法|场景设计]]',
         '文档说明、面试与简历经验、秋招笔试题、问题自查表'),
}


def is_question(t):
    return len(t) <= 75 and '。' not in t and (
        t.endswith('？') or t.endswith('吗') or t.endswith('呢')
        or re.match(r'^(为什么|如何|怎么|什么是|谈谈|说说|请|介绍一下|了解|你了解)', t) is not None)


LABEL_EXACT = {
    '底层的数据结构', '添加元素流程', '扩容加载因子0.75', '扩容为数组长度的2倍', '核心概念',
    '主要构成', '实现步骤', '具体应用', '关键问题', '整体架构', '分片原理', '集群伸缩',
    '参数传递方式', '请求的可见性', '数据长度', '幂等性', '缓存', '使用场景', '安全性',
    '可重复性', '总结', '总结表格', '堆划分', '消息队列的作用', '实现方式', '解决方案',
    '优点', '缺点', '实现原理', '背景知识', '背景', '定义', '原理', '策略', '淘汰流程',
    '适用场景', '目的', '原因', '好处', '注意', '提示', '对比', '区别', 'Map双列集合',
    'MVCC的实现依赖于', '实现原理',
}


def is_label(t):
    if not (2 <= len(t) <= 20):
        return False
    if t.endswith('：') or t.endswith(':'):
        return True
    return t in LABEL_EXACT


def listify(t):
    m = re.match(r'^([●○■◆▪◦])\s*', t)
    if m:
        ind = {'●': '- ', '○': '  - ', '■': '    - ', '◆': '- ', '▪': '  - ', '◦': '    - '}.get(m.group(1), '- ')
        return ind + t[m.end():].strip()
    m = re.match(r'^(\d{1,2})\.\s+(?![0-9])', t)
    if m:
        return f'{m.group(1)}. ' + t[m.end():].strip()
    m = re.match(r'^(\d{1,2})、\s*', t)
    if m:
        return f'{m.group(1)}. ' + t[m.end():].strip()
    m = re.match(r'^(\d{1,2})）\s*', t)
    if m:
        return f'{m.group(1)}. ' + t[m.end():].strip()
    m = re.match(r'^([a-zA-Z])[.、]\s+', t)
    if m:
        return '- ' + t[m.end():].strip()
    return None


def code_para(t):
    s = t.strip()
    if not s or len(s) > 400:
        return False
    if '\n' in s:
        lines = [l.strip() for l in s.split('\n') if l.strip()]
        if len(lines) >= 2 and sum(1 for l in lines if re.match(
                r'^(public|private|protected|class|interface|import|package|@|//|/\*|\*|for|if|while|return|try|catch|int|String|System|SELECT|select|UPDATE|update|INSERT|insert|DELETE|delete)', l)) >= len(lines) * 0.6:
            return True
    patterns = [r'^(public|private|protected)\s+', r'^(class|interface|enum)\s+', r'^import\s+', r'^@\w+',
                r'^(SELECT|UPDATE|INSERT|DELETE|select|update|insert|delete)\s+',
                r'^[A-Za-z_][\w<>\[\]]*\s+\w+\s*=\s*new\s+', r'^[A-Za-z_][\w<>\[\]]*\s+\w+\s*=\s*[^;]+;$',
                r'^(String|int|long|boolean|char|byte|double|float)\s+\w+\s*[=;]', r'^System\.out\.', r'^return\s+',
                r'^Authorization:\s',
                r'^(netstat|df|top|jstack|jmap|jps|grep|kill|cat|head|tail|vim|vi|find|ps|free)\s',
                r'^-[A-Za-z]', r'^[A-Za-z_][\w.]*\s*=\s*[^;]+$']
    return any(re.search(p, s) for p in patterns)


def code_lang(t):
    s = t.strip()
    if re.match(r'^(SELECT|UPDATE|INSERT|DELETE|select|update|insert|delete)\b', s):
        return 'sql'
    if re.match(r'^(netstat|df|top|jstack|jmap|ps|free|grep|kill|cat|head|tail|vim|vi|find)\s', s):
        return 'bash'
    if s.startswith('Authorization:'):
        return 'http'
    if re.match(r'^[A-Za-z_][\w.]*\s*=\s*[^;]+$', s) and not s.endswith(';'):
        return 'properties'
    return 'java'


def split_numbered_code(text):
    t = text.replace('\r', '')
    t = re.sub(r'(?:(?<=\s)|^)(\d{1,3})\s{2,}', r'\n\1\t', t)
    lines = []
    for l in t.split('\n'):
        l = l.strip()
        if not l:
            continue
        m = re.match(r'^(\d{1,3})\t?(.*)$', l)
        if m:
            lines.append(m.group(2))
        else:
            lines.append(l)
    out = []
    for l in lines:
        l = re.sub(r'(\d{8,})$', '', l).rstrip()
        l = re.sub(r'^-\s{2,}', '', l)
        out.append(l)
    while out and not out[-1].strip():
        out.pop()
    res = '\n'.join(out)
    res = re.sub(r'(?<=[㐀-鿿])(\d{1,2})\s*}\s*$', '\n}', res, flags=re.M)
    return clean_code_header_lines(res)


def is_code_table(rows):
    if not rows:
        return (False, None)
    allcells = [c.strip() for r in rows for c in r]
    lang = None
    for L, lg in [('Java', 'java'), ('SQL', 'sql'), ('YAML', 'yaml'), ('Plain Text', 'text'), ('C', 'c')]:
        if any(c.strip().lower() == L.lower() for c in allcells[:8]):
            lang = lg
            break
    if 'SQL' in allcells and any(re.fullmatch(r'\d+', r[0].strip()) for r in rows if r):
        lang = 'sql'
    first = [r[0].strip() for r in rows if r]
    nums = [int(x) for x in first if re.fullmatch(r'\d+', x)]
    seq = len(nums) >= 3 and nums[:len(nums)] == list(range(1, len(nums) + 1))
    if lang:
        return (True, lang)
    if seq:
        return (True, 'java')
    return (False, None)


def join_code_cells(cells):
    cells = [c.strip() for c in cells if c.strip()]
    if not cells:
        return ''
    sql = any(re.search(r'\b(select|from|where|and|or|group by|order by|limit|join|on|having|update|insert|delete|set|values)\b', c, re.I) for c in cells)
    if sql:
        return ' '.join(cells)
    out = cells[0]
    for c in cells[1:]:
        if re.search(r'[A-Za-z0-9_]$', out) and re.match(r'[a-z0-9_]', c):
            out += c
        elif out.endswith(('(', '[', '{', '<', '.')) or c.startswith((')', ']', '}', ';', ',', '.', '<')):
            out += c
        else:
            out += ' ' + c
    return out


MARKERS = {'java', 'sql', 'yaml', 'c', 'plain text', 'w'}


def clean_code_header_lines(code):
    out = []
    for l in code.split('\n'):
        compact = re.sub(r'\s+', ' ', l).strip()
        if (re.search(r'\b(Java|SQL|YAML|C|Plain Text)\s*$', compact)
                and not re.search(r'[{};()=]', compact) and len(compact) < 120):
            continue
        out.append(l)
    return '\n'.join(out)


def indent_java(code):
    out = []
    level = 0
    for line in code.split('\n'):
        s = line.strip()
        if not s:
            out.append('')
            continue
        lead = s.startswith('}')
        if lead:
            level = max(0, level - 1)
            rest = s[1:]
        else:
            rest = s
        out.append('    ' * level + s)
        level = max(0, level + rest.count('{') - rest.count('}'))
    return '\n'.join(out)


def extract_code(rows):
    lang = None
    allcells = [c.strip() for r in rows for c in r]
    for L, lg in [('Java', 'java'), ('SQL', 'sql'), ('YAML', 'yaml'), ('Plain Text', 'text'), ('C', 'c')]:
        if any(c.strip().lower() == L.lower() for c in allcells[:8]):
            lang = lg
            break
    if lang is None and 'SQL' in allcells:
        lang = 'sql'
    if lang is None:
        lang = 'java'
    if len(rows) <= 3:
        joined = '\n'.join('\n'.join(r) for r in rows)
        if re.search(r'(?:^|\s)\d{1,3}\s{2,}', joined):
            code = split_numbered_code(joined)
            code = '\n'.join(l for l in code.split('\n') if l.strip().lower() not in MARKERS)
            if code.strip():
                return [(None, code, lang)]
    segments = []
    cur = []
    cap = None
    for r in rows:
        cells = [c.strip() for c in r]
        is_header = (len(cells) >= 2 and cells[-1].lower() in ('java', 'sql', 'yaml', 'c', 'plain text')
                     and (cells[0].lower() in ('w', '') or len(cells) > 2))
        if is_header and cur:
            segments.append((cap, cur))
            cur = []
            cap = None
        if is_header:
            cap = None
            for c in cells[:-1]:
                if c and c.lower() not in ('w', 'java', 'sql', 'yaml', 'c', 'plain text'):
                    cap = c
                    break
            continue
        cells = [c for c in cells if c.lower() not in MARKERS]
        if cells and re.fullmatch(r'\d+', cells[0]):
            cells = cells[1:]
        if not any(cells):
            continue
        cur.append(join_code_cells(cells))
    if cur:
        segments.append((cap, cur))
    out = []
    for cap, lines in segments:
        code = '\n'.join(lines)
        code = re.sub(r'(\d{8,})$', '', code).rstrip()
        code = '\n'.join(l for l in code.split('\n') if l.strip().lower() not in MARKERS)
        code = clean_code_header_lines(code)
        if lang == 'java':
            code = indent_java(code)
        if code.strip():
            out.append((cap, code, lang))
    return out


def clean_cell(c):
    c = clean_text(c, keep_lines=True)
    c = re.sub(r'\n+', '<br>', c)
    c = c.replace('● ', '<br>- ').replace('○ ', '<br>  - ').replace('■ ', '<br>    - ')
    c = re.sub(r'^(<br>)+', '', c)
    c = re.sub(r'(<br>)+', '<br>', c)
    c = c.replace('|', '\\|')
    return c.strip()


def pad_rows(rows):
    if not rows:
        return []
    w = max(len(r) for r in rows)
    return [r + [''] * (w - len(r)) for r in rows]


def special_table(rows):
    rows = pad_rows(rows)
    h = [c.strip() for c in rows[0]]
    if h[:1] == ['特性'] and any('GET' in x for x in h):
        return ['| 特性 | GET | POST |', '| --- | --- | --- |',
                '| 用途 | 请求资源或查询数据 | 提交数据或创建/更新资源 |',
                '| 参数位置 | URL 查询字符串（`?key=value&key=value`） | 请求体（body） |',
                '| 数据可见性 | 明文显示在 URL 中 | 参数在请求体中，不显示在 URL 中 |',
                '| 长度限制 | 限制较大（一般为 2048 字符） | 无限制，可以传输大量数据 |',
                '| 缓存 | 可以缓存（浏览器可以缓存 GET 请求） | 通常不缓存 |',
                '| 幂等性 | 幂等（多次相同请求产生相同结果） | 非幂等（每次请求可能产生不同结果） |',
                '| 安全性 | 不适合传递敏感数据（明文传输） | 比较安全，但仍需使用 HTTPS 加密通信 |',
                '| 重复执行 | 支持重复执行（不会产生副作用） | 不支持重复执行（可能导致重复操作） |',
                '| 使用场景 | 获取资源、查询操作、导航等 | 提交表单、上传文件、创建/修改数据等 |']
    if h[:2] == ['阶段', '核心任务']:
        return ['| 阶段 | 核心任务 | 关键规则 |', '| --- | --- | --- |',
                '| 加载 | 读取字节码，生成 Class 对象 | 类加载器负责，支持自定义逻辑 |',
                '| 链接 | 验证、准备、解析符号引用 | 准备阶段仅赋零值，解析可能延迟到初始化后 |',
                '| 初始化 | 执行 `<clinit>()`，完成静态赋值 | 父类优先，线程安全，被动引用不触发 |',
                '| 使用 | 通过实例化、反射等方式使用类 | 类的功能完全可用 |',
                '| 卸载 | 回收类元数据，依赖 GC 和 ClassLoader 回收 | 需同时满足实例、Class 对象、ClassLoader 回收 |']
    if h[:2] == ['取值', '等价写法']:
        return ['| 取值 | 等价写法 | 行为 |', '| --- | --- | --- |',
                '| 0 | - | 不等待确认，直接发送下一条消息。 |',
                '| 1 | - | 等待 Leader 副本确认。 |',
                '| all | -1 | 等待 ISR 中所有副本确认（需配置 `min.insync.replicas` 定义最小副本数）。 |']
    if h and h[0].startswith('代码随想录'):
        data = rows[1:]
        out = ['| 章节 | 分类 | 题目 | 来源 |', '| --- | --- | --- | --- |']
        last = ['', '', '', '']
        for r in data:
            r = pad_rows([r])[0][:4]
            for i in range(4):
                if r[i].strip():
                    last[i] = r[i].strip()
            if not any(x.strip() for x in r):
                continue
            out.append('| ' + ' | '.join(clean_cell(x) for x in last) + ' |')
        return out
    if h[:3] == ['类型', '用途', '底层实现']:
        out = ['| 类型 | 用途 | 底层实现 |', '| --- | --- | --- |']
        for r in rows[1:]:
            r = pad_rows([r])[0][:3]
            if not any(x.strip() for x in r):
                continue
            out.append('| ' + ' | '.join(clean_cell(x) for x in r) + ' |')
        return out
    return None


def render_table(rows, ctx):
    if not rows:
        return []
    rows = pad_rows(rows)
    code, lang = is_code_table(rows)
    if len(rows[0]) == 1:
        texts = [clean_text(r[0]) for r in rows if r and r[0].strip()]
        if not texts:
            return []
        if code or (len(rows) <= 2 and code_para(texts[0])):
            segs = extract_code(rows) if code else [(None, texts[0], code_lang(texts[0]))]
            out = []
            for cap, body, lg in segs:
                if cap:
                    out.append('**' + clean_text(cap) + '**')
                out.append('```' + lg)
                out.append(body)
                out.append('```')
            return out
        if len(texts) == 1 and len(texts[0]) <= 24 and not re.search(r'[，。；：]', texts[0]):
            return ['**' + texts[0] + '**']
        return ['> 注：' + ' '.join(texts)]
    sp = special_table(rows)
    if sp:
        return sp
    if code:
        segs = extract_code(rows)
        out = []
        for cap, body, lg in segs:
            if cap:
                out.append('**' + clean_text(cap) + '**')
            out.append('```' + lg)
            out.append(body)
            out.append('```')
        return out
    header = [clean_cell(c) for c in rows[0]]
    data = rows[1:]
    out = ['| ' + ' | '.join(header) + ' |', '| ' + ' | '.join(['---'] * len(header)) + ' |']
    for r in data:
        if not any(c.strip() for c in r):
            continue
        out.append('| ' + ' | '.join(clean_cell(c) for c in r) + ' |')
    if len(out) == 2:
        return []
    return out


def is_code_line_text(s):
    s = s.strip()
    if not s:
        return False
    if s in ('W Java', 'Java', 'SQL', 'YAML', 'C', 'Plain Text'):
        return True
    if re.fullmatch(r'\d{1,3}', s):
        return True
    if re.match(r'^\d{4,}\s*}', s):
        return True
    if re.match(r'^\d{1,3}\s+\S', s):
        return True
    if re.match(r'^(public|private|protected|class|interface|import|package|@|//|/\*|\*|for|if|while|return|try|catch|else|int|long|String|System|Thread|new|final|static|void|synchronized|count|arr|tempArr|minHeap|LOCK|MAX|semA|semB|semC|thread|thread1)\b', s):
        return True
    if re.match(r'^[A-Za-z_]\w*\s*[=(.;]', s) or re.match(r'^[A-Za-z_]\w*\+\+', s):
        return True
    if s.startswith(('}', ')', '{')):
        return True
    return False


def strip_code_paragraph(t):
    t = re.sub(r'\s+(\d{1,3})\s+}', '\n', t)
    t = re.sub(r'(\d{4,})\s*}', '}', t)
    t = re.sub(r'^(\d{1,3}\s+.*[;}])\s+\d{1,3}\s*$', r'\1', t)
    out = []
    for part in t.split('\n'):
        part = part.strip()
        if not part:
            continue
        m = re.match(r'^(\d{1,3})\s+(.*)$', part)
        if m:
            out.append(m.group(2))
        elif re.fullmatch(r'\d{1,3}', part):
            continue
        elif part in ('W Java', 'Java', 'SQL', 'YAML', 'C', 'Plain Text'):
            continue
        else:
            out.append(re.sub(r'(\d{8,})$', '', part).rstrip())
    return out


def merge_code_runs(blocks):
    out = []
    i = 0
    while i < len(blocks):
        b = blocks[i]
        if (b['kind'] == 'p' and b['size'] not in (24.0, 21.0, 18.0)
                and is_code_line_text(clean_text(b['text']))):
            run = []
            j = i
            while j < len(blocks):
                bj = blocks[j]
                if bj['kind'] == 'p':
                    t = clean_text(bj['text'])
                    if is_code_line_text(t):
                        run.append(t)
                        j += 1
                        continue
                    if not t and bj['imgs']:
                        break
                    break
                break
            code_lines = []
            for t in run:
                code_lines.extend(strip_code_paragraph(t))
            code = '\n'.join(code_lines)
            if len(code_lines) >= 3 and re.search(r'[{};()=]|\b(public|private|class|System|select|update|insert|delete)\b', code, re.I):
                lang = 'sql' if re.search(r'\b(select|from|where|update|insert|delete)\b', code, re.I) else 'java'
                if lang == 'java':
                    code = indent_java(code)
                out.append({'kind': 'code', 'code': code, 'lang': lang, 'pidx': b['pidx']})
                i = j
                continue
        out.append(b)
        i += 1
    return out


blocks = [b for b in blocks if not (b['kind'] == 'p' and not clean_text(b['text']) and not b['imgs'])]
blocks = merge_code_runs(blocks)

merged = []
i = 0
while i < len(blocks):
    b = blocks[i]
    if b['kind'] == 'tbl':
        rows = [r[:] for r in b['rows']]
        j = i + 1
        while j < len(blocks) and blocks[j]['kind'] == 'tbl':
            r2 = blocks[j]['rows']
            if r2 and rows and max(len(x) for x in r2) == max(len(x) for x in rows):
                rows += [r[:] for r in r2]
                j += 1
            else:
                break
        merged.append({'kind': 'tbl', 'tidx': b['tidx'], 'rows': rows})
        i = j
    else:
        merged.append(b)
        i += 1
blocks = merged
blocks = [b for b in blocks if not (b['kind'] == 'p' and not clean_text(b['text']) and not b['imgs'])]

SKIP_CONTEXT = ('PDF获取下载', 'AI 项目介绍')


def keep_image(name, ctx):
    if name not in media_info:
        return False
    size, w, h, hh, data = media_info[name]
    if size < 800:
        return False
    if min(w, h) <= 40:
        return False
    if max(w, h) / max(1, min(w, h)) >= 15:
        return False
    if any(s in ctx for s in SKIP_CONTEXT):
        return False
    return True


files = {c: {'lines': [], 'used_heads': set(), 'imgs': []} for c in CATS}
cur_cat = 11
cur_ctx = ''
seen_img = {}


def emit(c, line=''):
    files[c]['lines'].append(line)


def normalize_heading(t):
    t = fix_ocr(t)
    t = re.sub(r'(?<=[㐀-鿿])\s+(?=[㐀-鿿])', '', t)
    t = re.sub(r'(?<=[㐀-鿿])(?=[A-Za-z0-9])', ' ', t)
    t = re.sub(r'(?<=[A-Za-z0-9])(?=[㐀-鿿])', ' ', t)
    t = re.sub(r'\s+（', '（', t)
    t = re.sub(r'（\s+', '（', t)
    t = re.sub(r'\s+）', '）', t)
    t = re.sub(r'\s{2,}', ' ', t)
    return t.strip()


def add_heading(c, text, level, kind):
    text = normalize_heading(text)
    if not text:
        return
    used = files[c]['used_heads']
    st = files[c]['head_stack']
    while st and st[-1][0] >= level:
        st.pop()
    parent = st[-1][1] if st else ''
    base = text
    if base in used:
        if parent and parent != base:
            text = parent + ' · ' + base
        if text in used:
            k = 2
            while f'{text}（{k}）' in used:
                k += 1
            text = f'{text}（{k}）'
    used.add(text)
    st.append((level, text, kind))
    emit(c, '#' * level + ' ' + text)
    emit(c, '')


for c, (fname, title, link, footer, summary) in CATS.items():
    files[c]['head_stack'] = []
    emit(c, f'# {title}')
    emit(c, '')
    emit(c, f'> 本笔记整理自八股文题库的「{summary}」部分，保留原题表述与原文顺序。跨模块主笔记：{link}。')
    emit(c, '')

for b in blocks:
    if b['kind'] == 'p':
        pidx = b['pidx']
        newcat = cat_for(pidx)
        if newcat != cur_cat:
            cur_cat = newcat
            files[cur_cat]['head_stack'] = []
        raw = clean_text(b['text'])
        if pidx in INSERTS:
            for txt, lv in INSERTS[pidx]:
                kind = 'h24' if lv == 2 else ('h21' if lv == 3 else 'h18')
                if txt in H21_INSERTS:
                    kind = 'h21'
                add_heading(cur_cat, txt, lv, kind)
                cur_ctx = txt
        if b['size'] in (24.0, 21.0, 18.0) and raw:
            if pidx in OVERRIDES:
                txt, lv, kind = OVERRIDES[pidx]
                add_heading(cur_cat, txt, lv, kind)
                cur_ctx = txt
            else:
                st = files[cur_cat]['head_stack']
                parent24 = None
                parent21 = None
                for lv, t, kd in reversed(st):
                    if kd == 'h24':
                        parent24 = t
                        break
                for lv, t, kd in reversed(st):
                    if kd == 'h21':
                        parent21 = t
                        break
                skip = False
                if b['size'] == 24.0:
                    lv = 2
                    kind = 'h24'
                elif b['size'] == 21.0:
                    kind = 'h21'
                    if raw == parent24 or raw == parent21:
                        skip = True
                        lv = 3
                    elif parent24 and re.sub(r'\s+', '', raw) not in H2_RESET_N:
                        lv = 3
                    else:
                        lv = 2
                        if re.sub(r'\s+', '', raw) in {re.sub(r'\s+', '', x) for x in H24_PROMOTE}:
                            kind = 'h24'
                else:
                    kind = 'h18'
                    has_h3_parent = any(lv2 == 3 and kd == 'h21' for lv2, t2, kd in st)
                    if has_h3_parent:
                        lv = 4
                    elif parent24 or parent21:
                        lv = 3
                    else:
                        lv = 3
                if not skip:
                    add_heading(cur_cat, raw, lv, kind)
                    cur_ctx = raw
            continue
        if 7393 <= pidx <= 7733:
            if raw:
                cat_label = re.fullmatch(r'(JavaSE|JUC|JVM|MySQL|Redis|Kafka|Spring|Spring 框架|计算机网络|操作系统)\s*\((重点|扩展)\)', raw)
                if cat_label or raw in {'分布式', '数据结构与算法', '设计模式', '场景题', '分库分表', '智力题', 'AI&大模型'}:
                    add_heading(cur_cat, raw, 4, 'h18')
                else:
                    for part in re.split(r'(?<=？)\s*', raw):
                        if part.strip():
                            emit(cur_cat, '- ' + part.strip())
            continue
        if raw:
            if raw in ('-', '—', '·', '●', '○', '■'):
                continue
            lp = listify(raw)
            if lp:
                if lp.strip() not in ('-', '  -', '    -'):
                    emit(cur_cat, lp)
            elif code_para(raw):
                lang = code_lang(raw)
                emit(cur_cat, '```' + lang)
                emit(cur_cat, raw)
                emit(cur_cat, '```')
                emit(cur_cat, '')
            elif is_question(raw):
                emit(cur_cat, '**' + raw + '**')
                emit(cur_cat, '')
            elif is_label(raw):
                emit(cur_cat, '**' + raw + '**')
                emit(cur_cat, '')
            else:
                emit(cur_cat, raw)
                emit(cur_cat, '')
        for name in b['imgs']:
            if not keep_image(name, cur_ctx):
                continue
            size, w, h, hh, data = media_info[name]
            if hh in seen_img:
                continue
            seen_img[hh] = True
            fname = CATS[cur_cat][0]
            dest = os.path.join(IMGROOT, fname)
            os.makedirs(dest, exist_ok=True)
            ext = os.path.splitext(name)[1] or '.png'
            outname = hh[:12] + ext
            outpath = os.path.join(dest, outname)
            with open(outpath, 'wb') as f:
                f.write(data)
            alt = re.sub(r'[\[\]|]', '', cur_ctx)[:40] or 'image'
            emit(cur_cat, f'![{alt}](file:///D:/Java/data/八股文/{fname}/{outname})')
            emit(cur_cat, '')
            files[cur_cat]['imgs'].append(outpath)
    elif b['kind'] == 'code':
        emit(cur_cat, '```' + b['lang'])
        emit(cur_cat, b['code'])
        emit(cur_cat, '```')
        emit(cur_cat, '')
    else:
        lines = render_table(b['rows'], cur_ctx)
        for l in lines:
            emit(cur_cat, l)
        if lines:
            emit(cur_cat, '')

for c, (fname, title, link, footer, summary) in CATS.items():
    emit(c, '---')
    emit(c, '')
    emit(c, f'> 📎 **相关笔记**：{footer}')
    emit(c, '')


def postprocess(lines):
    changed = True
    while changed:
        changed = False
        out = []
        i = 0
        while i < len(lines):
            l = lines[i]
            if re.match(r'^#{2,4} ', l):
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j >= len(lines):
                    i += 1
                    continue
                nxt = lines[j]
                m = re.match(r'^(#{2,4}) ', nxt)
                if m and len(m.group(1)) <= len(re.match(r'^(#{2,4}) ', l).group(1)):
                    i += 1
                    changed = True
                    continue
            out.append(l)
            i += 1
        lines = out
    out = []
    blank = 0
    for l in lines:
        if not l.strip():
            blank += 1
            if blank <= 1:
                out.append('')
        else:
            blank = 0
            out.append(l)
    # ensure a blank line before headings and after list blocks
    out2 = []
    for l in out:
        if l.strip():
            prev = out2[-1] if out2 else ''
            if re.match(r'^#{2,4} ', l) and prev.strip():
                out2.append('')
            elif prev.startswith(('- ', '  - ', '    - ')) and not l.startswith(('- ', '  - ', '    - ')):
                out2.append('')
            elif l.startswith('```') and prev.strip():
                out2.append('')
        out2.append(l)
    out = out2
    out2 = []
    blank = 0
    for l in out:
        if not l.strip():
            blank += 1
            if blank <= 1:
                out2.append('')
        else:
            blank = 0
            out2.append(l)
    out = out2
    while out and not out[-1].strip():
        out.pop()
    return out


for c in CATS:
    if 'head_stack' in files[c]:
        del files[c]['head_stack']
    files[c]['lines'] = postprocess(files[c]['lines'])
    path = os.path.join(OUT, CATS[c][0] + '.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(files[c]['lines']).rstrip() + '\n')
    print(CATS[c][0], len(files[c]['lines']), 'lines', len(files[c]['imgs']), 'imgs')

idx = []
idx.append('# 八股文 知识体系')
idx.append('')
idx.append('> 本索引汇总八股文题库的 11 个专题，按主题拆分并保留原题表述；图片统一外置到 `D:\\Java\\data\\八股文`。')
idx.append('')
idx.append('| 笔记 | 内容摘要 |')
idx.append('| --- | --- |')
for c in sorted(CATS):
    fname, title, link, footer, summary = CATS[c]
    idx.append(f'| [[八股文/{fname}|{fname}]] | {summary} |')
idx.append('')
idx.append('---')
idx.append('')
idx.append('> 📎 [[JVM/JVM 索引|JVM]] · [[JUC/JUC 索引|JUC]] · [[MySQL/MySQL 索引|MySQL]] · [[Redis/Redis 索引|Redis]] · [[面试/面试 索引|面试]] · [[检索/检索中心|检索中心]]')
open(os.path.join(OUT, '八股文 索引.md'), 'w', encoding='utf-8').write('\n'.join(idx) + '\n')
print('index written')