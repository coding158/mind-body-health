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
├── classics/
│   # 经典原文摘录与注解（仅收录公版无版权内容）
│   │
│   ├── tcm/
│   │   # 中医经典相关
│   │   ├── huangdi-neijing-excerpts.md   # 黄帝内经关键章节摘录与白话注解
│   │   ├── shanghan-lun-excerpts.md      # 伤寒论相关段落摘录
│   │   └── references.md                 # 中医经典引用来源与免费获取链接
│   │
│   └── buddhism/
│       # 佛理经典相关
│       ├── surangama-key-passages.md     # 楞严经核心段落（六触、转触相关）与注解
│       ├── liao-fan-key-passages.md      # 了凡四训关键段落与现代实践对照
│       ├── diamond-sutra-excerpts.md     # 金刚经相关段落摘录
│       └── references.md                 # 佛经引用来源与 CBETA 链接
│
├── reading-list.md
│   # 推荐书目清单
│   # 包含中医、佛理、现代觉察、儒释道融合四个分类
│   # 注明版权状态，不收录受版权保护的原文
│
├── practice-records/
│   # 社区贡献的真实实践记录（最核心的内容）
│   │
│   ├── TEMPLATE.md                       # 实践记录模板，支持文字/录音/视频/图片/匿名五种方式
│   ├── anonymous-001.md                  # 匿名贡献者记录（由维护者整理编号）
│   └── [github-username].md              # 实名贡献者记录（以 GitHub 用户名命名）
│
├── open-questions/
│   # 开放问题汇总，等待社区共同探索
│   │
│   ├── README.md                         # 开放问题总览，来自主文档第九节
│   ├── extreme-boundaries.md             # 走极端的安全边界在哪里？
│   ├── modern-vs-ancient-liuchen.md      # 现代六尘和古代六尘的本质差异
│   ├── zhuan-chu-limits.md               # 有没有转不动的触？
│   └── ai-companion-limits.md            # 智能体陪伴的有效边界在哪里？
│
└── tools/
    # 智能体辅助工具和提示词（可选，逐步建立）
    │
    ├── README.md                          # 工具说明，如何用 AI 辅助实践记录和经典对照
    ├── prompts/
    │   ├── classic-cross-reference.md    # 提示词：用 AI 在经典中找对应段落
    │   ├── practice-analysis.md          # 提示词：用 AI 分析实践记录中的模式
    │   └── zhuan-chu-guide.md            # 提示词：用 AI 辅助转触练习的引导
    └── ccr-config-example.json           # CCR 路由配置示例（接入多个 LLM 的参考配置）
```

---

## 文件命名规则

| 类型 | 命名格式 | 示例 |
|------|---------|------|
| 经典摘录 | `经典名-关键词.md` | `surangama-key-passages.md` |
| 实践记录（实名） | `github用户名.md` | `coding158.md` |
| 实践记录（匿名） | `anonymous-编号.md` | `anonymous-001.md` |
| 开放问题 | `问题关键词.md` | `zhuan-chu-limits.md` |
| 提示词 | `用途说明.md` | `practice-analysis.md` |

---

## 贡献到哪里？

| 你想贡献的内容 | 放在哪里 |
|-------------|---------|
| 自己的实践记录 | `practice-records/` |
| 经典原文的注解或白话 | `classics/tcm/` 或 `classics/buddhism/` |
| 推荐一本书 | 在 `reading-list.md` 中补充 |
| 对某个开放问题的回应 | `open-questions/` 对应文件，或直接在 Discussions |
| AI 辅助工具或提示词 | `tools/prompts/` |
| 不确定放哪里 | 直接发到 Discussions，维护者帮你找位置 |

---

> 不确定放哪里，就直接发到 Discussions。
> 位置可以调整，记录不能丢。
