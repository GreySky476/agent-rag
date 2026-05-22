# 任务卡模板

> **文件命名规范**：`tasks/{YYYYMMDD}-{brief-slug}.md`
> 示例：`tasks/20260522-implement-config-py.md`

---

## 任务信息

| 字段 | 内容 |
|------|------|
| **任务 ID** | TASK-XXX |
| **类型** | `新增` / `增强` / `修复` / `重构` |
| **关联 Epic** | 链接到 `docs/roadmap/current.md` 中的对应 Story |
| **优先级** | P0 / P1 / P2 |
| **预估工时** | Xh |
| **负责人** | — |

---

## 背景与目标

_简要描述为什么要做这个任务，完成后达到什么效果。_

---

## 验收标准

- [ ] AC1: 描述可验证的条件
- [ ] AC2: 描述可验证的条件
- [ ] AC3: 描述可验证的条件

---

## 受影响模块

| 模块 | 变更类型 | 说明 |
|------|----------|------|
| `docs/modules/xxx.md` | 记录变更 | — |
| `src/rag_agent/xxx/xxx.py` | 新增/修改 | — |

---

## 设计引用

- 架构文档：`docs/architecture.md`
- 模块文档：`docs/modules/{module}.md`
- 相关 ADR：`docs/adr/{nnn}-{title}.md`

---

## 实现检查清单

- [ ] 阅读了 `docs/conventions.md`
- [ ] 阅读了对应模块文档 `docs/modules/{module}.md`
- [ ] 实现了核心逻辑
- [ ] 补充了类型注解
- [ ] 编写了单元测试（覆盖 Happy Path + 主要错误路径）
- [ ] 通过了 `ruff check`
- [ ] 通过了 `mypy`
- [ ] 通过了 `pytest`
- [ ] 更新了模块文档的"修改历史"
- [ ] 如需架构变更，产出了 ADR

---

## 备注

_补充信息、已知风险、Open Question_
