# 提取工作流说明 · How the Extraction Works

> 从《新时代与灵修合集V1.1典藏版.exe》到 GitHub 可查的领域化知识引擎——
> 完整流程文档，方便他人参与和复现。

---

## 概览

```
┌─────────────────┐
│  V1.1典藏版.exe  │  55MB Windows 电子书阅读器，内嵌 400+ 本书
└────────┬────────┘
         │ extract_all_books.py  ── zlib 解压 → HTML → Markdown
         ▼
┌─────────────────┐
│  444 本 MD 全文  │  130MB → 本地 Obsidian Vault（私有，外部路径）
└────────┬────────┘
         │ generate_catalog.py   ── frontmatter → 版权分级
         │ generate_v2_catalog.py ── Skill 域映射 → V2.0 总目
         ▼
┌─────────────────┐
│  公开元数据目录   │  classics/xinshidai_catalog/身心灵经典库-V2.0.md
│  (无全文，合规)   │  412 本 → 5 个 Skill 域 → A/B/C 版权档
└─────────────────┘
```

---

## 前置条件

### 你需要有

| 项目 | 说明 |
|---|---|
| `新时代与灵修合集V1.1典藏版.exe` | 放在 `classics/` 下（已在 .gitignore 中排除）。<br>**如何获取**：在百度云盘、微信公众号等平台搜索「新时代与灵修合集 V1.1 典藏版」即可找到。该文件由 oh·灵魂网 (www.osoul.cn) 于 2010 年制作发布，纯公益免费传播。 |
| Python 3.8+ | 建议安装 `beautifulsoup4`（`pip install beautifulsoup4`） |
| 磁盘空间 | ~200 MB（解压后的 MD + 图片） |

### 文件位置

```
仓库/
├─ classics/
│   ├─ 新时代与灵修合集V1.1典藏版.exe   ← 源文件（不要提交！已在 .gitignore）
│   ├─ 合集总目录.md                    ← V1.1 原版目录（已转录）
│   └─ xinshidai_catalog/
│       └─ README.md                    ← V2.0 领域化总目（脚本生成）
├─ tools/
│   ├─ dump_windows.py                  ← 探测 EXE 内部结构
│   ├─ extract_ebook.py                 ← 逐本提取（Win32 API 方式，⚠️ 备用，需管理员权限，可能被杀软误报）
│   ├─ extract_all_books.py             ← ⭐ 批量提取（zlib 解压方式，主要用这个）
│   ├─ generate_catalog.py              ← 生成版权分级目录
│   └─ generate_v2_catalog.py           ← 生成 V2.0 领域化总目
└─ <本地 Obsidian Vault>/              ← 444 本 MD 全文（外部路径，不提交）
```

---

## Step 1：解压 EXE → Markdown

### 原理

`新时代与灵修合集V1.1典藏版.exe` 是一个 Windows 壳程序（基于 eBook 阅读器框架）。它的 overlay 区嵌入了大量 zlib 压缩块，每个块是一本书的 HTML。

`extract_all_books.py` 做了什么：
1. 读取 EXE 的 overlay 区域（从偏移 0x3DC00 开始）
2. 扫描 zlib 魔数（`0x78 0xda` / `0x78 0x9c`），逐个解压
3. 根据首字节分类：HTML（`<html`）、JPG（`0xFF 0xD8`）、PNG（`0x89 P N G`）等
4. 解析 EXE 内嵌索引（第一块），获取 400+ 本书的书名+路径
5. 将 HTML 匹配到索引中的书名
6. `html_to_md()`：BeautifulSoup 剥离标签 → 检测章节标题 → 生成带目录的 Markdown
7. 提取 frontmatter（title / category / source / tags）写入文件头

### 运行

```bash
cd 仓库根目录
python tools/extract_all_books.py
```

输出到本地 Obsidian Vault 路径（可在脚本中修改 `OUT` 变量）。

**耗时**：约 1-2 分钟。

**输出结构**：
```
<本地 Obsidian Vault>/
├─ 与神对话/
│   ├─ 1、与上帝交谈.md
│   ├─ 2、与神对话Ⅱ.md
│   └─ ...
├─ 奥修文集/
│   ├─ 002-老子道德经.md
│   └─ ...
├─ 赛斯资料/
│   └─ ...
└─ README.md    ← 自动生成的总目录
```

---

## Step 2：生成公开元数据目录

```bash
# 版权分级版（412 本 → A/B/C）
python tools/generate_catalog.py

# V2.0 领域化版（412 本 → 五个 Skill 域）
python tools/generate_v2_catalog.py
```

两个脚本都输出到 `classics/xinshidai_catalog/身心灵经典库-V2.0.md`。

---

## 版权分级规则

参见 `tools/generate_catalog.py` 中的分类逻辑：

### 🟢 A 类：公版经典

**判定方式**：精确标题白名单匹配（`PUBLIC_DOMAIN_TITLES`）

```python
PUBLIC_DOMAIN_TITLES = {
    '金刚经', '心经', '六祖坛经', '地藏经', '药师经',
    '法华经', '楞严经',
    '道德经', '庄子', '黄帝内经',
    '碧岩录', '信心铭',
    '480位禅宗大德悟道因缘（上）',
    '480位禅宗大德悟道因缘（下）',
    '薄伽梵歌', '巴巴吉传',
}
```

