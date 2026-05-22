# RAG Agent 系统架构文档（Python · LightRAG · PostgreSQL · 精简版）

**技术栈**：Python 3.11+ · LangChain · FastAPI · PostgreSQL (pgvector + AGE) · Redis · LightRAG

---

## 1. 设计原则

- **LightRAG 统一检索**：实体关系、语义搜索、社区摘要均由 LightRAG 提供，不再单独维护块摘要向量库。
- **文件分级控成本**：仅高价值文档（L3）构建完整知识图谱，L2 轻度提取，L1 仅存储元数据。
- **增量哈希更新**：基于 SHA-256 的增量索引，仅处理变更内容。
- **Agent 决策反思**：LLM 自主选择工具（SQL、LightRAG 查询、Python 计算），反思完备性，不猜测。

---

## 2. 项目结构

```text
rag-agent/
├── pyproject.toml
├── docker-compose.yml // PG+AGE, Redis, Sandbox
├── src/
│ └── rag_agent/
│ ├── main.py
│ ├── config.py
│ ├── api/
│ │ ├── deps.py
│ │ └── routes/
│ │ ├── agent.py
│ │ └── documents.py
│ ├── domain/
│ │ ├── models.py // SQLAlchemy ORM
│ │ ├── schemas.py
│ │ └── enums.py
│ ├── infrastructure/
│ │ ├── db.py
│ │ ├── lightrag.py // LightRAG 初始化与配置
│ │ ├── cache.py // Redis 语义缓存
│ │ ├── sandbox.py // Docker 沙箱
│ │ ├── llm.py
│ │ └── filestore.py
│ ├── core/
│ │ ├── orchestrator.py
│ │ ├── engine.py
│ │ ├── tools/
│ │ │ ├── sql_tool.py
│ │ │ ├── lightrag_tool.py // 统一检索工具（替代原向量/图谱）
│ │ │ └── python_tool.py
│ │ ├── pipeline.py
│ │ └── graph_service.py // 维护 LightRAG 索引
│ └── utils/
│ ├── hashing.py
│ └── text.py
├── tests/
└── alembic/
```

---

## 3. 存储与职责

| 存储 | 用途 |
|------|------|
| PostgreSQL (业务表) | 文件/块元数据、Agent 执行日志、实体关系（可选） |
| PostgreSQL + pgvector + AGE | LightRAG 完整后端：图、实体、关系、文本块向量 |
| Redis | 语义缓存、会话状态缓存 |
| MinIO / 本地 | 原始文件持久化 |

**无独立 Qdrant 或其他向量数据库**：LightRAG 的向量存储可直接使用 PG 向量（PGVectorStorage），满足中小规模需求。若需更高性能，可将向量后端切换至 Qdrant/Milvus，但不必单独维护。

---

## 4. 数据库表设计（业务 PG）

### 4.1 知识领域
```sql
CREATE TABLE knowledge_domains (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    file_count  INT DEFAULT 0,
    entry_point VARCHAR(500),
    updated_at  TIMESTAMPTZ DEFAULT now()
);
```

### 4.2 文件索引
```sql
CREATE TABLE file_index (
    id            BIGSERIAL PRIMARY KEY,
    domain_id     INT REFERENCES knowledge_domains(id),
    file_path     TEXT UNIQUE NOT NULL,
    title         TEXT,
    entities      JSONB,
    has_tables    BOOLEAN DEFAULT false,
    data_fields   JSONB,
    time_range    DATERANGE,
    hash_checksum VARCHAR(64) NOT NULL,
    importance    VARCHAR(2) DEFAULT 'L1'  -- L1/L2/L3
);
```

### 4.3 块索引（仅元数据，无摘要）
```sql
CREATE TABLE chunk_index (
    id           BIGSERIAL PRIMARY KEY,
    file_id      BIGINT REFERENCES file_index(id) ON DELETE CASCADE,
    chunk_order  INT NOT NULL,
    chunk_type   VARCHAR(20) DEFAULT 'text',
    start_line   INT,
    end_line     INT,
    content_hash VARCHAR(64) NOT NULL,
    UNIQUE(file_id, chunk_order)
);
```

### 4.4 Agent 追踪
```sql
CREATE TABLE agent_traces (
    id           BIGSERIAL PRIMARY KEY,
    session_id   VARCHAR(64) NOT NULL,
    question     TEXT,
    step         INT,
    action       VARCHAR(100),
    tool_input   JSONB,
    tool_output  JSONB,
    reflection   TEXT,
    final_answer TEXT,
    status       VARCHAR(20) DEFAULT 'running',
    created_at   TIMESTAMPTZ DEFAULT now()
);
```

---

## 5. 核心组件说明
### 5.1 Agent 编排器 (`orchestrator.py`)
- 维护 `AgentState（Pydantic）`：问题、历史记录、已知数据摘要、循环计数。

- 循环 `decide` → `execute` → `reflect`，最多 `max_loops`（默认5）次。

- 记录 `trace` 到 `agent_traces`。

### 5.2 决策引擎 (`engine.py`)
- 结构化输出 `NextAction`（tool_name, tool_args, reasoning）。

- 可用工具：`sql_query`, `lightrag_search`, `python_calc`, `answer`, `give_up`。

- 系统提示词明确禁止猜测，信息缺失时必须调用工具或 `give_up`。

### 5.3 反思引擎 (`engine.py`)
- 评估信息完备性、一致性。

- 硬终止条件：连续两次空结果、工具异常、数据矛盾、超时、达到最大循环。

