# Master-Skill 知识网络 · 建设路线图
# Master-Skill Knowledge Network · Roadmap

> 本文档从 `concepts-questions.md` 提炼关键结论，作为正式的阶段性计划。
> 当前已进入 Phase 3：从「书库」阶段转入「知识网络」阶段。
>
> Key conclusions extracted from `concepts-questions.md`, formalized as the next-phase plan.
> We have entered Phase 3: from "book collection" to "knowledge network."

---

## 当前状态评估 · Current State Assessment

```
Phase 1 ✅  Skill 定义（5 个 Master Skill 已成型）
Phase 2 ✅  Router 调度（单路由 / 混合路由 / 安全路由 / 兜底路由已定义）
Phase 3 🔵 知识网络建设（← 当前位置 · Current）
Phase 4 ⬜ 测试验证（100–300 条问题集，闭环跑通）
Phase 5 ⬜ 运行时部署（OpenWebUI → Dify → LangGraph）
```

### 能力评分 · Capability Score

| 维度 Dimension | 分数 Score | 状态 Status |
|---|---|---|
| Skill 划分 · Skill Partitioning | 9/10 | ✅ 边界清晰，无明显重叠 |
| 安全边界 · Safety Boundaries | 9/10 | ✅ 危机/医疗/风险实践均已定义 |
| Router 设计 · Router Design | 8.5/10 | ✅ 四层路由（安全→单域→混合→兜底） |
| 可扩展性 · Extensibility | 9/10 | ✅ 新增 Skill / 概念 / 问题均可接入 |
| 知识结构 · Knowledge Structure | 7.5/10 | 🔵 缺 Concept / Question / People 三层 |
| 运行验证 · Runtime Validation | 3/10 | ⬜ 尚未建立测试闭环 |

---

## 核心判断 · Core Judgment

**下一步不是继续扩充书库，也不是马上接 Dify/OpenWebUI。**
**优先完成 Router → Concept → Question 三层，然后建立测试闭环。**

The next step is NOT adding more books, nor immediately deploying to Dify/OpenWebUI.
Build the three layers (Concept → Question → People), then establish a test loop.

### 为什么不继续收书 · Why Not More Books

```
更多书 → 更多书 → 更多书
500本 → 1000本 → 2000本
→ Skill 能力几乎没有提升
```

书籍是知识来源，但**问题库才是 Skill 的训练集**。
Books are the source; the question library is the training set.

### 为什么不先接 Dify · Why Not Dify First

Router 还在频繁修改。Dify Workflow 每次改 Router 都要同步条件节点、分支节点、变量节点——维护成本太高。
先在本机用 Claude/OpenAI 直连测试，等 Router 稳定后再部署。

Router still changes frequently. Syncing Dify workflows on every Router tweak is costly.
Test locally with Claude/OpenAI first; deploy when Router is stable.

---

## 三层建设 · The Three Layers to Build

### 知识网络目标架构 · Target Architecture

```
书籍库 (books/)
    ↓
人物库 (people/)        ← Level 2
    ↓
概念库 (concepts/)      ← Level 3
    ↓
问题库 (questions/)     ← Level 4
    ↓
Skill (agents/)        ← Level 5
```

### Layer 1: 概念库 · Concept Library

**为什么需要：** 用户不会问「请调用 Zen-Master」，用户会问「什么是觉察？」。而「觉察」同时属于克里希那穆提、托利、奥修、禅宗——需要独立的概念节点来承载跨 Skill 关联。

Why: Users don't ask "call Zen-Master." They ask "what is awareness?" — and "awareness" spans Krishnamurti, Tolle, Osho, and Zen simultaneously. Concepts need their own nodes.

**目录结构：**

```
concepts/
├── 觉察.md
├── 无我.md
├── 正念.md
├── 气脉.md
├── 业力.md
├── 宽恕.md
├── 死亡.md
├── 信念.md
├── 定.md
├── 慧.md
├── 因果.md
├── 福报.md
└── ...
```

**每个概念文件的结构模板：**

```yaml
concept: 觉察

related_skills:
  - Zen-Master
  - Psychology-Master
  - NewAge-Master

related_people:
  - 克里希那穆提
  - 奥修
  - 托利

related_books:
  - 当下的力量
  - 心灵自由之路

related_concepts:
  - 正念
  - 观照
  - 见性

related_questions:
  - 什么是觉察
  - 如何觉察念头
  - 觉察与正念的区别
```

**目标：300+ 核心概念**

### Layer 2: 问题库 · Question Library

