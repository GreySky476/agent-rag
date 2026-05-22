# Domain 层

## 模块职责

定义项目的领域模型，包括 SQLAlchemy ORM 模型（数据库表映射）、Pydantic 数据校验 Schema，以及领域枚举常量。不包含业务逻辑。

## 目录结构

```
domain/
├── models.py   # SQLAlchemy ORM 模型
├── schemas.py  # Pydantic 请求/响应/内部传输 Schema
└── enums.py    # 领域枚举
```

## 对外暴露的接口

### ORM 模型 (`models.py`)

| 模型类 | 表名 | 说明 |
|--------|------|------|
| `KnowledgeDomain` | `knowledge_domains` | 知识领域分类 |
| `FileIndex` | `file_index` | 文件索引元数据 |
| `ChunkIndex` | `chunk_index` | 文件分块元数据 |
| `AgentTrace` | `agent_traces` | Agent 执行追踪 |

### Pydantic Schema (`schemas.py`)

| Schema 类别 | 示例 | 说明 |
|-------------|------|------|
| 请求体 | `AgentQueryRequest`, `DocumentUploadRequest` | API 输入校验 |
| 响应体 | `AgentQueryResponse`, `DocumentResponse` | API 输出序列化 |
| 内部传输 | `AgentState`, `NextAction`, `ToolResult` | Core 层间数据传递 |

### 枚举 (`enums.py`)

| 枚举 | 值 | 说明 |
|------|-----|------|
| `ImportanceLevel` | L1, L2, L3 | 文件重要性分级 |
| `ChunkType` | text, table, code | 块类型 |
| `AgentStatus` | running, completed, failed | Agent 执行状态 |
| `AgentAction` | sql_query, lightrag_search, python_calc, answer, give_up | Agent 可用操作 |
| `ReflectionResult` | CONTINUE, ANSWER, GIVE_UP | 反思结果 |

---

## 依赖模块

- 无下游依赖（Domain 层是最底层，不依赖项目其他模块）
- 依赖 SQLAlchemy、Pydantic 两个库

---

## 设计约束

- ORM 模型仅定义字段和关系，不包含业务逻辑 `[建议]`
- Schema 按用途组织：Request / Response / Internal `[建议]`
- 枚举值必须在代码中集中定义，禁止魔数/魔字符串 `[建议]`

---

> **修改历史**
>
> | 日期 | 变更内容 | 作者 |
> |------|----------|------|
> | 2026-05-22 | 初始文档：基于 project-design-init.md §4 和 §5 规划 | AI Agent |
> | 2026-05-22 | AgentAction 枚举新增 SCHEMA_QUERY | AI Agent |
> | 2026-05-22 | AgentTrace 模型新增 title、updated_at 字段；FileIndex 新增 created_at 字段 | AI Agent |
> | 2026-05-22 | 所有 str/Enum 改为 StrEnum | AI Agent |
> | 2026-05-22 | schemas 新增 ConversationSummary/Detail/Update, KnowledgeDomainCreate/Response, StatsResponse | AI Agent |