- 输出：CONTINUE, ANSWER, GIVE_UP。

### 5.4 工具层 (tools/)
|工具|	底层实现|	功能|
| ----------- | ----------- | ----------- |
|`SqlTool`	|SQLAlchemy (只读连接)|	仅允许 SELECT，返回结构化数据|
|`LightRAGTool`	|LightRAG 的查询接口	|统一入口，模式可选 local/global/hybrid，返回实体、关系、文本块、社区摘要|
|`PythonTool`	|Docker 沙箱|	执行计算与数据变换，网络禁用，超时强制终止|

---

## 6. 文档摄取与分级
### 6.1 摄取流程
1.上传文件 → 计算全文 SHA-256 → 查询 file_index，若相同则跳过。

2.分块（RecursiveCharacterTextSplitter, chunk=800, overlap=100）。

3.写入 file_index 和 chunk_index（仅元数据和哈希）。

4.根据 importance 字段：

- L1：不做任何提取。

- L2：调用 LightRAG 的 insert，可配置仅提取实体、跳过社区摘要（降低 LLM 调用）。

- L3：完整的 LightRAG 处理（实体、关系、社区摘要）。

5.原始文件保存至文件存储。

### 6.2 增量更新
- 若文件哈希变化：对比各块 content_hash，仅对变更/新增块重新调用 LightRAG 更新（先删除旧实体后插入新内容）。

- 块顺序变化时，重新分配 chunk_order 并同步 LightRAG 更新。


## 7.配置 (config.py)
```python
class Settings(BaseSettings):
    # LLM
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    temperature: float = 0.1

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/rag_agent"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LightRAG
    lightrag_working_dir: str = "./lightrag_data"
    lightrag_importance_level: str = "L2"  # 默认处理级别

    # Document
    chunk_size: int = 800
    chunk_overlap: int = 100

    # Agent
    max_loops: int = 5
    semantic_cache_threshold: float = 0.92
    cache_ttl: int = 3600

    # Sandbox
    sandbox_image: str = "python:3.11-slim"
    sandbox_timeout: int = 10
```

---

## 8. 注意事项
### 8.1 成本控制
- 文件分级强制执行，避免对所有文档无差别构建图谱。

- 决策和反思使用低价快速模型（如 deepseek-v4-flash），限制 max_tokens。

- LightRAG 的 global 模式查询社区摘要时开销较大，Agent 应仅在宏观问题时使用，并缓存结果。

### 8.2 性能优化
- Redis 语义缓存：相似问题直接返回答案，减少 Agent 循环。

- LightRAG 查询结果缓存（可选）：对同一实体的重复查询可短时缓存。

- 大文件摄入使用后台任务（FastAPI BackgroundTasks 或 Celery）。

### 8.3 数据一致性
- 文档更新在事务中完成业务表写入与 LightRAG 更新（尽最大努力，LightRAG 的图谱更新可能非事务性，需记录补偿日志）。

- 实体去重：LightRAG 内部会基于相似度合并实体，无需额外处理。

### 8.4 安全
- SQL 工具仅允许 SELECT，使用只读数据库用户。

- Python 沙箱隔离：Docker 网络禁用、内存限制、禁止危险模块。

- API 层加入 JWT 或 API Key 认证。

### 8.5 可观测性

- `agent_traces` 记录全流程。

- 使用 `structlog` 结构化日志，记录请求 ID。

- 暴露 `Prometheus` 指标：循环次数、工具成功率、缓存命中率、LightRAG 查询耗时。

### 8.6 LightRAG 配置
- `PostgreSQL` 需安装 `pgvector` 和 `AGE` 扩展。

- 初始化时指定存储后端：`graph_storage="PGGraphStorage"`, `vector_storage="PGVectorStorage"`, `kv_storage="PGKVStorage"`。

- 若未来向量规模扩大，可将 `vector_storage` 切换为 `QdrantVectorStorage`，无需改动 Agent 代码。

---

## 9. 核心流程
### 9.1 文档摄取
1.上传文件 → 计算哈希 → 与 file_index 对比。

2.若未变更 → 跳过。

3.分块 → 每块 LLM 生成摘要、类型识别、表格列提取 → 写入 PG 业务表。

4.根据级别调用 LightRAG insert（L2/L3）。

5.增量更新仅处理变更块。

### 9.2 Agent 查询流程
1.接收问题 → 创建 `AgentState`。

2.**决策**：LLM 根据问题、历史、已知数据选择工具。

- 实体关联问题 → `lightrag_search` (hybrid)

- 需要结构化数据 → `sql_query`

- 需要计算 → `python_calc`

3.**执行**：调用对应工具，返回结构化结果。

4.**反思**：检查信息完备性。

- 缺失 → 回到步骤2

- 矛盾 → 尝试澄清或 give_up

- 完备 → 生成最终答案（含引用来源）

5.记录 agent_traces。

### 8.3 LightRAG + Qdrant 协同示例
问题：“去年华东区核心供应商中，哪些交付延迟率超过5%？”

- 决策 → 调用 `lightrag_search` 查询“华东区核心供应商” → 得到实体列表。

- 反思 → 缺少延迟率 → 调用 `sql_query` 从订单表计算各供应商延迟率。

- 反思 → 需要筛选 >5% → 调用 `python_calc` 做过滤和交集。

- 信息完备 → 最终答案输出。

---

架构精简要点：用 LightRAG 统一替换独立向量索引与图谱查询，保留文件分级作为成本阀门，Agent 决策反思层不变。
