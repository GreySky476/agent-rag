# Infrastructure 层

## 模块职责

提供底层技术基础设施的初始化与连接管理，包括数据库、LightRAG、Redis 缓存、LLM 客户端、Docker 沙箱和文件存储。不包含业务逻辑。

## 目录结构

```
infrastructure/
├── db.py         # SQLAlchemy async engine + session 工厂
├── lightrag.py   # LightRAG 初始化与配置
├── cache.py      # Redis 语义缓存（相似问题匹配）
├── sandbox.py    # Docker 沙箱（Python 代码执行）
├── llm.py        # LLM 客户端（OpenAI 兼容接口）
└── filestore.py  # 文件存储（MinIO / 本地）
```

## 对外暴露的接口

### `db.py` — 数据库连接

| 接口 | 说明 |
|------|------|
| `get_async_session()` | 返回 `AsyncSession`，用于 FastAPI Depends |
| `init_db()` | 创建表（开发用，生产用 Alembic） |

**约束**：`[现存]` Agent 使用的 SQL 连接必须是只读用户，仅允许 SELECT。

### `lightrag.py` — LightRAG 配置

| 接口 | 说明 |
|------|------|
| `get_lightrag_instance()` | 返回配置好的 LightRAG 实例 |
| `LightRAGConfig` | LightRAG 初始化参数（存储后端、嵌入模型、工作目录） |

**存储后端** `[现存]`：PGraphStorage + PGVectorStorage + PGKVStorage。

### `cache.py` — Redis 语义缓存

| 接口 | 说明 |
|------|------|
| `semantic_lookup(question: str) -> Optional[str]` | 查找相似问题，返回缓存答案 |
| `semantic_store(question: str, answer: str)` | 存入问答对 |
| 配置项 | `semantic_cache_threshold` (默认 0.92), `cache_ttl` (默认 3600s) `[现存]` |

### `sandbox.py` — Docker 沙箱

| 接口 | 说明 |
|------|------|
| `execute_python(code: str, timeout: int) -> str` | 在 Docker 容器中执行 Python 代码并返回输出 |

**安全约束** `[现存]`：网络禁用、内存限制、超时强制终止（默认 10s）、禁止危险模块（os.system, subprocess 等）。

### `llm.py` — LLM 客户端

| 接口 | 说明 |
|------|------|
| `get_llm()` | 返回 LangChain `ChatOpenAI` 实例 |
| `get_embedding_model()` | 返回嵌入模型实例 |

**配置** `[现存]`：默认模型 `gpt-4o-mini`，嵌入模型 `text-embedding-3-small`，temperature 默认 0.1。

### `filestore.py` — 文件存储

| 接口 | 说明 |
|------|------|
| `upload_file(source_path, dest_key) -> str` | 上传到存储，返回访问路径 |
| `get_file(key) -> bytes` | 获取文件内容 |
| `delete_file(key)` | 删除文件 |

---

## 依赖模块

- `domain.models` — 仅 `db.py` 需要引用以注册 ORM 模型
- 外部库：SQLAlchemy, LightRAG, redis-py, docker-py, openai, boto3

---

## 设计约束

- 基础设施层不引用 Core 层或 API 层 `[建议]`
- 所有连接管理使用 context manager / async context manager `[建议]`
- 敏感配置（API Key、密码）从 `config.py`（环境变量）读取，不得硬编码 `[现存]`

---

> **修改历史**
>
> | 日期 | 变更内容 | 作者 |
> |------|----------|------|
> | 2026-05-22 | 初始文档：基于 project-design-init.md §3-§7 规划 | AI Agent |
> | 2026-05-22 | lightrag.py: LLM 改用 openai_complete_if_cache；embedding 改用 openai_embed.func + partial；新增 PG 环境变量设置；新增 async initialize_storages | AI Agent |
> | 2026-05-22 | email.py → lightrag.py 和 pipeline.py 同步，日志用 rag_agent logger | AI Agent |
