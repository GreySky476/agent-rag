# API 层

## 模块职责

对外提供 HTTP RESTful 接口，处理请求验证、认证、路由分发，将业务逻辑委托给 Core 层。

## 目录结构

```
api/
├── deps.py                  # FastAPI 依赖注入（数据库会话、配置、认证）
├── sse_protocol.py          # SSE 事件格式化工具
└── routes/
    ├── agent.py             # Agent 查询接口（SSE 流式 + 同步）
    ├── conversations.py     # 对话会话管理接口
    ├── documents.py         # 文档管理接口（含 multipart 上传）
    └── knowledge_domains.py # 知识领域管理接口
```

## 对外接口/API

### Agent 路由 (`routes/agent.py`)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/agent/query` | SSE 流式查询，返回 `text/event-stream` |
| POST | `/api/v1/agent/query/sync` | 同步查询，返回完整 JSON 结果 |
| GET | `/api/v1/agent/traces/{session_id}` | 查询某个会话的完整执行追踪 |

### SSE 事件协议 (`/api/v1/agent/query`)

| 事件 | 说明 |
|------|------|
| `status` | Agent 状态更新（starting/deciding，含 loop_count） |
| `tool_call` | 工具调用开始（tool + args） |
| `tool_result` | 工具调用结果（tool + status + summary） |
| `reflection` | 反思结果（CONTINUE/ANSWER/GIVE_UP） |
| `answer_start` | 开始流式输出最终答案 |
| `answer_chunk` | 答案片段（逐 token） |
| `done` | 流程结束（session_id + status + sources） |
| `error` | 异常中断 |

### 对话路由 (`routes/conversations.py`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/conversations` | 列出所有对话（按 session_id 聚合） |
| GET | `/api/v1/conversations/{session_id}` | 获取单个对话详情（含所有消息） |
| PUT | `/api/v1/conversations/{session_id}` | 重命名对话 |
| DELETE | `/api/v1/conversations/{session_id}` | 删除对话及其所有 traces |

### 知识领域路由 (`routes/knowledge_domains.py`)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/knowledge-domains` | 创建知识领域 |
| GET | `/api/v1/knowledge-domains` | 列出所有知识领域 |

### 文档路由 (`routes/documents.py`)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/documents/upload` | 上传文档（multipart/form-data），触发摄取管道 |
| GET | `/api/v1/documents` | 列出已索引的文档 |
| GET | `/api/v1/documents/{id}` | 获取单个文档详情 |
| DELETE | `/api/v1/documents/{id}` | 删除文档及其关联数据 |

### 统计接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/stats` | 获取统计概览（文档总数、领域数、最近处理日期） |

### 依赖注入 (`deps.py`)

| 函数 | 注入类型 | 说明 |
|------|----------|------|
| `get_db` | AsyncSession | 数据库会话 |
| `get_settings` | Settings | 应用配置 |
| `get_llm_client` | BaseChatModel | LLM 客户端 |
| `get_lightrag_client` | LightRAG | LightRAG 客户端 |
| `get_cache_client` | SemanticCache | Redis 语义缓存 |
| `get_current_user` | str | 认证用户标识 |

---

## 依赖模块

- `core.orchestrator` — Agent 查询流程（同步 + 流式）
- `core.pipeline` — 文档摄取管道
- `infrastructure.db` — 数据库会话
- `domain.schemas` — 请求/响应模型
- `domain.models` — ORM 模型

---

## 设计约束

- 所有响应使用 Pydantic `response_model` `[现存]`
- SSE 端点返回 `StreamingResponse`，media_type=`text/event-stream` `[新增]`
- 文件上传使用 FastAPI `UploadFile`，接收 `multipart/form-data` `[新增]`
- 认证通过 JWT 或 API Key，在 `deps.py` 中实现 `[现存]`
- 错误响应统一格式，HTTP 状态码语义化 `[建议]`

---

> **修改历史**
>
> | 日期 | 变更内容 | 作者 |
> |------|----------|------|
> | 2026-05-22 | 初始文档：基于 project-design-init.md 规划 | AI Agent |
> | 2026-05-22 | Phase 1 实施：新增 SSE 流式查询、conversations CRUD、knowledge-domains CRUD、stats 接口、multipart 文件上传 | AI Agent |
