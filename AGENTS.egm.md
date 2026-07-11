# EGM 专属规则（V6-EGM）

> 版本：V6-EGM · 叠加于 CodexTamplate `AGENTS.md` V6
> 冲突时以本文为准。EGM 仓库部署：复制为根目录 `Agents.md`。

---

## 项目结构

- `egm_backend`：Spring Boot 微服务后端。
- `egm_vue`：Vue 管理端。
- uni-app：移动端。

---

## 分层架构

```
Controller → Application → Domain → Infrastructure
```

| 层              | 职责                  |
| -------------- | ------------------- |
| Controller     | 接口接入                |
| Application    | 业务流程编排              |
| Domain         | 核心业务规则              |
| Infrastructure | DB / MQ / RPC 等技术实现 |

---

## Skill 默认策略

- 规范驱动变更 → `$openspec`。
- 会话延续与项目记忆 → `$memory`。
- 探索代码、改 symbol 前、提交前 → `$gitnexus`（项目名 **EGM**）。

---

## Git 提交格式

版本号与风格参考 `egm_docs/RELEASE_NOTE.md`：

```md
## 版本号 - YYYY-MM-DD
- 模块路径 -> 功能入口：变更点。
- 具体行为、规则调整或修复说明。
```

---

## 文档

- 目录：`egm_docs/spec/`
- 文件名：`文档名-作者-YYYYMMDD.md`
- 修改须说明原因、影响范围及关联代码。

---

## 服务重启

禁止 Agent 自动启动或重启本地服务。修改后端或前端后，仅在任务结束时提醒用户自行执行：

```bash
# 修改 egm_backend 后
./egm_docs/Shells/auto_startup.sh 2.自动启动全部服务

# 修改 egm_vue 后
./egm_docs/Shells/auto_startup.sh restart-vue
```
