alembic upgrade head # 前端界面设计方案

> **状态**：已确认。本方案采用 React + Vite 前后端分离架构，实现类 DeepSeek 的双栏聊天界面，同时集成 RAG 知识库管理。

---

## 1. 技术栈

| 层 | 选型 | 理由 |
|----|------|------|
| 框架 | React 18 + TypeScript | 生态最丰富，适合复杂交互 |
| 构建 | Vite | 快速启动，代理配置简单 |
| 样式 | Tailwind CSS | 快速开发，深色模式支持好 |
| 状态管理 | Zustand | 轻量，比 Redux 简洁，比 Context 性能好 |
| Markdown | react-markdown + rehype-highlight | 渲染 AI 回复中的代码块和表格 |
| 流式 | fetch + ReadableStream | 浏览器原生支持 SSE，无需额外依赖 |
| UI 提示 | react-hot-toast | 轻量 toast 反馈 |

---

## 2. 部署方式

前后端分离：
- 前端：`npm run dev` → `localhost:5173`，Vite 代理 `/api` 到后端
- 后端：`uvicorn src.rag_agent.main:app` → `localhost:8000`
- 生产环境：nginx 反向代理，前端静态文件 + API 代理

### Vite 代理配置

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

---

## 3. 整体布局（双栏结构）

```
┌─────────────────────────────────────────────────────────────┐
│  🧠 RAG Agent                    [Chat] [Knowledge]    ⚙️   │  ← 顶栏导航
├────────────────┬────────────────────────────────────────────┤
│                │                                            │
│  🔍 搜索对话...  │  ┌──────────────────────────────────────┐ │
│                │  │  👤 User: 去年华东区供应商延迟率？      │ │
│  ───────────── │  │                                      │ │
│  📁 今天        │  │  🤖 Assistant:                        │ │
│   华东供应商查询 │  │  根据知识库检索结果，华东区核心供应商中  │ │
│   财务报表分析   │  │  以下企业的交付延迟率超过5%：          │ │
│                │  │                                      │ │
│  📁 昨天        │  │  • 上海xx制造 — 延迟率 7.2%           │ │
│   产品规格查询   │  │  • 浙江yy物流 — 延迟率 5.8%    [引用] │ │
│   员工手册问答   │  │                                      │ │
│                │  │  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ │ │
│  [+] 新对话     │  │  📎 上传文件   [输入你的问题...]  ⬆️ │ │
│                │  └──────────────────────────────────────┘ │
├────────────────┴────────────────────────────────────────────┤
│  消息列表区域（可滚动，自适应高度）                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. 路由设计

| 路径 | 页面 | 说明 |
|------|------|------|
| `/` | ChatPage | 默认首页，重定向到最近会话或空状态 |
| `/chat` | ChatPage | 聊天主页面（含侧边栏） |
| `/chat/:sessionId` | ChatPage | 指定会话的聊天页面 |
| `/knowledge` | KnowledgePage | 知识库管理页面 |

---

## 5. 页面一：聊天页面（ChatPage）

### 5.1 对话侧边栏

| 功能 | 交互 |
|------|------|
| 新建对话 | 点击 `[+]` 按钮，POST 创建新 session，跳转到空白聊天 |
| 对话列表 | 按日期分组（今天/昨天/更早），显示对话标题（自动截取首条消息前20字） |
| 重命名对话 | 双击标题进入编辑模式，PUT 更新 |
| 删除对话 | 右键菜单 / 悬停出现 🗑️，弹出确认框后 DELETE |
| 搜索历史 | 顶部搜索框，实时过滤对话列表 |

### 5.2 聊天消息列表

| 状态 | 处理 |
|------|------|
| **Empty** | 显示引导文案："上传知识库文档后开始提问" + 建议问题列表 |
| **Loading** | 显示骨架屏动画（3 条消息占位） |
| **流式输出** | 逐 token 渲染 AI 回复，Markdown 实时解析；打字光标闪烁；工具调用步骤内联展示 |
| **Error** | 消息气泡变红，显示错误摘要 + 重试按钮 |
| **Success** | 完整消息列表，最底部自动滚动到最新消息 |

### 5.3 Agent 步骤内联展示

在 AI 回复中，每个工具调用作为可折叠卡片内联展示：

```
🤖 Assistant
  ┌─ 🔧 sql_query ──────────────────────┐
  │  SELECT supplier, delay_rate FROM ...  │
  │  ▸ 返回 12 行                           │  ← 可折叠
  └──────────────────────────────────────┘
  ┌─ 🔧 lightrag_search ────────────────┐
  │  模式: hybrid                          │
  │  查询: 华东区供应商                     │
  │  ▸ 找到 5 个实体, 3 条关系              │  ← 可折叠
  └──────────────────────────────────────┘
  ┌─ 🤔 反思 ────────────────────────────┐
  │  → 信息完备，可以给出答案                │
  └──────────────────────────────────────┘
  
  根据知识库检索结果...（最终答案）     [查看引用来源 ▼]
