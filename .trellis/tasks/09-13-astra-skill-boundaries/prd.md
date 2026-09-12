# 精简 Astra 工作流与 Skill 冲突

## Goal
落实用户批准的十项静态审查建议，保留主动 Trellis/Grill、最小验证、证据真实性和 Git 授权。

## Requirements
全局模板与安装副本、项目 AGENTS、Trellis workflow；using-superpowers、brainstorming、verification-before-completion、Graphify、Grill、diagnosing-bugs、OpenSpec，及直接矛盾的交接说明。只改规则文档，不改 helper 算法、MCP、hooks 或业务代码。

补充对齐项目级规则：消除复杂任务重复建 Task 确认、固定 commit、过宽 GitNexus 重命名门禁；同步优化 EGM 模板和现有 `AGENTS-egm.md`，保留 EGM 数据库交付、Gitee 主远端和按影响验证约束。

## Authorization
用户在本会话明确批准十项建议及同步安装文件；本次建任务、文档实施与针对性检查属已批准范围。不 commit/push，不归档。

## Acceptance Criteria
- [x] 十项建议落地，保持 Trellis 唯一生命周期。
- [x] 安装文件变更有备份，源码与对应安装文件一致。
- [x] 针对性规则/格式检查通过，实际验证边界如实记录。

## Validation
文档级修改；核对触发、授权、输出路径、证据复用；运行现有模板相关测试和 workflow 状态解析相关测试，不执行全仓测试。最终 quality 使用显式范围命令。

## Requirement review
已用 Grill 审查：沿用前一轮明确建议，无新的业务或高风险未决项，无需再次访谈。
