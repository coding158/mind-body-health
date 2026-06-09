# 仓库结构说明 · Repository Structure

> 每个文件夹和文件的用途说明，方便贡献者快速找到合适的位置。

---

```
mind-body-health/
│
├── README.md
│   # 项目主文档，包含完整的身心健康体系框架
│   # 十一个章节，从入门书目到转触实践到学习次第
│
├── STRUCTURE.md
│   # 本文件，仓库结构说明和各文件夹用途注释
│
├── CLAUDE.md
│   # 觉知陪伴智能体 v2 系统提示词（中英双语）
│   # 定义智能体的根本定位、安全边界、四层来源体系、语气和知识库索引
│   # CCR 路由即可调用运行的完整 prompt
│
├── CONTRIBUTING.md
│   # 参与共建指南：铁律（版权、安全、诚实标注、不给糖）、共建模式说明
│
├── LICENSE.md / NOTICE.md
│   # 开源许可与版权声明
│
├── PHILOSOPHY-八字心法.md
│   # 项目总纲（根目录副本，主文件在 docs/ 下）
│   # 快乐·动手·开源·分享——每个字都是对一个具体执著的对治
│
├── crisis-resources.md
│   # 危机热线资源清单（人工核实）
│   # ⛔ 最高优先级：只能引用此文件内的号码，禁止凭记忆给号
│
├── reading-list.md
│   # 推荐书目清单
│   # 包含中医、佛理、现代觉察、儒释道融合四个分类
│   # 注明版权状态，不收录受版权保护的原文
│
├── docs/                              ← 体系核心文档
│   │
│   ├── 00-体系总索引.md
│   │   # 整个体系文档的导航入口，按魂·理·境·术四层索引
│   │
│   ├── PHILOSOPHY-八字心法.md
│   │   # 魂层：项目总纲，八字各字的含义与关联
│   │
│   ├── PRINCIPLE-回归与转换.md
│   │   # 理层：一切方法 = 回归 + 转换；转换 vs 给糖的微妙分寸
│   │
│   ├── PRINCIPLE-suo-and-zhuan.md
│   │   # 理层英文补充：所（object）立与转换的机制
│   │
│   └── AWARENESS-觉知与六触.md
│       # 境层：拱顶石——觉知观看六触流转，见修行在此合一
│
├── agents/                            ← 智能体提示词与配置
│   │
│   ├── awareness-companion-v2-prompt.md
│   │   # 觉知陪伴智能体 v2 系统提示词（英文版）
│   │
│   ├── 觉知陪伴智能体-v2计划书.md
│   │   # v2 设计方案：四层来源体系、安全边界、两轮自检、保真度测试
│   │
│   ├── AGENT-觉知陪伴智能体.md
│   │   # 智能体路由与部署说明
│   │
│   └── crisis-resources.md
│       # 智能体专用的危机资源副本
│
├── classics/                          ← 经典原文摘录与注解（仅收公版无版权内容）
│   │
│   ├── tcm/                           # 中医经典
│   │   ├── huangdi-neijing-ch1.md                # 黄帝内经·上古天真论（养生总纲·恬淡虚无真气从之）
│   │   ├── 黄帝内经-上古天真论关键段落.md          # 同文件中文命名版
│   │   ├── reading-list-tcm-path.md               # 中医学习路径（阅读次序指引）
│   │   └── reading-list-中医学习路径.md            # 同文件中文命名版
│   │
│   ├── buddhism/                      # 佛理经典
│   │   ├── surangama-six-faculties.md             # 楞严经·六根觉性（元明照生所·转触·文殊偈）
│   │   ├── liaofan-establishing-destiny.md        # 了凡四训·立命之学（命由我作·功过格）
│   │   ├── 了凡四训-立命之学关键段落.md              # 同文件中文命名版
│   │   ├── cundi-mantra.md                        # 准提咒与了凡四训（行持）
│   │   ├── 准提咒与了凡四训.md                       # 同文件中文命名版
│   │   ├── vegetarian-classical-basis.md          # 素食与五辛·公版经典依据
│   │   ├── jingangjing-wu-suo-zhu.md              # 金刚经·应无所住而生其心
│   │   ├── dashizhi-nianfo-perfect-penetration.md # 大势至菩萨念佛圆通章
│   │   ├── tanjing-neng-sheng-wanfa.md            # 六祖坛经·何期自性能生万法
│   │   └── Heart Sūtra Key Passages.md            # 心经·关键段落（英文）
│   │
│   └── taoism/                        # 道家经典
│       ├── daodejing-ch5.md                       # 道德经第五章（橐籥·反者道之动·多闻数穷）
│       ├── 道德经第五章-版本对照.md                   # 同文件中文命名版
│       └── baiziming-hundred-character-tablet.md  # 吕祖百字铭（养气忘言守·降心为不为）
│
├── practice-records/                  ← 社区贡献的真实实践记录（最核心的内容）
│   │
│   ├── TEMPLATE.md                                # 实践记录模板
│   ├── 辟谷-服气法亲身实证.md                        # 🟡 辟谷服气个人实践记录（带危险警示）
│   ├── 素食-十年亲身实证.md                          # 🟡 素食十年个人实践记录（带营养提示）
│   ├── vegetarian-practice.md                     # 同文件英文版
│   ├── 茶与食物属性-实践记录.md                      # 🟡 茶与食物属性（带边界，不开方）
│   └── tea-food-properties-practice.md            # 同文件英文版
│
├── cantonese/                         ← 粤语诵读层
│   │
│   ├── cantonese-recitation-index.md              # 粤语诵读索引（诵读与觉知的结合）
│   ├── cantonese-粤语诵读层.md                      # 粤语诵读层的设计说明
│   ├── 准提咒粤语版202606022146_1780494713.m4a      # 准提咒·粤语诵读音档
│   └── 心经粤语版202606032257_1780498671.m4a        # 心经·粤语诵读音档
│
├── SQ/                                ← 灵商（Spiritual Intelligence）研究延伸
│   │
│   ├── README.md                                  # SQ 文件夹总览、与主项目的关系、如何参与
│   ├── spiritual-intelligence-reference.md        # ⚫ 西方 SQ 著作·学者·论文参考书目
│   ├── spiritual-intelligence-scales.md           # ⚫ SQ21 / SISRI-24 / PSI 三大量表详解
│   ├── eastern-sq-scale-design.md                 # 🔴 基于中医与儒释道原理的五维灵商量表设计方案
│   └── RESOURCE-HUB.md                            # 🌐 社区资源收集中心（小红书/Reddit/论文提交入口）
│
├── open-questions/                    ← 开放问题汇总，等待社区共同探索
│   │
│   └── .gitkeep                                   # 占位文件，待社区填充
│       # 已有问题线索（来自 README.md 第九节）：
│       #   走极端的安全边界 / 现代六尘与古代的差异 / 转不动的触 /
│       #   智能体陪伴的有效边界 / 见修行的次序
│
├── conversation-logs/                 ← 对话记录存档（Reddit 等平台的真实对话）
│   │
│   ├── reddit-dialogue-awakening.md               # Reddit 对话：觉知与开悟
│   └── reddit-dialogue-door-reversal.md           # Reddit 对话：门的反转
│
└── tools/                             ← 智能体辅助工具和提示词
    │
    └── prompts/
        ├── awareness-companion-v2-plan.md          # 觉知陪伴智能体 v2 计划书
        ├── awareness-companion-v2-prompt.md        # 觉知陪伴 v2 系统提示词（英文）
        ├── crisis-resources.md                     # 危机资源副本（与根目录同步）
        ├── 觉知陪伴智能体-v2系统提示词.md             # 同文件中文版
        └── 觉知陪伴智能体-v2计划书.md                 # 同文件中文版
```

