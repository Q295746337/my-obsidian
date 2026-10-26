import os
import re
from collections import OrderedDict

V = r'D:\Java\Obisidian笔记'

# note -> list of (phrase, target note stem)
M = {
'JavaSE/01-Java基础入门.md': [('后续','JavaSE/02-运算符与流程控制'),('后续','JavaSE/05-面向对象编程'),('练习','JavaSE/04-基础综合练习')],
'JavaSE/04-基础综合练习.md': [('前置','JavaSE/01-Java基础入门'),('前置','JavaSE/02-运算符与流程控制'),('后续','JavaSE/06-面向对象综合练习')],
'JavaSE/06-面向对象综合练习.md': [('前置','JavaSE/05-面向对象编程'),('前置','JavaSE/04-基础综合练习'),('延伸','JavaSE/10-集合框架')],
'JavaSE/09-常用API/09-时间与包装类.md': [('对比','JavaSE/09-常用API/09-Math与System'),('后续','JavaSE/10-集合框架'),('后续','JavaSE/07-字符串与常用API')],
'JavaSE/09-常用API/09-算法与Lambda.md': [('前置','JavaSE/05-面向对象编程'),('应用','JavaSE/10-集合框架'),('对比','JavaSE/09-常用API/09-时间与包装类')],
'JavaSE/11-IO流/11-字节与字符流.md': [('相关','JavaSE/11-IO流/11-异常与File'),('相关','JavaSE/11-IO流/11-其他流'),('应用','JavaSE/13-网络编程')],
'JavaWeb/01-Web前端/03-Ajax与Vue.md': [('后续','JavaWeb/04-SpringBoot请求响应'),('相关','JavaWeb/01-Web前端/04-Element'),('应用','JavaWeb/05-案例与登录/05-案例-员工管理(上)')],
'JavaWeb/01-Web前端/04-Element.md': [('前置','JavaWeb/01-Web前端/03-Ajax与Vue'),('应用','JavaWeb/05-案例与登录/05-案例-员工管理(上)')],
'JavaWeb/05-案例与登录/05-案例-员工管理(上).md': [('后续','JavaWeb/05-案例与登录/05-案例-员工管理(下)'),('依赖','JavaWeb/02-数据库与持久层'),('依赖','JavaWeb/04-SpringBoot请求响应')],
'JavaWeb/05-案例与登录/05-案例-员工管理(下).md': [('前置','JavaWeb/05-案例与登录/05-案例-员工管理(上)'),('前置','JavaWeb/02-数据库与持久层'),('后续','JavaWeb/05-案例与登录/05-登录认证')],
'MySQL/MySQL-基础篇.md': [('后续','MySQL/进阶篇/02-索引'),('后续','MySQL/进阶篇/06-InnoDB引擎'),('运维','MySQL/MySQL-运维篇')],
'MySQL/MySQL-运维篇.md': [('前置','MySQL/MySQL-基础篇'),('相关','MySQL/进阶篇/07-MySQL管理'),('相关','MySQL/进阶篇/03-SQL优化')],
'MySQL/进阶篇/01-存储引擎.md': [('后续','MySQL/进阶篇/06-InnoDB引擎'),('后续','MySQL/进阶篇/02-索引'),('对比','MySQL/进阶篇/05-锁')],
'MySQL/进阶篇/03-SQL优化.md': [('前置','MySQL/进阶篇/02-索引'),('前置','MySQL/进阶篇/06-InnoDB引擎'),('相关','MySQL/进阶篇/04-视图与存储过程')],
'MySQL/进阶篇/04-视图与存储过程.md': [('前置','MySQL/MySQL-基础篇'),('相关','MySQL/进阶篇/03-SQL优化'),('相关','MySQL/进阶篇/05-锁')],
'MySQL/进阶篇/05-锁.md': [('相关','MySQL/进阶篇/06-InnoDB引擎'),('相关','MySQL/进阶篇/01-存储引擎'),('对比','JUC/并发编程原理/03-AQS与锁')],
'MySQL/进阶篇/06-InnoDB引擎.md': [('相关','MySQL/进阶篇/05-锁'),('相关','MySQL/进阶篇/02-索引'),('前置','MySQL/进阶篇/01-存储引擎')],
'MySQL/进阶篇/07-MySQL管理.md': [('前置','MySQL/MySQL-运维篇'),('相关','MySQL/进阶篇/03-SQL优化'),('相关','MySQL/进阶篇/01-存储引擎')],
'Redis/Redis-入门篇.md': [('后续','Redis/实战篇/实战-开篇导读'),('延伸','Redis/高级篇/高级-分布式缓存'),('索引','Redis/Redis 索引')],
'Redis/Redis-原理篇.md': [('后续','Redis/高级篇/高级-分布式缓存'),('后续','Redis/高级篇/高级-集群'),('应用','Redis/实战篇/实战-分布式锁')],
'Redis/实战篇/实战-UV统计.md': [('相关','Redis/实战篇/实战-用户签到'),('相关','Redis/实战篇/实战-好友关注'),('项目','黑马点评/黑马点评 索引')],
'Redis/实战篇/实战-优惠券秒杀.md': [('后续','Redis/实战篇/实战-秒杀优化'),('后续','Redis/实战篇/实战-分布式锁'),('项目','黑马点评/03-秒杀模块')],
'Redis/实战篇/实战-分布式锁-redission.md': [('前置','Redis/实战篇/实战-分布式锁'),('原理','Redis/高级篇/高级-分布式缓存'),('项目','黑马点评/05-项目衍生八股')],
'Redis/实战篇/实战-分布式锁.md': [('实现','Redis/实战篇/实战-分布式锁-redission'),('应用','Redis/实战篇/实战-秒杀优化'),('项目','黑马点评/05-项目衍生八股')],
'Redis/实战篇/实战-商户查询缓存.md': [('延伸','Redis/高级篇/高级-多级缓存'),('项目','黑马点评/02-缓存模块'),('前置','Redis/实战篇/实战-开篇导读')],
'Redis/实战篇/实战-好友关注.md': [('相关','Redis/实战篇/实战-达人探店'),('相关','Redis/实战篇/实战-附近商户'),('对比','Redis/实战篇/实战-UV统计')],
'Redis/实战篇/实战-开篇导读.md': [('后续','Redis/实战篇/实战-短信登录'),('后续','Redis/实战篇/实战-商户查询缓存'),('项目','黑马点评/01-项目介绍与简历')],
'Redis/实战篇/实战-消息队列.md': [('延伸','SpringBoot2/03-开发实用篇/08-整合第三方技术-消息'),('面试','面试/06-消息中间件篇'),('项目','黑马点评/05-项目衍生八股')],
'Redis/实战篇/实战-用户签到.md': [('对比','Redis/实战篇/实战-UV统计'),('相关','Redis/实战篇/实战-好友关注'),('相关','Redis/实战篇/实战-达人探店')],
'Redis/实战篇/实战-短信登录.md': [('前置','Redis/实战篇/实战-开篇导读'),('对比','JavaWeb/05-案例与登录/05-登录认证'),('项目','黑马点评/01-项目介绍与简历')],
'Redis/实战篇/实战-秒杀优化.md': [('前置','Redis/实战篇/实战-优惠券秒杀'),('项目','黑马点评/03-秒杀模块'),('延伸','Redis/实战篇/实战-消息队列')],
'Redis/实战篇/实战-达人探店.md': [('相关','Redis/实战篇/实战-好友关注'),('相关','Redis/实战篇/实战-附近商户'),('对比','Redis/实战篇/实战-UV统计')],
'Redis/实战篇/实战-附近商户.md': [('相关','Redis/实战篇/实战-达人探店'),('相关','Redis/实战篇/实战-好友关注'),('延伸','Redis/高级篇/高级-多级缓存')],
'Redis/高级篇/高级-分布式缓存.md': [('后续','Redis/高级篇/高级-集群'),('应用','Redis/实战篇/实战-商户查询缓存'),('项目','黑马点评/05-项目衍生八股')],
'Redis/高级篇/高级-多级缓存.md': [('应用','Redis/实战篇/实战-商户查询缓存'),('项目','黑马点评/02-缓存模块'),('前置','Redis/高级篇/高级-分布式缓存')],
'Redis/高级篇/高级-最佳实践.md': [('相关','Redis/高级篇/高级-分布式缓存'),('相关','Redis/高级篇/高级-集群'),('索引','Redis/Redis 索引')],
'Redis/高级篇/高级-集群.md': [('前置','Redis/高级篇/高级-分布式缓存'),('相关','Redis/高级篇/高级-最佳实践'),('面试','面试/02-Redis篇')],
'SSM框架/SpringMVC/day02-高级.md': [('前置','SSM框架/SpringMVC/day01-基础'),('对比','SSM框架/Spring框架/day02-AOP'),('应用','JavaWeb/04-SpringBoot请求响应')],
'SSM框架/Spring框架/day02-AOP.md': [('前置','SSM框架/Spring框架/day01-IOC与DI'),('后续','SSM框架/Spring框架/day03-事务'),('应用','JavaWeb/06-SpringBoot事务与AOP')],
'SSM框架/Spring框架/day03-事务.md': [('前置','SSM框架/Spring框架/day02-AOP'),('前置','MySQL/MySQL-基础篇'),('应用','JavaWeb/06-SpringBoot事务与AOP')],
'SpringBoot2/02-运维实用篇.md': [('前置','SpringBoot2/01-基础篇/01-快速上手SpringBoot'),('相关','SpringBoot2/03-开发实用篇/09-监控'),('后续','SpringBoot2/04-原理篇')],
'SpringBoot2/04-原理篇.md': [('前置','SpringBoot2/01-基础篇/02-SpringBoot基础配置'),('前置','SpringBoot2/02-运维实用篇'),('对比','SSM框架/SpringBoot')],
}

