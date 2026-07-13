# Trellis 协作边界

```text
Trellis：需求、场景、验收、task 级 PRD/计划、状态、Journal
        ↓
TDD：RED → GREEN → REFACTOR（测试与实现）
        ↓
Trellis Check：质量、架构、安全与可维护性检查
        ↓
GitNexus：高影响提交的范围复核（低风险使用标准 Git 检查）
```

- TDD 将 Trellis PRD 的验收标准转成可执行测试，不替代需求审查。
- TDD 不创建或更新 Trellis task 状态；将测试证据交给当前 task 的 Journal。
- TDD 是实现方法，不替代 Trellis 状态机；文档、纯配置和无法合理自动化测试的改动使用风险相称的验证。
- 需求有歧义、边界未知或验收不可测试时暂停实现，返回 Grill Me / Trellis planning，而非自行假设。