```

### 5.4 输入区域

| 功能 | 交互 |
|------|------|
| 多行输入框 | 自适应高度（最小 1 行，最大 6 行） |
| Enter 发送 | Enter 发送，Shift+Enter 换行 |
| 发送按钮 | 输入非空时变为激活色 |
| 停止生成 | 流式输出中，发送按钮变为 ⏹ 停止按钮 |
| 文件引用 | 📎 按钮可快速切换到知识库 Tab 选择文档引用 |
| 快捷提示 | 空输入时显示 placeholder："输入问题，Enter 发送，Shift+Enter 换行" |

---

## 6. 页面二：知识库管理（KnowledgePage）

### 6.1 布局

```
┌──────────────────────────────────────────────────────┐
│  📚 知识库管理                                        │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────┐  ┌──────────────┐ │
│  │                              │  │              │ │
│  │    📎 拖拽文件到此处上传       │  │  统计卡片     │ │
│  │    或点击选择文件              │  │  12 个文件    │ │
│  │                              │  │  3 个领域     │ │
│  │  支持 PDF / TXT / MD / CSV   │  │              │ │
│  └──────────────────────────────┘  └──────────────┘ │
│                                                      │
│  过滤: [全部领域 ▼] [全部级别 ▼]  🔍 搜索文件名...     │
│                                                      │
│  ┌──────┬──────────┬──────┬──────┬──────┬────────┐  │
│  │ 名称  │ 领域     │ 级别  │ 块数  │ 状态  │ 操作   │  │
│  ├──────┼──────────┼──────┼──────┼──────┼────────┤  │
│  │ 财报  │ 财务     │ L3   │ 24   │ ✅   │ 🗑️ 👁️  │  │
│  │ 合同  │ 法务     │ L2   │ 8    │ ✅   │ 🗑️ 👁️  │  │
│  │ ...  │ ...      │ ...  │ ...  │ ...  │ ...    │  │
│  └──────┴──────────┴──────┴──────┴──────┴────────┘  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 6.2 组件状态覆盖

| 组件 | Loading | Empty | Error | Success |
|------|---------|-------|-------|---------|
| 上传区域 | 禁用态 + 灰色背景 | 虚线框 + 上传提示 | 红色边框 + 错误信息 | 上传完成后淡出成功提示 |
| 文档列表 | 骨架屏（4 行占位） | "暂无文档，上传第一个文件开始" | inline 错误 toast | 表格正常展示 |
| 统计卡片 | 显示 "--" 占位 | 全部显示 0 | 显示 "--" 占位 | 数字正常显示 |
| 领域筛选 | 禁用态 | 显示"无领域" | 禁用态 | 下拉正常 |

---

## 7. 后端 API 完整清单

### 7.1 现有 API（需改造）

| # | 接口 | 改造内容 |
|---|------|----------|
| 1 | `POST /api/v1/agent/query` | 改造为 SSE 流式响应 `text/event-stream`，每个 Agent 步骤作为命名事件推送 |
| 2 | `POST /api/v1/documents/upload` | 改造为接收 `multipart/form-data` 实际文件上传，文件保存到 MinIO |

### 7.2 新增 API

| # | 接口 | 说明 |
|---|------|------|
| 3 | `GET /api/v1/conversations` | 列出所有对话会话（从 agent_traces 聚合，按 session_id 分组，返回最后更新时间） |
| 4 | `GET /api/v1/conversations/{session_id}` | 获取单个会话的所有消息（traces 中 final_answer 非空的记录） |
| 5 | `PUT /api/v1/conversations/{session_id}` | 重命名对话（更新标题） |
| 6 | `DELETE /api/v1/conversations/{session_id}` | 删除对话及其所有 traces |
| 7 | `POST /api/v1/knowledge-domains` | 创建知识领域 |
| 8 | `GET /api/v1/knowledge-domains` | 列出所有知识领域 |
| 9 | `GET /api/v1/stats` | 获取统计概览（文档总数、领域数、最近处理日期） |

### 7.3 SSE 事件协议

```
event: status
data: {"step": 0, "status": "deciding", "loops_max": 5}

event: tool_call
data: {"step": 1, "tool": "lightrag_search", "args": {"query": "华东区供应商", "mode": "hybrid"}}

event: tool_result  
data: {"step": 1, "tool": "lightrag_search", "status": "success", "summary": "找到 5 个实体"}

event: reflection
data: {"step": 1, "result": "CONTINUE"}

event: tool_call
data: {"step": 2, "tool": "sql_query", "args": {"query": "SELECT ... WHERE delay_rate > 5"}}

event: tool_result
data: {"step": 2, "tool": "sql_query", "status": "success", "summary": "返回 3 行"}

event: reflection  
data: {"step": 2, "result": "ANSWER"}

event: answer_start
data: {}

event: answer_chunk
data: {"content": "根据知识库检索结果，华东区..."}

event: answer_chunk
data: {"content": "以下企业的交付延迟率超过5%：..."}

event: done
data: {"session_id": "abc123", "status": "completed", "loop_count": 2, "sources": [...]}
```

