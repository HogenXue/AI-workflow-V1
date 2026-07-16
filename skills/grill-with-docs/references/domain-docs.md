# 领域文档规则

本规则改编自 Matt Pocock `domain-modeling`，并把其默认知识文件收编到 Trellis spec。

## .trellis/spec/domain/

默认在 `.trellis/spec/domain/index.md` 保存项目特有的领域词汇。术语一旦确认就即时更新；
不得写实现细节、需求、验收标准、计划或 task 状态。已有更细的领域文件时，遵守其结构，
不要复制同一术语。

```markdown
# <领域名称>

<一到两句领域说明>

## Language

**<规范术语>**：
<一到两句定义>
_Avoid_: <应避免的同义词>
```

- 选择一个规范术语，并列出应避免的同义词。
- 定义是什么，不描述代码如何实现。
- 通用编程词汇不进入领域术语表。
- 多领域项目可在该目录下按上下文拆分文件，并由 `index.md` 链接；不清楚归属时询问用户。

## .trellis/spec/decisions/

只有同时满足以下条件才建议 ADR：

1. 决定难以逆转，未来更改成本显著；
2. 缺少上下文时，未来维护者会对当前选择感到意外；
3. 存在真实替代方案，并经过明确权衡。

决定记录使用 `.trellis/spec/decisions/NNNN-slug.md` 顺序编号，正文保持精简：

```markdown
# <决定标题>

<一到三句说明背景、决定和原因。>
```

需要时才增加状态、备选方案或后果。普通实现细节、易逆转选择和会话记录不写 ADR。

## 与 Trellis 的关系

- Trellis PRD：需求、范围、场景、验收和未决项的唯一来源。
- Trellis Design/Plan：技术设计和实施步骤的唯一来源。
- `.trellis/spec/domain/`：领域词汇。
- `.trellis/spec/decisions/`：持久、难以逆转的决定及原因。

若内容同时像需求和领域知识，先写 Trellis PRD；只有稳定术语或满足三项条件的决定才同步到
领域文档。