---

## 体系四层结构速览

| 层 | 核心文档 | 一句话 |
|----|---------|--------|
| **魂** Soul | `docs/PHILOSOPHY-八字心法.md` | 快乐·动手·开源·分享——为什么走这条路 |
| **理** Principle | `docs/PRINCIPLE-回归与转换.md` | 一切方法 = 回归 + 转换；转换不是「给糖」 |
| **境** State | `docs/AWARENESS-觉知与六触.md` | 看见六触在转，看着的那个始终在 |
| **术** Technique | `practice-records/` + `classics/` | 转触、辟谷、素食、茶——具体入口 |

---

## 文件命名规则

| 类型 | 命名格式 | 示例 |
|------|---------|------|
| 经典摘录 | `经典名-关键词.md` | `surangama-six-faculties.md` |
| 经典摘录（中文名） | `经典全名-章节描述.md` | `黄帝内经-上古天真论关键段落.md` |
| 体系核心文档 | `层级分类-中文描述.md` | `AWARENESS-觉知与六触.md` |
| 实践记录（实名） | `github用户名.md` | `coding158.md` |
| 实践记录（匿名） | `anonymous-编号.md` | `anonymous-001.md` |
| SQ 研究资料 | `英文关键词-描述.md` | `spiritual-intelligence-scales.md` |
| 开放问题 | `问题关键词.md` | `zhuan-chu-limits.md` |
| 智能体提示词 | `agent名-v版本-内容.md` | `awareness-companion-v2-prompt.md` |
| 音视频资源 | `内容描述+时间戳+唯一ID.扩展名` | `准提咒粤语版202606022146_1780494713.m4a` |

