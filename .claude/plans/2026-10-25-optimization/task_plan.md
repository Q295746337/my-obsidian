# Task Plan: 2026-10-25 知识库优化（P1 + MySQL 细节）

## Goal

按用户确认的范围执行：

- P1-1：拆分 `SpringBoot2/03-开发实用篇.md`（250KB / 5432 行）
- P1-2：拆分 `SpringBoot2/01-基础篇.md`（147KB / 3409 行）
- P1-3：补 14 个空章节（MySQL 运维 6、MySQL 进阶 4、Redis 高级 2、SSM 2）
- P2：MySQL 细节收口（索引页 `—` 描述、章号与子节号不一致、事务 SQL 一行多句/尾随空格）

不做：P0 图片瘦身、P3 空目录清理、归档移动、外链图片。

## Phases

- [x] Phase 1：基线盘点 + 原始 docx 恢复 + MySQL 细节清单
- [x] Phase 2：拆分 SpringBoot2/03
- [x] Phase 3：拆分 SpringBoot2/01
- [x] Phase 4：补 14 个空章节
- [x] Phase 5：MySQL 细节收口
- [x] Phase 6：全库验收 + 更新索引/图谱 + 交付报告

## Status

**Completed** — 交付报告：[[源资料补全与JUC拆分报告-2026-10-25]]

## Constraints

- 不触碰 `JUC/`、`JVM/` 文件夹。
- 源 docx 从 git 历史恢复，不凭记忆补写。
- 每阶段完成后更新本文件和 `notes.md`。
- 拆分后必须更新 SpringBoot2 索引、相关 wikilink、图片引用和页脚。
- 最终复查：0 缺 H1、0 多 H1、0 空页脚、0 断链、0 缺图、0 未引用图片。

## Errors / Decisions

- 2026-10-25：用户确认 P0 跳过、P1 三项执行、P2 仅 MySQL 细节、P3 全部跳过。