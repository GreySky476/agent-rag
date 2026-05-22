# 知识库维护规则

> **目标**：确保知识库文档始终与代码保持一致，不腐化。

---

## 1. 强制更新规则

以下情况 **必须** 执行对应的文档更新操作：

| 触发事件 | 必须执行的操作 |
|----------|---------------|
| 新增/修改 API 端点 | 更新 `docs/modules/api.md` 的接口表格 |
| 新增/修改 ORM 模型 | 更新 `docs/modules/domain.md` + `docs/schema/index.md` |
| 新增/修改基础设施组件 | 更新 `docs/modules/infrastructure.md` |
| 新增/修改 Core 层逻辑 | 更新 `docs/modules/core.md` |
| 新增/修改工具函数 | 更新 `docs/modules/utils.md` |
| 新增依赖包 | 更新 `docs/architecture.md` §技术栈 |
| 架构层面的任何偏离 | 产出新 ADR 到 `docs/adr/` |
| 约定或规范变更 | 更新 `docs/conventions.md` |

---

## 2. 修改历史格式

每个模块文档的末尾必须维护一个 **修改历史** 表格：

```markdown
> **修改历史**
>
> | 日期 | 变更内容 | 作者 |
> |------|----------|------|
> | YYYY-MM-DD | 变更简述 | 提交者 |
```

新条目追加在表格末尾（旧的在上面，新的在下面）。

---

## 3. 一致性检查

### 3.1 手动检查清单（任务完成前执行）

- [ ] `docs/modules/` 中列出的接口在实际代码中是否存在？
- [ ] `docs/schema/` 中描述的字段与 ORM 模型是否一致？
- [ ] `docs/architecture.md` 中描述的依赖关系与实际 import 是否一致？
- [ ] `docs/conventions.md` 中的规则是否被实际代码遵循？
- [ ] `AGENTS.md` 中的命令是否仍然可运行？

### 3.2 自动检查命令（推荐定期执行）

```bash
# 检查代码风格一致性
ruff check src/ tests/

# 检查类型完整性
mypy src/

# 运行全量测试
pytest
```

---

## 4. ADR 产出规范

### 4.1 何时产出 ADR

- 引入新的技术依赖或框架
- 改变已有架构模式（如从同步改异步）
- 数据模型的大幅重构
- 安全或性能方面的重大决策
- 与 `docs/project-design-init.md` 设计方案出现偏差

### 4.2 ADR 命名规范

```
docs/adr/{NNN}-{brief-slug}.md
```

编号从现有 ADR 最大编号 +1 递增。

### 4.3 ADR 格式

```markdown
# ADR-NNN: {标题}

## 状态
{提议中 / 已接受 / 已废弃 / 已替代}

## 日期
YYYY-MM-DD

## 背景
_为什么需要做这个决策_

## 决策
_我们做了什么决定_

## 后果
### 正面影响
### 负面影响
### 缓解措施
```

---

## 5. Roadmap 更新规范

- 每当 Story 完成，将 `docs/roadmap/current.md` 中的状态从"进行中"改为"已完成"
- 每当 Epic 完成，归档旧的 current.md 并创建新的
- 新 Epic 的 Story 列表应由架构师（或人类决策者）审批后写入

---

## 6. 禁止事项

- ❌ 不创建 `README.md` 替代 `AGENTS.md`（二者定位不同）
- ❌ 不修改 `docs/project-design-init.md`
- ❌ 不在模块文档中写入超过 200 行的内容（超过则应拆分）
- ❌ 不留空的"待补充"字段——要么写清楚，要么删除该字段

---

> **修改历史**
>
> | 日期 | 变更内容 | 作者 |
> |------|----------|------|
> | 2026-05-22 | 初始文档 | AI Agent |