**为什么需要：** 书籍是知识来源，问题库才是 Skill 的训练集。每新增一本书，关联到已有问题即可自动进入知识网络——不需要重新训练。

Why: A new book just needs to be linked to existing questions to enter the knowledge network — no retraining needed.

**目录结构：**

```
questions/
├── 佛学/
│   ├── 打坐昏沉怎么办.md
│   ├── 什么是无我.md
│   └── ...
├── 禅修/
├── 中医/
├── 道家/
└── 新时代/
```

**每个问题文件的结构模板：**

```yaml
question: 打坐昏沉怎么办

related_skills:
  - Zen-Master

related_books:
  - 内证观察笔记
  - 坐禅之管见
  - 如何修证佛法

keywords:
  - 昏沉
  - 散乱
  - 睡眠
  - 定力

expected_answer:
  # 标准回答或回答要点
```

**目标：1000+ 问题**

### Layer 3: 人物库 · People Library

**为什么需要：** 用户会问「南怀瑾怎么看气脉？」「奥修和托利有什么区别？」——需要人物节点来承载跨领域引用。

Why: Users ask comparative questions ("Osho vs Tolle") — people nodes enable cross-reference.

**目录结构：**

```
people/
├── 南怀瑾.md
├── 奥修.md
├── 克里希那穆提.md
├── 托利.md
├── 赛斯.md
├── 刘力红.md
├── 李阳波.md
└── ...
```

**目标：100+ 核心人物**

---

## 路由进化 · Router Evolution

### 当前路由 · Current

```
问题 → Skill
```

### 目标路由 · Target

```
问题 → 概念 → Skill
```

概念层让 Router 更精准：先识别问题涉及哪些核心概念，再根据概念的 `related_skills` 判定该路由到哪个（哪些）Skill。

The concept layer makes routing more precise: first identify which concepts the question touches, then use the concept's `related_skills` to determine routing.

---

## 测试驱动 · Test-Driven Validation

### 优先级：先跑起来验证

很多问题只有运行后才会暴露。例如：

| 用户问题 | 理论路由 | 运行后可能发现 |
|---|---|---|
| 打坐三个月后开始失眠 | Zen + TCM | Psychology + Zen + TCM |
| 感觉人生没有意义 | Psychology | Psychology + NewAge |
| 为什么修行越久越孤独 | Zen | Zen + Psychology |

### 测试集结构

```
tests/
├── 001-打坐腿麻.yml
├── 002-凌晨三点醒.yml
├── 003-什么是觉察.yml
└── ...
```

```yaml
# tests/001-打坐腿麻.yml
question: 打坐腿麻怎么办
expected:
  primary: Zen-Master
actual: ?
pass: ?
```

**目标：先建 100 条，逐步到 300 条，长期 1000 条。**

每轮测试输出：
- 路由正确率（expected vs actual）
- Skill 边界模糊点
- 需建立独立 Concept 节点的概念

---

## 部署路线 · Deployment Roadmap

```
现在          先在本机用 Claude/OpenAI 直连测试
    ↓
Router 稳定    概念/问题/人物三层达到基准量
    ↓
Step 1        OpenWebUI（本地运行 · 免费 · 调试方便）
    ↓
Step 2        Dify（Router 稳定后再转 Workflow）
    ↓
Step 3        LangGraph（最后考虑 · 学习成本最高）
```

### 不提前部署的原因

```
当前                        提前接 Dify 后
──────                      ──────────────
改 Router → 改一个文件       改 Router → 同步条件节点
                                      → 同步分支节点
                                      → 同步变量节点
                                      → 维护成本 × 3
```

---

## 里程碑 · Milestones

| 里程碑 | 完成标志 | 预估 |
|---|---|---|
| M1: 概念库 | 300+ 概念文件，每个含 related_skills/people/books/questions | — |
| M2: 问题库 | 1000+ 问题文件，每个含 related_skills/books/keywords | — |
| M3: 人物库 | 100+ 人物文件，每个含 related_concepts/books/skills | — |
| M4: 测试闭环 | 300 条测试问题，Router 正确率 ≥ 90% | — |
| M5: 部署 | OpenWebUI 上线，Router + 5 Skill 可对外服务 | — |

---

## 一句话 · In One Line

> 不再优先扩充书库，也不再急着部署。
> 优先做 Router → Concept → Question 三层，然后跑一轮真实问题闭环验证。
>
> Don't prioritize expanding the library or rushing to deploy.
> Build Router → Concept → Question layers first, then run a real-question validation loop.