---

## 来源层级标注规则

所有文件头部须标注内容所属层级，与项目核心提示词（CLAUDE.md）一致：

| 标记 | 含义 | 示例 |
|------|------|------|
| 🟢 | 公版经典引证，有原典出处可查 | `classics/` 下所有经典摘录 |
| 🟡 | 个人实践记录，非普适 | `practice-records/` 下所有文件 |
| 🔴 | 一家之言 / 待考 / 理论构想 | `SQ/eastern-sq-scale-design.md` |
| ⚫ | 第三方参考整理，非本项目知识库原有范畴 | `SQ/spiritual-intelligence-reference.md` |

---

## 贡献到哪里？

| 你想贡献的内容 | 放在哪里 |
|-------------|---------|
| 自己的实践记录 | `practice-records/` |
| 经典原文的注解或白话 | `classics/tcm/` 或 `classics/buddhism/` 或 `classics/taoism/` |
| 推荐一本书 | 在 `reading-list.md` 中补充 |
| 对某个开放问题的回应 | `open-questions/` 对应文件，或直接在 Discussions |
| AI 辅助工具或提示词 | `tools/prompts/` |
| 粤语诵读或其他语言的经典诵读 | `cantonese/` 或新建对应语言文件夹 |
| SQ 相关：资料、论文、论坛帖子 | `SQ/RESOURCE-HUB.md` 按模板提交 |
| SQ 相关：量表条目评审、实证研究 | `SQ/` 下提 Issue 或 PR |
| 不确定放哪里 | 直接发到 Discussions，维护者帮你找位置 |

---

> 不确定放哪里，就直接发到 Discussions。
> 位置可以调整，记录不能丢。

---

## 本地 vs GitHub 远程仓库 · 差异对照

> 远程仓库：https://github.com/coding158/mind-body-health
> 对比时间：2026-06-09
> 状态：本地文件已更新，等待上传至 GitHub

### 🔵 本地新增 · 远程没有（待上传）

