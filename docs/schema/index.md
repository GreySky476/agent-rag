# 数据模型与 Schema

> **原始设计依据**：`docs/project-design-init.md` §4

---

## 1. 数据库表

### 1.1 `knowledge_domains` — 知识领域

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | SERIAL | PK | 自增主键 |
| `name` | VARCHAR(100) | UNIQUE, NOT NULL | 领域名称 |
| `description` | TEXT | NULLABLE | 领域描述 |
| `file_count` | INT | DEFAULT 0 | 关联文件数 |
| `entry_point` | VARCHAR(500) | NULLABLE | 领域入口文件路径 |
| `updated_at` | TIMESTAMPTZ | DEFAULT now() | 最后更新时间 |

### 1.2 `file_index` — 文件索引

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BIGSERIAL | PK | 自增主键 |
| `domain_id` | INT | FK → knowledge_domains(id) | 所属知识领域 |
| `file_path` | TEXT | UNIQUE, NOT NULL | 文件路径 |
| `title` | TEXT | NULLABLE | 文件标题 |
| `entities` | JSONB | NULLABLE | 提取的实体列表 |
| `has_tables` | BOOLEAN | DEFAULT false | 是否含表格 |
| `data_fields` | JSONB | NULLABLE | 数据字段列表 |
| `time_range` | DATERANGE | NULLABLE | 内容时间范围 |
| `hash_checksum` | VARCHAR(64) | NOT NULL | SHA-256 哈希 |
| `importance` | VARCHAR(2) | DEFAULT 'L1' | L1/L2/L3 |

### 1.3 `chunk_index` — 块索引

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BIGSERIAL | PK | 自增主键 |
| `file_id` | BIGINT | FK → file_index(id) ON DELETE CASCADE | 所属文件 |
| `chunk_order` | INT | NOT NULL | 分块顺序 |
| `chunk_type` | VARCHAR(20) | DEFAULT 'text' | text/table/code |
| `start_line` | INT | NULLABLE | 起始行号 |
| `end_line` | INT | NULLABLE | 结束行号 |
| `content_hash` | VARCHAR(64) | NOT NULL | 内容哈希（用于增量检测） |

**唯一约束**：`UNIQUE(file_id, chunk_order)`

### 1.4 `agent_traces` — Agent 追踪

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BIGSERIAL | PK | 自增主键 |
| `session_id` | VARCHAR(64) | NOT NULL | 会话标识 |
| `question` | TEXT | NULLABLE | 原始问题 |
| `step` | INT | NULLABLE | 循环步数 |
| `action` | VARCHAR(100) | NULLABLE | sql_query / lightrag_search / python_calc / answer / give_up |
| `tool_input` | JSONB | NULLABLE | 工具输入参数 |
| `tool_output` | JSONB | NULLABLE | 工具返回结果 |
| `reflection` | TEXT | NULLABLE | 反思结论 |
| `final_answer` | TEXT | NULLABLE | 最终答案 |
| `status` | VARCHAR(20) | DEFAULT 'running' | running / completed / failed |
| `created_at` | TIMESTAMPTZ | DEFAULT now() | 创建时间 |

---

## 2. 实体关系图

```
knowledge_domains 1 ──── N file_index 1 ──── N chunk_index
                                    │
                                    │ (逻辑关联，非 FK)
                                    ▼
                              LightRAG 图谱
                                    │
                                    │ (lightrag 管理)
                                    ▼
                      实体节点 ──── 关系边 ──── 社区

        无 FK 关联：
        agent_traces （独立会话记录）
```

---

## 3. LightRAG 存储结构

LightRAG 使用 PostgreSQL 的内部表空间（由 LightRAG 自动管理）：

| 存储类型 | PostgreSQL 实现 | 内容 |
|----------|-----------------|------|
| 图存储 | PGGraphStorage (AGE) | 实体节点、关系边 |
| 向量存储 | PGVectorStorage (pgvector) | 文本块的向量嵌入 |
| KV 存储 | PGKVStorage | 元数据、社区摘要 |

**注意**：这些表由 LightRAG 框架自动维护，业务代码不直接操作。

---

## 4. Pydantic 内部数据结构（规划）

### AgentState
```python
class AgentState(BaseModel):
    question: str
    session_id: str
    history: list[dict] = []
    known_data: dict = {}
    loop_count: int = 0
    status: AgentStatus = AgentStatus.RUNNING
```

### NextAction
```python
class NextAction(BaseModel):
    tool_name: AgentAction
    tool_args: dict
    reasoning: str
```

### ToolResult
```python
class ToolResult(BaseModel):
    success: bool
    data: Any
    error: str | None = None
    sources: list[str] | None = None
```

---

> **修改历史**
>
> | 日期 | 变更内容 | 作者 |
> |------|----------|------|
> | 2026-05-22 | 初始文档：基于 project-design-init.md §4 表结构 | AI Agent |