# validate
for n in M:
    if not os.path.exists(os.path.join(V, n)):
        print('MISSING NOTE', n)
for pairs in M.values():
    for _, t in pairs:
        if not os.path.exists(os.path.join(V, t + '.md')):
            print('MISSING TARGET', t)

def body_without_footer(text):
    return '\n'.join(l for l in text.splitlines() if '相关笔记' not in l)

def first_h2(lines):
    fence = None
    for i, l in enumerate(lines):
        fm = re.match(r'^\s*(`{3,4}|~{3,4})', l)
        if fm:
            if fence is None:
                fence = fm.group(1)
            elif l.strip().startswith(fence):
                fence = None
            continue
        if fence:
            continue
        if re.match(r'^##\s+', l):
            return i
    return None

added_notes = 0
added_links = 0
skipped = []
for n, pairs in M.items():
    p = os.path.join(V, n)
    text = open(p, encoding='utf-8').read()
    body = body_without_footer(text)
    # drop targets already present in body
    remain = []
    for phrase, t in pairs:
        base = os.path.basename(t)
        if f'[[{t}' in body or f'[[{base}' in body:
            continue
        remain.append((phrase, t))
    if not remain:
        skipped.append((n, 'all-present'))
        continue
    # group by phrase, preserving order
    groups = OrderedDict()
    for phrase, t in remain:
        groups.setdefault(phrase, []).append(t)
    parts = []
    for phrase, ts in groups.items():
        links = ' · '.join(f'[[{t}|{os.path.basename(t)}]]' for t in ts)
        parts.append(f'{phrase}：{links}')
    line = '> ' + '；'.join(parts) + '。'
    lines = text.splitlines()
    idx = first_h2(lines)
    if idx is None:
        # insert before final footer
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].startswith('> 📎'):
                idx = i
                break
        if idx is None:
            idx = len(lines)
    # ensure blank before and after
    block = ['', line, '']
    # avoid triple blank
    while idx > 0 and lines[idx-1].strip() == '':
        idx -= 1
    newlines = lines[:idx] + block + lines[idx:]
    open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(newlines) + '\n')
    added_notes += 1
    added_links += len(remain)

print('notes in map', len(M), 'added_notes', added_notes, 'added_links', added_links, 'skipped', skipped)