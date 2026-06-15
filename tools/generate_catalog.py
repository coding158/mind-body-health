#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从本地 xinshidai_library 提取 frontmatter → 生成公开元数据目录
输出：classics/xinshidai_catalog/
"""

import os, re, argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LOCAL = os.path.join(REPO_ROOT, 'classics', 'xinshidai_library')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '..', 'classics', 'xinshidai_catalog')

# ── 版权档位判定 ──
# 🔴 优先级 1：整个分类属于现代版权期
MODERN_COPYRIGHT_CATEGORIES = {
    '与神对话', '赛斯资料', '奇迹课程资料', '欧林系列',
    '光的课程', '克里昂讯息', '吸引力法则', '少有人走的路',
    '托尔特克(含唐望系列)', '第四道', '阿米系列',
    '钻石途径', '透特', '宇宙之光&约书亚',
    '生命花园', '伊曼纽三本',
    '张德芬&埃克哈特·托利',
    '医学养生类',
    '奥修文集',
    '克里希纳穆提',
    '佩玛丘卓',
    '肯·威尔伯', '苏菲亚布朗', '乔斯坦贾德',
    '布莱恩·魏斯', '狄巴克·乔布拉', '门罗',
    '藏密',
    '瑜伽资料',          # 大部分是 ISKCON 现代译著，版权期内
    '综合类一',           # 绝大部分是现代/当代作品
    '综合类二',           # 绝大部分是现代/当代作品
}

# 🔴 优先级 2：作者名/关键词触发 → C
MODERN_COPYRIGHT_KEYWORDS = (
    '奥修', '南怀瑾', '克里希那穆提', '埃克哈特·托利', '张德芬',
    '吴清忠', '马悦凌', '刘力红', '李阳波', '海灵格',
    '胡因梦', '露易丝·海', '杰克·康菲尔德',
    '盛噶仁波切', '罗桑伦巴', '朵琳·芙秋',
    '陈胜英', '高国新', '许添盛', '袁一平',
    '宋世鹏', '李耳纳', '大卫·霍夫梅斯特',
    # ISKCON / 瑜伽版权
    '圣帕布帕德', '奎师那知觉', '帕布帕德', 'ISKCON',
    '巴克提吠丹塔', 'Bhaktivedanta',
    # B 类修正：这些是现代作品被错判为 B 的
    '平常禅', '十字路口的圣经', '我有死亡经验', '神圣经验',
    '刀光剑影话禅宗',
    # 更多现代作者
    '尼尔·唐纳德·沃尔什', '拜伦·凯蒂', '保罗·费里尼',
    '葛瑞·雷纳', '唐望', '卡斯塔尼达', '门罗',
    '艾兹拉·贝达', 'Charlotte Joko Beck',
    '阿玛斯', '佩玛',
)

# 🟢 A 类：确认真公版经典标题（非解说、非译注）
# 只用于分类判定后的穿透，因此不设模糊关键词
PUBLIC_DOMAIN_TITLES = {
    # 大乘佛经原文（非解说版）
    '金刚经', '心经', '六祖坛经', '地藏经', '药师经',
    '法华经', '楞严经',
    # 道家原文
    '道德经', '庄子',
    # 中医原文
    '黄帝内经',
    # 禅宗古典
    '碧岩录', '信心铭',
    '480位禅宗大德悟道因缘（上）',
    '480位禅宗大德悟道因缘（下）',
    # 印度古典原文（非 ISKCON 译注版）
    '薄伽梵歌',
    '巴巴吉传',
}

# 🟡 B 类特殊处理：虽然整类归 C，但个别有争议/过渡期的挑出来
B_CLASSIFIED_TITLES = {
    '一个科学者研究佛经的报告',   # 民国时期（1940s），作者已故超过50年
    '给一万个佛的一百个故事',     # 传统佛教故事的复述
    '和谐拯救危机系列二文字版',   # 公益讲记整理，非正式出版物
}

# 🔴 ISKCON 现代译著——书名含公版关键词（如"薄伽梵歌"），但译注有版权
ISKCON_TITLES = {
    '薄伽梵歌原义',       # Srila Prabhupada 翻译+注释，有版权
    '至尊人格神奎师那',   # ISKCON 出版物
    '至尊奥义书',         # 此版本为 ISKCON 译注版
}

def classify(title, category, author_hint=''):
    """A=公版 B=古籍整理/不确定 C=现代版权期
    判定顺序：B特例 → 分类归C → 公版标题白名单(穿透) → 版权关键词 → 兜底"""
    t = title + ' ' + author_hint

    # 0 B 类特例
    if title in B_CLASSIFIED_TITLES:
        return 'B'

    # 1 ISKCON 现代译著——书名含公版词但实为版权译注
    if title in ISKCON_TITLES:
        return 'C'

    # 2 整个分类归 C
    if category in MODERN_COPYRIGHT_CATEGORIES:
        # 但确认真公版原文允许穿透（白名单精确匹配，防奥修解说等误判）
        if title in PUBLIC_DOMAIN_TITLES:
            return 'A'
        return 'C'

    # 3 现代版权关键词（作者/书名/流派）
    for kw in MODERN_COPYRIGHT_KEYWORDS:
        if kw in t:
            return 'C'

    # 4 兜底 -> B（没有明确版权依据的，保守处理）
    return 'B'


def extract_frontmatter(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if not content.startswith('---'):
        return {}, content
    end = content.find('---', 3)
    if end == -1:
        return {}, content
    try:
        fm = parse_frontmatter(content[3:end])
    except Exception:
        return {}, content
    return fm or {}, content[end+3:]


def parse_frontmatter(text):
    """手工解析简单 YAML frontmatter，避免依赖 PyYAML"""
    result = {}
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or ':' not in line:
            continue
        key, _, val = line.partition(':')
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if val.startswith('[') and val.endswith(']'):
            inner = val[1:-1]
            if inner:
                result[key] = [x.strip().strip('"').strip("'") for x in inner.split(',')]
            else:
                result[key] = []
        else:
            result[key] = val
    return result


def main(local_path=None):
    local = local_path or DEFAULT_LOCAL
    os.makedirs(OUT, exist_ok=True)
    catalog = []

    for root, dirs, files in os.walk(local):
        for fn in files:
            if not fn.endswith('.md') or fn == 'README.md':
                continue
            fp = os.path.join(root, fn)
            fm, body = extract_frontmatter(fp)
            if not fm:
                continue
            title = fm.get('title', fn)
            category = fm.get('category', '')
            tags = fm.get('tags', [])
            tier = classify(title, category)

            # 只取第一段正文摘要（跳过标题、目录、导航链接、HTML 残留）
            summary = ''
            for line in body.strip().split('\n'):
                line = line.strip()
                if not line or len(line) < 15:
                    continue
                if line.startswith('#') or line.startswith('['):
                    continue
                if line.startswith('- [') or line.startswith('> '):
                    continue
                # 跳过 HTML 残留（HTMLBUILERPART, ebook, language, Theme 等）
                if any(bad in line for bad in ('HTMLBUILERPART', '[ebook]', '[language]',
                                                 '[Theme]', 'tree.dat', '上一页', '下一页',
                                                 '上一篇', '下一篇')):
                    continue
                # 跳过含超长省略号和页码的 TOC 行
                if re.search(r'[．…\.]{4,}', line):
                    continue
                summary = line[:120]
                break

            catalog.append({
                'title': title,
                'category': category,
                'tier': tier,
                'tags': tags,
                'summary': summary,
            })

    # 按分类排序输出
    catalog.sort(key=lambda x: (x['category'], x['title']))

    # ── 写 README ──
    tiers = {'A': [], 'B': [], 'C': []}
    for item in catalog:
        tiers[item['tier']].append(item)

    readme = [
        '# 新时代与灵修合集 — 公开元数据目录',
        '',
        '> 📖 全文（444 本）仅存于本地 Obsidian，不公开上传',
        '> 📋 本目录只提供：书名、作者、分类、标签、版权档位',
        f'> 🔗 本地库路径：`{local}`',
        '',
        '## 版权档位说明',
        '',
        '| 档位 | 说明 | 公开 GitHub | 本目录收录 |',
        '|---|---|---|---|',
        '| 🟢 A | 公版经典（佛经/道家/印度经典） | ✅ 可传原文 | 元数据 |',
        '| 🟡 B | 古籍现代整理/不确定 | ⚠️ 谨慎 | 元数据 |',
        '| 🔴 C | 现代版权期内 | ❌ 不传全文 | 元数据 |',
        '',
        f'统计：A={len(tiers["A"])} B={len(tiers["B"])} C={len(tiers["C"])} 共 {len(catalog)} 本',
        '',
        '---',
        '',
    ]

    # 按档位输出清单
    for tier_code, tier_name, emoji in [('A', '公版经典', '🟢'), ('B', '古籍整理/不确定', '🟡'), ('C', '现代版权期', '🔴')]:
        if not tiers[tier_code]:
            continue
        readme.append(f'## {emoji} {tier_name}（{len(tiers[tier_code])} 本）')
        readme.append('')
        last_cat = ''
        for item in tiers[tier_code]:
            if item['category'] != last_cat:
                last_cat = item['category']
                readme.append(f'### {last_cat}')
                readme.append('')
            tags_str = ', '.join(item['tags'][:5]) if item['tags'] else ''
            readme.append(f'- **{item["title"]}**  `{tags_str}`')
            if item['summary']:
                readme.append(f'  > {item["summary"]}')
        readme.append('')

    with open(os.path.join(OUT, 'README.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(readme))

    print(f'OK: {OUT}/README.md')
    print(f'   A={len(tiers["A"])} B={len(tiers["B"])} C={len(tiers["C"])} total={len(catalog)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='从 xinshidai_library 生成版权分级元数据目录')
    parser.add_argument('--local', default=DEFAULT_LOCAL,
                        help=f'xinshidai_library 路径（默认: {DEFAULT_LOCAL}）')
    args = parser.parse_args()
    main(local_path=args.local)
