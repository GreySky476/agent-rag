# Utils 层

## 模块职责

提供无业务逻辑的通用工具函数，供所有模块使用。不允许有数据库、网络等副作用操作。

## 目录结构

```
utils/
├── hashing.py   # 文件哈希计算与比较
└── text.py      # 文本处理工具
```

## 对外暴露的接口

### `hashing.py` — 哈希工具

| 接口 | 说明 |
|------|------|
| `compute_sha256(content: bytes) -> str` | 计算内容的 SHA-256 哈希 |
| `compute_chunk_hash(text: str) -> str` | 计算文本块的哈希（用于增量对比） |
| `hashes_equal(h1, h2) -> bool` | 安全比较两个哈希值 |

**用途** `[现存]`：文件去重、增量更新时的块变更检测。

### `text.py` — 文本工具

| 接口 | 说明 |
|------|------|
| `split_text(text, chunk_size=800, overlap=100) -> list[str]` | 封装 RecursiveCharacterTextSplitter |
| `clean_text(text: str) -> str` | 文本清洗（去除多余空白、特殊字符等） |
| `truncate_text(text: str, max_tokens: int) -> str` | 按 token 数截断文本 |

---

## 依赖模块

- 仅依赖第三方库（LangChain 的 text_splitter、hashlib）
- 不依赖项目其他模块

---

## 设计约束

- 纯函数，无副作用 `[建议]`
- 所有函数必须带类型注解 `[建议]`
- 不引用项目的领域模型、配置或数据库 `[建议]`

---

> **修改历史**
>
> | 日期 | 变更内容 | 作者 |
> |------|----------|------|
> | 2026-05-22 | 初始文档：基于 project-design-init.md §2 目录结构规划 | AI Agent |