**为什么不是关键词？** "奥修解金刚经"包含"金刚经"但版权属于奥修。所以只信任精确匹配的原文标题。

### 🟡 B 类：古籍整理/不确定

**判定方式**：`B_CLASSIFIED_TITLES` 特例列表

```python
B_CLASSIFIED_TITLES = {
    '一个科学者研究佛经的报告',   # 1946 年，作者已故超 50 年
    '和谐拯救危机系列二文字版',   # 公益讲记
    '给一万个佛的一百个故事',     # 传统佛典故事复述
}
```

### 🔴 C 类：现代版权期内

**判定方式**：分类归 C → 版权关键词触发 → 兜底

- 整个分类归 C（如 奥修文集、赛斯资料、与神对话 等 25 个分类）
- 作者/关键词触发（如 "南怀瑾"、"托利"、"圣帕布帕德" 等）
- 就算归类到了 C，如果书名在 A 类白名单中，仍会穿透为 A

---

## Skill 域映射规则

参见 `tools/generate_v2_catalog.py`：

### 分类级映射（`CATEGORY_TO_SKILL`）

V1.1 的 30 个原始分类，绝大多数直接映射到一个 Skill 域：

| V1.1 分类 | V2.0 Skill 域 |
|---|---|
| 奥修文集、藏密、佩玛丘卓、瑜伽资料 | 佛学与禅修 |
| 第四道 | 道家生命学 |
| 医学养生类 | 中医养生 |
| 与神对话、欧林系列、赛斯资料、奇迹课程…（16 个） | 新时代与灵性成长 |
| 克里希纳穆提、少有人走的路、肯·威尔伯、生命花园… | 心理成长 |

### 书名级覆盖（`TITLE_SKILL_OVERRIDE`）

综合类一/二的每本书逐本映射到具体域。

---

## 常见问题

### Q: 为什么不要提交全文到 GitHub？

版权。400+ 本书中 404 本是现代版权期作品（奥修、南怀瑾、托利、张德芬、赛斯等）。GitHub 对 DMCA 投诉响应迅速，全文公开可能导致仓库下架。

详见 `docs/STRATEGY-内容架构与版权策略.md` 的详细分析。

### Q: 那我怎么读这些书？

1. 本地 Obsidian Vault → 打开外部路径（即 Step 1 解压输出目录）
2. 推荐购买正版纸质书 / 电子书
3. 本仓库的 `xinshidai_catalog/` 提供索引和读书笔记

### Q: 工具报错怎么办？

1. **缺少 beautifulsoup4**：`pip install beautifulsoup4`
2. **找不到 EXE 文件**：确认 `classics/` 下有 `新时代与灵修合集V1.1典藏版.exe`
3. **输出路径不存在**：确认 Obsidian Vault 目录存在
4. **编码错误**：在 Windows 下运行时用 `PYTHONIOENCODING=utf-8` 前缀

### Q: 我可以增加新书吗？

可以。在当前架构下增加一本书的步骤：
1. 将书籍转为 Markdown 格式，存入本地 Obsidian Vault 的对应分类目录
2. 添加 frontmatter：
   ```yaml
   ---
   title: "书名"
   category: "分类名"
   source: "来源说明"
   tags: [标签1, 标签2]
   ---
   ```
3. 在 `generate_v2_catalog.py` 的 `TITLE_SKILL_OVERRIDE` 中添加映射
4. 重跑 `python tools/generate_v2_catalog.py`

---

## 架构演进史

| 版本 | 时间 | 形态 | 内容 |
|---|---|---|---|
| V1.0 | 2010 | Windows .exe | 原始电子书阅读器 |
| V1.1 | 2010.04 | Windows .exe | 更新版，修正乱码和图片 |
| 提取版 | 2026.06 | MD 文件（本地） | 从 EXE 解压为 444 个 Markdown |
| V2.0 | 2026.06 | 领域化目录（公开）+ 全文（私有） | 按 5 个 Skill 域重组，版权分级 |

---

## 相关文件索引

| 文件 | 用途 |
|---|---|
| `CLAUDE.md` | 觉知陪伴智能体核心提示词 |
| `agents/Router.md` | Skill 路由调度规则 |
| `agents/Zen-Master.md` | 佛学禅修域 Skill 定义 |
| `agents/Dao-Master.md` | 道家生命学域 Skill 定义 |
| `agents/TCM-Master.md` | 中医养生域 Skill 定义 |
| `agents/NewAge-Master.md` | 新时代灵性域 Skill 定义 |
| `agents/Psychology-Master.md` | 心理成长域 Skill 定义 |
| `classics/合集总目录.md` | V1.1 原版目录（历史档案） |
| `classics/xinshidai_catalog/身心灵经典库-V2.0.md` | V2.0 领域化总目（最终产出） |
| `docs/STRATEGY-内容架构与版权策略.md` | 内容架构与版权策略 |
| `.claude/plans/xinshidai-v2-strategy.md` | 一期计划 |
| `.claude/plans/next-phase-review-2026-06-15.md` | 二期审视与计划 |
