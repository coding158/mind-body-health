# 内容架构与版权策略 · 公私有三层架构
# Content Architecture & Copyright Strategy · The Three-Layer Model

> 本文档提炼自项目早期关于「如何从 V1.1 搬迁到 GitHub」的完整策略讨论。
> 与 [`ROADMAP-Master-Skill知识网络.md`] 互补——路线图侧重「建什么、何时建」，本文档侧重「什么能公开、什么不能、架构如何分层」。
>
> Key conclusions extracted from the strategy discussion. Complements the Roadmap:
> the Roadmap covers "what to build and when"; this document covers "what can be public, what can't, and how the layers are split."

---

## 核心判断 · Core Judgment

**把 400+ 本电子书全文直接推送到 GitHub 公开仓库，存在明显版权风险。**
**正确做法：公开知识结构，私有保存原文。三层分离。**

Uploading 400+ full-text e-books to a public GitHub repo carries clear copyright risk.
The right approach: make the knowledge structure public, keep the full texts private. Three separated layers.

---

## 一、为什么 EXE 时代没人管，GitHub 时代风险更高

V1.1 编者序已声明：「所有版权归出版社和原作者所有。」

合集内绝大部分作品（奥修、南怀瑾、托利、克里希那穆提、《与神对话》、《少有人走的路》等）现在仍受版权保护。TXT/PDF/CHM 来源于网络，不等于版权失效。

- 出版社或版权方可发 DMCA 投诉
- GitHub 一般会：删除文件 → 下架仓库 → 多次违规封号
- 公开仓库的风险远高于早期离线传播的 EXE 合集

---

## 二、内容风险分级 · Content Risk Tiers

### 🟢 A 类：几乎无风险 · Class A: Near-Zero Risk

公版古籍原文。已进入公有领域，可全文公开。

Public-domain classics. Originals are in the public domain; full text may be public.

- 金刚经、心经、六祖坛经、地藏经、法华经、阿含经
- 道德经、庄子、黄帝内经

### 🟡 B 类：风险较低 · Class B: Lower Risk

古籍现代整理版的**原文部分**。注释可能有版权，需注意版本。

Original text of modern editions of ancient classics. Annotations may carry copyright; verify the edition.

### 🔴 C 类：风险最高 · Class C: Highest Risk

现当代作者的全本作品。全部受版权保护，全文上传风险高。

Contemporary works. All under copyright; uploading full text carries high risk.

- 奥修（《觉察》《勇气》《创造力》等）
- 南怀瑾（《如何修证佛法》《静坐修道与长生不老》等）
- 托利（《当下的力量》）
- 张德芬（《遇见未知的自己》）
- 吴清忠（《人体使用手册》）
- 赛斯、欧林、与神对话、奇迹课程

### 判定原则

```
公版古籍原文  → 可公开全文
现代作品全文  → 不可公开全文
目录/元数据/读书笔记/个人摘要  → 可公开（合理使用）
```

---

## 三、三层架构 · The Three-Layer Architecture

```
┌─────────────────────────────────────────────┐
│  第一层：公开 GitHub                          │
│  Layer 1: Public GitHub                      │
│                                              │
│  只放：目录 / 索引 / 标签 / 读书笔记 /         │
│        人物关系图谱 / Agent Prompt            │
│  不放：任何受版权保护的全文                     │
│                                              │
│  完全合规 · Fully compliant                   │
├─────────────────────────────────────────────┤
│  第二层：本地 Obsidian                        │
│  Layer 2: Local Obsidian                     │
│                                              │
│  保存：EPUB / PDF / TXT 全文                  │
│  用途：自己阅读                                │
│                                              │
│  不公开 · Private                             │
├─────────────────────────────────────────────┤
│  第三层：AI 知识库                            │
│  Layer 3: AI Knowledge Base                  │
│                                              │
│  RAG 索引全文 · 仅本地检索                     │
│  不公开分发原文                                │
│                                              │
│  私有 · Private                               │
└─────────────────────────────────────────────┘
```

> 这也是很多大型佛学、哲学、知识管理仓库长期存活的原因：
> 公开的是知识结构，私下保存的是原始文献。
>
> This is why many large Buddhist/philosophy/KM repositories survive long-term:
> what's public is the knowledge structure; what's private is the source texts.

---

## 四、公开仓库的目录结构 · Public Repo Directory Structure

```
GitHub 公开仓库
├── agents/            ← Skill prompt 文件（已在做 ✅）
├── concepts/          ← 概念库（待建 🔵）
├── questions/         ← 问题库（待建 🔵）
├── people/            ← 人物库（待建 🔵）
├── docs/              ← 哲学/原则/策略文档（已有基础）
├── classics/          ← 公版古籍原文 + 所有书籍的目录/元数据
│   ├── buddhism/      ← 金刚经、心经等（公版全文）
│   ├── taoism/        ← 道德经、庄子等（公版全文）
│   └── catalog/       ← C 类作品的目录索引（非全文）
├── practice-records/  ← 个人实践记录（已有基础）
└── tests/             ← 路由测试集（待建 🔵）
```

### 关键边界：C 类作品怎么放

以《如何修证佛法》（南怀瑾）为例：

```markdown
# 如何修证佛法

作者：南怀瑾
出版社：×××
出版年份：×××

## 目录
1. ×××
2. ×××
...

## 核心关键词
- 戒定慧
- 六度
- ...

## 相关书籍
[[内证观察笔记]]
[[静坐修道与长生不老]]

## 读书笔记（个人摘要，非原文）
……
```

只放：目录、元数据、关键词、个人笔记——**不放全文**。

---

## 五、为什么这比单纯上传 400 本书更有价值

```
❌ 不做：
   新时代与灵修合集 → 400 本全文上传 GitHub
   → 版权风险高 + 只是电子书仓库

✅ 做：
   身心灵知识地图（公开） + 经典电子书库（私有）
   → 版权合规 + 知识结构可演化 + 可接入 AI Agent
```

当 Skill 建立起来以后，增加一本《内证观察笔记》只是给 Skill 增加知识来源——不需要改整个系统。这是持续演化的基础。

---

## 六、与路线图的关系 · Relation to the Roadmap

| 维度 | 本文档（版权策略） | ROADMAP（建设路线） |
|---|---|---|
| 焦点 | 什么能公开、架构如何分层 | 先建什么、何时建、如何验证 |
| 核心产出 | 三层架构 + 风险分级 + 目录设计 | 概念库/问题库/人物库 + 测试闭环 + 部署顺序 |
| 约束 | 所有建设须遵守公私有边界 | 按 Phase 推进建设 |

两文档互相约束：路线图决定建设顺序，版权策略决定每层能放什么。

---

## 七、部署方案对比 · Deployment Options

| 方案 | 复杂度 | 适合阶段 | 说明 |
|---|---|---|---|
| GitHub + Claude/OpenAI 直连 | 低 | **现在** | 本机测试，改 Router 最方便 |
| GitHub + OpenWebUI | 中 | Router 稳定后 | 本地运行，免费，调试方便 |
| GitHub + Dify | 中高 | 正式上线 | Workflow 化，需 Router 稳定 |
| GitHub + LangGraph | 高 | 最终形态 | 最接近真正 Agent 系统，维护成本最高 |

> 见 [`ROADMAP-Master-Skill知识网络.md`] 的部署路线章节。

---

## 一句话 · In One Line

> 公开的是地图，私有的是矿。
> 三层分离，让项目既合规又能持续演化成真正的 Master-Skill 系统。
>
> What's public is the map; what's private is the mine.
> Three separated layers keep the project compliant while it evolves into a true Master-Skill system.
