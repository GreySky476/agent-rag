# 当前需求

> **指引**：在此记录当前 Epic / Story 及对应的目标。任务完成后划掉或删除。

---

## 当前 Epic：项目初始化与基础设施搭建

### 目标
根据 `docs/project-design-init.md` 的架构设计，完成项目骨架搭建，使系统具备最基本的运行能力。

### Story 列表

| # | Story | 状态 | 依赖 |
|---|-------|------|------|
| 1 | 创建 pyproject.toml 与项目依赖声明 | ✅ 完成 | — |
| 2 | 实现 `config.py`（pydantic-settings） | ✅ 完成 | #1 |
| 3 | 实现 `infrastructure/db.py`（SQLAlchemy async engine） | ✅ 完成 | #2 |
| 4 | 实现 `domain/models.py`（4 个 ORM 模型） | ✅ 完成 | #3 |
| 5 | 实现 `domain/schemas.py` + `enums.py` | ✅ 完成 | — |
| 6 | 实现 `api/deps.py` + FastAPI 应用骨架 | ✅ 完成 | #2, #3 |
| 7 | 搭建测试框架（pytest + conftest） | ✅ 完成 | #1 |
| 8 | 编写 docker-compose.yml（PG+AGE+Redis+MinIO） | ✅ 完成 | — |

---

> **使用说明**：新需求到来时，替换此文件内容。将 Story 列表映射到 `tasks/` 目录下的具体任务卡。