| 路径 | 说明 |
|------|------|
| `CLAUDE.md` | 觉知陪伴 v2 系统提示词（智能体根配置） |
| `PHILOSOPHY-八字心法.md` | 八字心法根目录副本（`docs/` 下为主文件） |
| `agents/AGENT-觉知陪伴智能体.md` | 智能体路由与部署说明 |
| `agents/awareness-companion-v2-prompt.md` | 英文版 v2 提示词 |
| `agents/crisis-resources.md` | 智能体专用危机资源副本 |
| `agents/觉知陪伴智能体-v2计划书.md` | v2 中文计划书 |
| `cantonese/准提咒粤语版202606022146_1780494713.m4a` | 准提咒粤语诵读音档 |
| `cantonese/心经粤语版202606032257_1780498671.m4a` | 心经粤语诵读音档 |
| `classics/buddhism/dashizhi-nianfo-perfect-penetration.md` | 大势至菩萨念佛圆通章 |
| `classics/buddhism/jingangjing-wu-suo-zhu.md` | 金刚经·应无所住 |
| `classics/buddhism/tanjing-neng-sheng-wanfa.md` | 六祖坛经·能生万法 |
| `classics/tcm/reading-list-tcm-path.md` | 中医学习路径（英文） |
| `classics/tcm/reading-list-中医学习路径.md` | 中医学习路径（中文） |
| `classics/taoism/baiziming-hundred-character-tablet.md` | 吕祖百字铭 |
| `docs/PRINCIPLE-suo-and-zhuan.md` | 回归与转换·英文补充 |
| **`SQ/`** 整文件夹（5 个文件） | 🔴 **本次最大新增**——灵商研究资料库 |

### 🟡 本地更新 · 远程版为旧版（待覆盖）

| 文件 | 变更类型 |
|------|---------|
| `STRUCTURE.md` | 🔄 大幅重写：新增 `SQ/`、`conversation-logs/`、`CLAUDE.md`、`agents/`、`cantonese/`（含音频）、道家经典、粤语等板块；新增体系结构速览、来源层级规则、空白文件夹 `.gitkeep` 说明；新增本差异对照表 |

### 🟠 远程有 · 本地没有

| 路径 | 说明 | 处理建议 |
|------|------|---------|
| `conversation-logs/reddit-dialogue-awakening.md` | Reddit 觉知对话记录 | ⬅️ 从远程拉取到本地 |
| `conversation-logs/reddit-dialogue-door-reversal.md` | Reddit 反转对话记录 | ⬅️ 从远程拉取到本地 |
| `classics/道德经第五章-版本对照.md` | ⚠️ **放错位置**：在 `classics/` 根目录下，正确位置是 `classics/taoism/daodejing-ch5.md` | 🔧 上传后移到 `classics/taoism/`，删除根目录的冗余副本 |
| `tools/prompts/crisis-resources.md` | 危机资源副本 | 保留（与根目录 `crisis-resources.md` 同步维护） |
| 部分 `.gitkeep` 文件 | 空白文件夹占位 | 保留 |

### 🟢 本地缺少的 .gitkeep 文件（需补）

以下目录在上传新文件前需加 `.gitkeep` 以免空目录被 Git 忽略：

| 目录 | 本地状态 |
|------|---------|
| `agents/` | 有内容，不需要 `.gitkeep` |
| `classics/buddhism/` | 有内容，已有 `.gitkeep`（远程） |
| `classics/tcm/` | 有内容，已有 `.gitkeep`（远程） |
| `open-questions/` | 空（只有 `.gitkeep`），保留 |
| `tools/prompts/` | 有内容，已有 `.gitkeep`（远程） |

---

## 更新日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-06-09 | v1.1 | 全面重构：新增 SQ/、conversation-logs/、CLAUDE.md、agents/、cantonese/（含音频）、道家经典、中医学习路径等板块；新增体系结构速览、来源层级标注规则；新增本地 vs 远程差异对照表 |
| — | v1.0 | 初始版本（仓库首次上传时创建） |

> **最后更新**：2026-06-09
> **远程仓库**：[`coding158/mind-body-health`](https://github.com/coding158/mind-body-health)
> **关联文档**：[`README.md`](README.md) · [`CONTRIBUTING.md`](CONTRIBUTING.md) · [`CLAUDE.md`](CLAUDE.md)
