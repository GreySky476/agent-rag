# 高层架构设计

> **原始设计依据**：`docs/project-design-init.md`（只读参考）

---

## 1. 架构模式

采用 **分层架构**，严格按职责分离：

```
┌─────────────────────────────┐
│         API 层 (FastAPI)     │  ← 对外 HTTP 接口
├─────────────────────────────┤
│         Core 层              │  ← Agent 编排、决策/反思引擎、工具调用
├─────────────────────────────┤
│        Domain 层             │  ← 领域模型（ORM + Pydantic Schema）
├─────────────────────────────┤
│     Infrastructure 层        │  ← 数据库、缓存、LLM、沙箱、LightRAG
└─────────────────────────────┘
```

**依赖方向**：API → Core → Domain → Infrastructure（上层可依赖下层，反之不可）

---

## 2. 技术栈

| 组件 | 选型 | 理由 |
|------|------|------|
| Web 框架 | FastAPI | 原生异步、自动 OpenAPI 文档、类型安全 |
| ORM | SQLAlchemy 2.0+ async | Python 生态最成熟的异步 ORM |
| RAG 引擎 | LightRAG | 统一图+向量+摘要检索，减少组件数量 |
| 数据库 | PostgreSQL + pgvector + AGE | 单库承载业务数据、向量和图数据 |
| 缓存 | Redis | 语义缓存、会话状态 |
| AI 编排 | LangChain | 工具调用抽象 |
| 沙箱 | Docker | 隔离 Python 代码执行 |
| 文件存储 | MinIO | S3 兼容，可切换本地存储 |
| 监控 | structlog + Prometheus | 结构化日志 + 指标暴露 |
| 认证 | JWT / API Key | 轻量级，满足初期需求 |

---

## 3. 模块依赖关系

```
api/routes/
  ├── agent.py ─────→ core/orchestrator.py ─────→ core/engine.py
  │                                               ├── core/tools/sql_tool.py
  │                                               ├── core/tools/lightrag_tool.py
  │                                               └── core/tools/python_tool.py
  └── documents.py ─→ core/pipeline.py ──────────→ core/graph_service.py
                                                     infrastructure/lightrag.py

所有模块 ──────────→ infrastructure/db.py
所有模块 ──────────→ domain/models.py, domain/schemas.py
```

---

## 4. 数据流

### 4.1 文档摄取流

```
上传文件 → 校验 & 哈希 → 分块 → 写入 file_index/chunk_index
                                └→ [L2/L3] LightRAG insert → PG 图/向量存储
                                └→ [全部]  原始文件 → MinIO
```

### 4.2 Agent 查询流

```
用户问题 → Redis 语义缓存命中？
  ├── 命中 → 直接返回
  └── 未命中 → AgentState 创建
              └→ 循环（最多 5 次）：
                  decide() → execute() → reflect()
                  ├── CONTINUE → 继续循环
                  ├── ANSWER   → 返回答案 + 引用
                  └── GIVE_UP  → 返回无法回答
              └→ 记录 agent_traces
              └→ 写入语义缓存
```

---

## 5. 安全边界

```
┌──────────────────────────────────────┐
│  外部请求                            │
│    ↓ JWT/API Key 认证                │
│  API 层（数据校验 + 权限）            │
│    ↓                                │
│  Core 层（Agent 逻辑）                │
│    ├── SQL 工具：只读连接 + SELECT 白名单  │
│    ├── Python 工具：Docker 沙箱 + 网络禁用  │
│    └── LightRAG：查询接口（只读）         │
└──────────────────────────────────────┘
```

---

## 6. 关键设计决策摘要

| 决策 | 详情见 |
|------|--------|
| LightRAG 统一检索，放弃独立向量/图谱组件 | `docs/adr/001-lightrag-as-unified-retrieval.md` |
| 文件分三级控制成本（L1 仅元数据，L2 轻提取，L3 全图谱） | `docs/adr/002-file-importance-grading.md` |
| 增量哈希更新 vs 全量重建 | `docs/project-design-init.md` §6.2 |
| Agent 决策反思循环（非一次性 RAG） | `docs/project-design-init.md` §5 |

---

> **修改历史**
>
> | 日期 | 变更内容 | 作者 |
> |------|----------|------|
> | 2026-05-22 | 初始文档：基于 project-design-init.md 提炼 | AI Agent |
