# 开发规范与约束

> **说明**：本文档中的标记含义：
> - `[现存]` = 从 `docs/project-design-init.md` 提取的项目既定设计约束
> - `[建议]` = 基于 Python/FastAPI 最佳实践补充的建议规范

---

## 1. 目录结构规范 `[现存]`

```
src/rag_agent/
├── main.py              # FastAPI 应用入口
├── config.py            # 配置（基于 pydantic-settings）
├── api/                 # API 层（路由、依赖注入）
│   ├── deps.py
│   └── routes/
├── domain/              # 领域层（ORM 模型、Pydantic Schema、枚举）
├── infrastructure/      # 基础设施层（DB、缓存、LLM、沙箱、文件存储）
├── core/                # 核心层（编排器、引擎、工具、管道）
└── utils/               # 工具函数（哈希、文本处理）
```

**约束**：新代码必须放入对应层级目录，不得跨层级反向依赖（infrastructure 不可依赖 api）。

---

## 2. Python 编码规范 `[建议]`

### 2.1 格式化
- 使用 **Ruff** 作为 linter 和 formatter
- 行宽：**100** 字符
- 缩进：4 空格，禁止 Tab
- 字符串：优先使用双引号（docstring 用三重双引号）

### 2.2 命名约定
| 类别 | 风格 | 示例 |
|------|------|------|
| 模块文件 | snake_case | `graph_service.py` |
| 类名 | PascalCase | `LightRAGTool` |
| 函数/方法 | snake_case | `decide_action()` |
| 变量 | snake_case | `agent_state` |
| 常量 | UPPER_SNAKE_CASE | `MAX_LOOPS` |
| 私有成员 | 前缀 `_` | `_build_prompt()` |

### 2.3 类型注解 `[建议]`
- 所有公共函数必须有类型注解
- 使用 `from __future__ import annotations`（Python 3.11+ 可省略）
- 复杂类型使用 `TypeAlias` 或 Pydantic 模型
- 配置项应使用 `pydantic-settings` 的 `BaseSettings`

### 2.4 导入顺序 `[建议]`
1. 标准库
2. 第三方库
3. 本地模块

使用 Ruff 自动排序。

---

## 3. FastAPI 规范 `[建议]`

### 3.1 路由设计
- 路由文件放 `api/routes/`，每领域一个文件
- 使用 `APIRouter` 的 `prefix` 和 `tags` 参数
- 路径参数使用 kebab-case：`/api/v1/documents/{document-id}`

### 3.2 响应模型
- 所有端点使用 Pydantic `response_model` 定义返回类型
- 错误响应统一格式：
```python
class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None
```

### 3.3 依赖注入
- 公共依赖（数据库会话、当前用户）统一在 `deps.py` 管理
- 使用 `Depends()` 注入，避免全局变量

---

## 4. 数据层规范 `[现存]`

- **ORM**：SQLAlchemy 2.0+（async 模式）
- **只读安全**：Agent 使用的 SQL 连接必须是只读用户，仅允许 SELECT `[现存]`
- **事务**：文档更新在事务中完成业务表写入与 LightRAG 更新 `[现存]`
- **迁移**：使用 Alembic，每次模型变更都必须生成新迁移
- **表命名**：snake_case 单数形式（与设计文档一致：`file_index`, `knowledge_domains`）

---

## 5. Agent 与 AI 交互规范 `[现存]`

### 5.1 提示词设计
- 系统提示词必须明确禁止猜测 `[现存]`
- 结构化输出使用 `NextAction` Pydantic 模型 `[现存]`
- 决策引擎每次只返回一个工具调用 `[现存]`

### 5.2 反思规则 `[现存]`
- 硬终止条件：连续两次空结果、工具异常、数据矛盾、超时、达到最大循环 `[现存]`
- 反思输出必须为：CONTINUE / ANSWER / GIVE_UP `[现存]`

### 5.3 工具调用 `[现存]`
- 每个工具必须有结构化输入/输出定义
- 工具失败必须返回明确错误信息，不可静默忽略

---

## 6. 错误处理 `[建议]`

### 6.1 异常层级
```python
class RAGAgentError(Exception): ...          # 基础异常
class ConfigurationError(RAGAgentError): ...  # 配置错误
class DocumentProcessingError(RAGAgentError): ...  # 文档处理错误
class ToolExecutionError(RAGAgentError): ...  # 工具执行错误
class AgentLoopExhaustedError(RAGAgentError): ...  # 循环耗尽
```

### 6.2 日志规范 `[现存]`
- 使用 `structlog` 结构化日志
- 每条日志必须包含 `request_id`（如有）
- 关键节点必须记录：工具调用起止、决策结果、反思结论

---

## 7. 测试规范 `[建议]`

### 7.1 覆盖要求
| 层级 | 框架 | 最低要求 |
|------|------|----------|
| 单元测试 | pytest + pytest-asyncio | 工具函数、模型验证 |
| 集成测试 | pytest + httpx | API 端点、数据库操作 |
| Agent 测试 | pytest + mock LLM | 决策/反思引擎逻辑 |

### 7.2 命名
- 测试文件：`test_{module}.py`
- 测试函数：`test_{功能描述}_{场景}`，如 `test_decide_action_returns_tool_call`

### 7.3 Mock 策略 `[建议]`
- LLM 调用必须 mock，使用固定响应
- 数据库测试使用测试专用 PostgreSQL 实例或 testcontainers
- Redis/LightRAG 操作在测试中 mock

---

## 8. Git 提交规范 `[建议]`

- 使用 Conventional Commits 格式：`type(scope): description`
- 类型：`feat`, `fix`, `refactor`, `test`, `docs`, `chore`
- 示例：`feat(agent): add decision engine with tool selection`
- 禁止在提交中混入无关变更

---

## 9. 环境管理 `[现有]`

- 敏感配置（API Key、数据库密码）通过环境变量注入 `[现存]`
- 本地开发使用 `.env` 文件（不提交到 Git） `[现存]`
- 配置类统一在 `config.py` 中通过 `pydantic-settings` 管理 `[现存]`

---

## 10. 组件状态覆盖 `[建议]`

每个涉及异步操作或数据获取的 UI/API 组件必须覆盖以下状态：

| 状态 | 处理方式 |
|------|----------|
| **Loading** | 返回处理中状态，设置合理超时 |
| **Empty** | 明确返回空结果标记，区分"无数据"与"出错" |
| **Error** | 捕获异常，记录日志，返回结构化错误 |
| **Success** | 返回标准化的成功响应 |

---

> **修改历史**
>
> | 日期 | 变更内容 | 作者 |
> |------|----------|------|
> | 2026-05-22 | 初始文档：从 design-init 提取现有约束，补充 Python/FastAPI 建议规范 | AI Agent |
