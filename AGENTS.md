# AGENTS.md — RAG Agent 系统 AI 索引地图

> **项目状态**：开发中。本文件是 AI 智能体的入口，一切详细内容请跳转至对应子文档。

---

## 🧭 快速定位

| 问题 | 去这里 |
|------|--------|
| 项目整体架构是什么？ | `docs/architecture.md` + `docs/project-design-init.md` |
| 技术栈与核心依赖？ | `docs/architecture.md` §技术栈 |
| 某个模块的职责与接口？ | `docs/modules/{module-name}.md` |
| API 接口定义？ | `docs/modules/api.md` |
| 数据模型与表结构？ | `docs/schema/` |
| 编码规范、命名约定？ | `docs/conventions.md` |
| 关键设计决策为什么这么做？ | `docs/adr/` |
| 当前在做什么需求？ | `docs/roadmap/current.md` |
| 任务卡怎么写？ | `tasks/_template.md` |
| 如何维护知识库？ | `docs/knowledge-maintenance.md` |
| 原始架构设计方案 | `docs/project-design-init.md`（不可修改，只读参考） |

---

## 🤖 可用工具与命令

> ⚠️ 若命令无法运行，必须向用户确认环境是否已就绪，不得擅自安装或修改系统环境。

| 用途 | 命令 |
|------|------|
| 安装依赖 | `pip install -e ".[dev]"` 或 `poetry install` |
| 运行开发服务器 | `uvicorn src.rag_agent.main:app --reload` |
| 启动基础设施 | `docker compose up -d` |
| 运行测试 | `pytest` |
| 运行 Lint | `ruff check src/ tests/` |
| 运行类型检查 | `mypy src/` |
| 数据库迁移 | `alembic upgrade head` |
| 生成迁移 | `alembic revision --autogenerate -m "..."` |

---

## ⚠️ 铁律（优先级最高，不可违反）

1. **设计文档只读**：`docs/project-design-init.md` 是原始设计方案，AI 不得修改。任何架构偏离必须在 `docs/adr/` 中记录为新的 ADR。
2. **先读后写**：修改任何模块前，必须先阅读 `docs/modules/` 对应文档和 `docs/conventions.md`。
3. **禁止猜测**：信息不足时必须向用户确认或声明不确定性，严禁编造 API、配置值或依赖版本。
4. **测试同步**：功能实现后必须补充测试，至少覆盖 Happy Path 和主要错误路径。
5. **文档更新**：任何功能变更后，必须更新受影响模块文档的"修改历史"表格。
6. **禁止直接操作主分支**：涉及 Git 操作时，必须使用 feature 分支。
7. **环境安全**：不得修改 `.env`、`.env.local` 等环境配置文件，除非用户明确要求。
8. **兼容性优先探索**：遇到版本/依赖兼容性问题时，禁止直接降级或删除功能。必须先主动探索上游/下游的版本适配方案（如更换分支、调整大版本号等）。只有在穷尽方案仍不可行或需大幅改动架构时，才可向用户确认后进行降级或替换。

---

## 🔄 工作流提示

```
领取任务 → 阅读 docs/roadmap/current.md
         → 阅读 docs/modules/ 相关模块文档
         → 阅读 docs/conventions.md
         → 实现代码
         → 编写/运行测试
         → 更新模块文档"修改历史"
         → 若架构变更 → 产出 ADR
```
