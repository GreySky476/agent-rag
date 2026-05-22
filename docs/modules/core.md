# Core 层

## 模块职责

系统核心业务逻辑，负责 Agent 查询的编排与决策、文档摄取的管道控制、LightRAG 索引的维护，以及四个工具（Schema / SQL / LightRAG / Python 沙箱）的封装。

## 目录结构

```
core/
├── orchestrator.py    # Agent 编排器：创建 AgentState，管理 decide→execute→reflect 循环
├── engine.py          # 决策 & 反思引擎：LLM 驱动，prompt JSON 解析
├── pipeline.py        # 文档摄取管道：分块 → 写入 DB → LightRAG insert（按级别）
├── graph_service.py   # LightRAG 索引维护：增量更新、实体去重
└── tools/
    ├── schema_tool.py   # Schema 查询工具：读取 information_schema 返回表结构
    ├── sql_tool.py      # SQL 查询工具：只读 SELECT，返回结构化数据
    ├── lightrag_tool.py # LightRAG 统一检索工具：local/global/hybrid 模式
    └── python_tool.py   # Python 沙箱工具：安全执行计算与数据变换
```

---

## 对外暴露的接口

### `orchestrator.py` — Agent 编排器

| 接口 | 说明 |
|------|------|
| `run_agent(question: str, session_id: str) -> AgentResult` | 主入口：创建 AgentState，驱动循环 |

**流程** `[现存]`：
1. 创建 `AgentState`（问题、历史、已知数据摘要、循环计数）
2. 循环 `decide` → `execute` → `reflect`，最多 `max_loops`（默认 5）次
3. 记录 `trace` 到 `agent_traces`
4. 返回最终答案或 GIVE_UP

### `engine.py` — 决策 & 反思引擎

| 接口 | 说明 |
|------|------|
| `decide(state: AgentState) -> NextAction` | 根据问题、历史、已知数据选择下一个工具 |
| `reflect(state: AgentState, tool_result) -> ReflectionResult` | 评估信息完备性、一致性 |

**决策规则** `[现存]`：
- 实体关联问题 → `lightrag_search` (hybrid)
- 需要结构化数据 → `sql_query`
- 需要计算 → `python_calc`
- 信息充足 → `answer`
- 无法获取信息 → `give_up`

**反思硬终止条件** `[现存]`：连续两次空结果、工具异常、数据矛盾、超时、达到最大循环。

**反思输出**：CONTINUE / ANSWER / GIVE_UP。

### `pipeline.py` — 文档摄取管道

| 接口 | 说明 |
|------|------|
| `process_document(file_path, importance: ImportanceLevel) -> DocumentResult` | 完整摄取流程 |

**流程** `[现存]`：
1. 计算 SHA-256 → 比对 `file_index`（已存在且未变更则跳过）
2. 分块（RecursiveCharacterTextSplitter, chunk=800, overlap=100）
3. 写入 `file_index` 和 `chunk_index`
4. 根据 importance：L1 跳过，L2 轻提取，L3 完整 LightRAG 处理

### `graph_service.py` — LightRAG 索引维护

| 接口 | 说明 |
|------|------|
| `insert_chunks(chunks, level)` | 将分块插入 LightRAG |
| `update_chunks(file_id, changed_chunks)` | 增量更新：删除旧实体后插入新内容 |
| `delete_file_graph(file_id)` | 删除文件对应的 LightRAG 数据 |

### 工具层 (`tools/`)

| 工具 | 接口 | 底层实现 | 安全约束 |
|------|------|----------|----------|
| `SqlTool` | `execute(sql: str) -> ToolResult` | SQLAlchemy 只读连接 | 仅允许 SELECT `[现存]` |
| `LightRAGTool` | `query(q, mode="hybrid") -> ToolResult` | LightRAG 查询接口 | 模式可选 local/global/hybrid `[现存]` |
| `PythonTool` | `execute(code: str) -> ToolResult` | Docker 沙箱 | 网络禁用、超时 10s、禁止危险模块 `[现存]` |

---

## 依赖模块

- `infrastructure.db` — 数据库会话
- `infrastructure.lightrag` — LightRAG 实例
- `infrastructure.cache` — 语义缓存
- `infrastructure.sandbox` — Python 执行
- `infrastructure.llm` — LLM 客户端
- `domain.models` — ORM 模型
- `domain.schemas` — AgentState、NextAction 等
- `domain.enums` — 枚举

---

## 设计约束

- Agent 系统提示词禁止猜测 `[现存]`
- 决策和反思使用低价快速模型，限制 max_tokens `[现存]`
- LightRAG global 查询结果应缓存 `[现存]`
- 工具层每个工具必须返回结构化 `ToolResult` `[现存]`

---

> **修改历史**
>
> | 日期 | 变更内容 | 作者 |
> |------|----------|------|
> | 2026-05-22 | 初始文档：基于 project-design-init.md §5-§6 规划 | AI Agent |
> | 2026-05-22 | engine.py: 移除 with_structured_output，改用 prompt JSON 解析（DeepSeek v4 不兼容 tool_choice） | AI Agent |
> | 2026-05-22 | 新增 tools/schema_tool.py: 查询 information_schema 返回表结构，Agent 决策前必须先查 schema | AI Agent |
> | 2026-05-22 | orchestrator.py: 加入 schema_query 工具分发；_record_trace 增加事务回滚重试；新增 run_agent_stream SSE 流式接口 | AI Agent |
> | 2026-05-22 | pipeline.py: 增加中文日志；修复 session.get 主键查询 bug | AI Agent |