---

## 8. 前端项目结构

```
frontend/
├── package.json
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── api/
│   │   ├── client.ts            # HTTP 客户端（fetch 封装）
│   │   ├── sse.ts               # SSE 流式客户端
│   │   ├── chat.ts              # 对话 API
│   │   └── documents.ts         # 文档 API
│   ├── components/
│   │   ├── Layout.tsx           # 整体布局容器（顶栏 + 双栏）
│   │   ├── Navbar.tsx           # 顶栏导航
│   │   ├── Sidebar.tsx          # 对话历史侧边栏
│   │   ├── ConversationItem.tsx # 单条对话列表项
│   │   ├── MessageList.tsx      # 消息列表容器
│   │   ├── MessageBubble.tsx    # 单条消息气泡（用户/系统/AI）
│   │   ├── ToolCallCard.tsx     # Agent 工具调用内联卡片
│   │   ├── ChatInput.tsx        # 输入区域
│   │   ├── StreamingText.tsx    # 流式文本渲染
│   │   ├── EmptyChat.tsx        # 空聊天引导页
│   │   ├── UploadZone.tsx       # 拖拽上传区域
│   │   ├── DocumentTable.tsx    # 文档列表表格
│   │   ├── StatsCard.tsx        # 统计卡片
│   │   └── ConfirmDialog.tsx    # 确认弹窗（删除用）
│   ├── pages/
│   │   ├── ChatPage.tsx         # 聊天页
│   │   └── KnowledgePage.tsx    # 知识库管理页
│   ├── hooks/
│   │   ├── useSSE.ts            # SSE 流式数据 Hook
│   │   └── useConversations.ts  # 对话列表管理 Hook
│   ├── stores/
│   │   └── chatStore.ts         # Zustand 全局状态
│   └── types/
│       └── index.ts             # TypeScript 类型定义
└── .gitignore
```

---

## 9. 关键交互流程

### 9.1 新对话 → 发送问题 → 流式回复

```
1. 用户点击 [+] 或首页空白引导
2. frontend: POST /api/v1/conversations → 获得 session_id
3. 用户输入问题，按 Enter
4. frontend: 调用 SSE 连接 POST /api/v1/agent/query
   → 用户消息气泡立即出现
   → AI 消息气泡出现（空状态 + 闪烁光标）
5. SSE 逐事件推送：
   → status    → 显示"Agent 正在思考..."
   → tool_call → 内联卡片出现，显示工具名称和输入
   → tool_result → 卡片更新为结果摘要（可展开详情）
   → reflection → 显示反思结论
   → answer_chunk → 逐 token 追加到 AI 消息气泡
   → answer_chunk → ...
   → done     → 最终状态，显示引用来源
6. 对话保存到左侧侧边栏（自动截取标题）
```

### 9.2 上传文档 → 处理后可在聊天引用

```
1. 切换到 Knowledge Tab
2. 拖拽文件或点击上传区
3. frontend: POST /api/v1/documents/upload (multipart/form-data)
   → 显示进度条
4. 后端处理（分块 → LightRAG）
   → 进度更新
5. 处理完成后出现在文档列表
6. 在 Chat Tab 输入框点击 📎，可快速查看/引用已处理的文档列表
```

---

## 10. 全局状态设计（Zustand Store）

```typescript
interface ChatStore {
  // 对话
  conversations: Conversation[]
  activeSessionId: string | null
  messages: Message[]
  
  // 流式状态
  isStreaming: boolean
  streamingContent: string
  toolCallSteps: ToolCallStep[]
  
  // UI 状态
  sidebarOpen: boolean
  activePage: 'chat' | 'knowledge'
  
  // 操作
  createConversation: () => Promise<string>
  sendMessage: (content: string) => Promise<void>
  stopGeneration: () => void
  deleteConversation: (id: string) => Promise<void>
  renameConversation: (id: string, title: string) => Promise<void>
}
```

---

## 11. 组件状态覆盖总表

| 组件 | Loading | Empty | Error | Success |
|------|---------|-------|-------|---------|
| 对话侧边栏 | 骨架屏 5 条 | "暂无对话，点击 + 开始" | inline 错误 + 重试 | 正常列表 |
| 消息列表 | 骨架屏 3 条 | 引导页 + 建议问题 | 错误消息气泡 + 重试 | 消息列表 |
| 流式输出 | 闪烁光标 | — | 红色中断提示 | 完整答案 |
| 上传区域 | 禁用 + loading spinner | 虚线框提示 | 红色边框 + 消息 | 成功 toast |
| 文档列表 | 骨架屏 4 行 | 空状态插画 + 提示 | inline 错误 toast | 表格数据 |
| 统计卡片 | Skeleton | 显示 0 | Skeleton | 真实数字 |

---

> **修改历史**
>
> | 日期 | 变更内容 | 作者 |
> |------|----------|------|
> | 2026-05-22 | 初始方案：确定 React + Vite 技术栈、双栏布局、SSE 流式协议 | AI Agent |
