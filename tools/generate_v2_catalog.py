#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从本地 xinshidai_library 生成 V2.0 领域化总目
按五个 Master Skill 域重组，输出到 classics/xinshidai_catalog/身心灵经典库-V2.0.md
"""

import os, re, argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LOCAL = os.path.join(REPO_ROOT, 'classics', 'xinshidai_library')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '..', 'classics', 'xinshidai_catalog')

# ── 版权分类规则：全部从 generate_catalog.py 导入 ──
# generate_catalog.py 是版权判定的单一权威来源。
# 增删公版标题、修改版权关键词或分类规则时，只改 generate_catalog.py 即可——v2 自动同步。
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_catalog import (
    MODERN_COPYRIGHT_CATEGORIES, MODERN_COPYRIGHT_KEYWORDS,
    PUBLIC_DOMAIN_TITLES, ISKCON_TITLES, B_CLASSIFIED_TITLES,
    classify, extract_frontmatter, parse_frontmatter,
)

# ── V1.1 分类 → V2.0 Skill 域映射 ──
CATEGORY_TO_SKILL = {
    # 佛学禅修域
    '奥修文集':            ['佛学与禅修'],
    '藏密':                ['佛学与禅修'],
    '佩玛丘卓':            ['佛学与禅修', '心理成长'],
    '瑜伽资料':            ['佛学与禅修'],  # 薄伽梵歌等

    # 道家生命学域
    '第四道':              ['道家生命学'],

    # 中医养生域
    '医学养生类':          ['中医养生'],

    # 新时代灵性域
    '与神对话':            ['新时代与灵性成长'],
    '欧林系列':            ['新时代与灵性成长'],
    '赛斯资料':            ['新时代与灵性成长'],
    '奇迹课程资料':        ['新时代与灵性成长'],
    '光的课程':            ['新时代与灵性成长'],
    '克里昂讯息':          ['新时代与灵性成长'],
    '吸引力法则':          ['新时代与灵性成长'],
    '宇宙之光&约书亚':     ['新时代与灵性成长'],
    '透特':                ['新时代与灵性成长'],
    '门罗':                ['新时代与灵性成长'],
    '托尔特克(含唐望系列)': ['新时代与灵性成长'],
    '阿米系列':            ['新时代与灵性成长'],
    '狄巴克·乔布拉':       ['新时代与灵性成长'],
    '苏菲亚布朗':          ['新时代与灵性成长'],
    '伊曼纽三本':          ['新时代与灵性成长'],
    '布莱恩·魏斯':         ['新时代与灵性成长'],

    # 心理成长域
    '克里希纳穆提':        ['心理成长'],
    '少有人走的路':        ['心理成长'],
    '肯·威尔伯':          ['心理成长'],
    '生命花园':            ['心理成长'],
    '乔斯坦贾德':          ['心理成长'],
    '钻石途径':            ['心理成长', '新时代与灵性成长'],

    # 跨域
    '张德芬&埃克哈特·托利': ['心理成长', '新时代与灵性成长'],

    # 综合类 → 按书名内容推断
    '综合类一':            [],  # 运行时逐本推断
    '综合类二':            [],
}

# 综合类具体书名的 Skill 推断
TITLE_SKILL_OVERRIDE = {
    # 综合类一
    'NAMASTE生命喜悦的祈祷':         ['新时代与灵性成长'],
    '做你想做的人':                   ['心理成长'],
    '爱无止境':                       ['新时代与灵性成长'],
    '宝瓶同谋':                       ['新时代与灵性成长'],
    '妲妲与旯旯':                     ['新时代与灵性成长'],
    '觉醒的对话':                     ['新时代与灵性成长'],
    '莲花次第开放':                   ['佛学与禅修'],
    '平常禅：活出真实的自己':         ['佛学与禅修', '心理成长'],
    '朝向完全觉醒的生命之旅（李耳纳）': ['新时代与灵性成长'],
    '从未知中解脱':                   ['新时代与灵性成长'],
    '大自然的启示':                   ['新时代与灵性成长'],
    '法爱博客文集——学道问答录':      ['道家生命学'],
    '还我本来面目':                   ['心理成长', '新时代与灵性成长'],
    '海鸥乔纳森':                     ['心理成长'],
    '会心集':                         ['道家生命学'],
    '活出美好':                       ['心理成长'],
    '觉察 袁一平':                    ['佛学与禅修', '心理成长'],
    '觉悟的上主之师David Hoffmeister': ['新时代与灵性成长'],
    '接触能量':                       ['新时代与灵性成长'],
    '接纳不完美的自己':               ['心理成长'],
    '解读地球生命密码':               ['新时代与灵性成长'],
    '森林里的一棵树':                 ['佛学与禅修'],
    '神圣经验':                       ['新时代与灵性成长'],
    '神通的真假（节选）':             ['佛学与禅修'],
    '生活的艺术':                     ['佛学与禅修'],
    '生命的智慧':                     ['道家生命学'],
    '生命与意识的省思':               ['心理成长', '新时代与灵性成长'],
    '生命源理':                       ['道家生命学'],
    '生命之后的生命':                 ['新时代与灵性成长'],
    '十字路口的圣经':                 ['新时代与灵性成长'],
    '石晓蔚／阅读札记':               ['心理成长'],
    '死亡.奇迹.预言':                 ['新时代与灵性成长'],
    '死亡九分钟':                     ['新时代与灵性成长'],
    '天幕即将拉开':                   ['新时代与灵性成长'],
    '天堂教我的七堂课':               ['新时代与灵性成长'],
    '天堂物语（通灵资料）':           ['新时代与灵性成长'],
    '外星世界-我与外星人思维对话实录（宋世鹏）': ['新时代与灵性成长'],
    '万能钥匙(世界上最神奇的24堂课)':  ['心理成长', '新时代与灵性成长'],
    '未来6000年':                     ['新时代与灵性成长'],
    '我有死亡经验':                   ['新时代与灵性成长'],
    '相约星期二':                     ['心理成长'],
    '心的出路':                       ['心理成长'],
    '心灵成长':                       ['心理成长'],
    '心灵鸡汤珍藏本':                 ['心理成长'],
    '心灵教导（合一网页摘录）':       ['新时代与灵性成长'],
    '新时代新人生':                   ['新时代与灵性成长'],
    '新世纪纪扬升之光':               ['新时代与灵性成长'],
    '性理之道':                       ['道家生命学'],
    '修心录':                         ['道家生命学'],
    '许添盛医师演讲':                 ['新时代与灵性成长'],
    '雅比斯的祷告':                   ['新时代与灵性成长'],
    '一的法则':                       ['新时代与灵性成长'],
    '一个科学者研究佛经的报告':       ['佛学与禅修'],
    '一切如是（海灵格）':             ['心理成长'],
    '依心而活':                       ['新时代与灵性成长'],
    '意识课程':                       ['心理成长', '新时代与灵性成长'],
    '印度心灵大师的开悟之旅：心灵午夜密谈': ['新时代与灵性成长'],
    '鹰与玫瑰--一位灵媒的生命之旅':   ['新时代与灵性成长'],
    '拥舞生命潜能':                   ['心理成长'],
    '与天堂对话':                     ['新时代与灵性成长'],
    '与治疗天使同行':                 ['新时代与灵性成长'],
    '宇宙生命学':                     ['道家生命学'],
    '预知生命大蜕变':                 ['新时代与灵性成长'],
    '遇见100%的爱':                   ['心理成长'],
    '运作中的灵魂的奇迹日记':         ['新时代与灵性成长'],
    '詹姆斯的心路历程':               ['心理成长'],
    '正法慈航':                       ['佛学与禅修'],
    '终极旅程':                       ['新时代与灵性成长'],

    # 综合类二
    '露易丝·海－生命的重建':          ['心理成长'],
    '露易丝·海－启动心的力量':        ['心理成长'],
    '夏威夷疗法－O极限':              ['心理成长'],
    '夏威夷疗法－最简单的方式':        ['心理成长'],
    '巴夏－2027：来自巴夏的生命讯息':  ['新时代与灵性成长'],
    '巴夏－来自未来的生命讯息':        ['新时代与灵性成长'],
    '碧岩录':                         ['佛学与禅修'],
    '陈胜英－跨越前世今生':           ['新时代与灵性成长'],
    '陈胜英－生命不死':               ['新时代与灵性成长'],
    '刀光剑影话禅宗':                 ['佛学与禅修'],
    '朵琳·芙秋－灵疗 奇迹 光行者':    ['新时代与灵性成长'],
    '朵琳·芙秋－召唤天使':            ['新时代与灵性成长'],
    '高国新－破译圣经科学密码':       ['新时代与灵性成长'],
    '高国新－最后的谜题':             ['新时代与灵性成长'],
    '给一万个佛的一百个故事':         ['佛学与禅修'],
    '和谐拯救危机系列二文字版':       ['佛学与禅修'],
    '胡因梦－生命的不可思议':         ['心理成长'],
    '胡因梦－我的灵疗经验':           ['新时代与灵性成长'],
    '杰克·康菲尔德－狂喜之后':        ['佛学与禅修', '心理成长'],
    '杰克·康菲尔德－踏上心灵幽静':    ['佛学与禅修', '心理成长'],
    '看见真相的小男孩':               ['新时代与灵性成长'],
    '旷野的声音':                     ['新时代与灵性成长'],
    '盔甲骑士':                       ['心理成长'],
    '来自宇宙人的讯息':               ['新时代与灵性成长'],
    '灵程指引':                       ['新时代与灵性成长'],
    '灵魂的旅程':                     ['新时代与灵性成长'],
    '灵魂炼金之旅':                   ['新时代与灵性成长'],
    '论星体投射':                     ['新时代与灵性成长'],
    '玛雅的智慧':                     ['新时代与灵性成长'],
    '迈可资料1－心灵成长 地球生命课程': ['新时代与灵性成长'],
    '迈可资料2－心灵修炼 地球修道院': ['新时代与灵性成长'],
    '猫猫资料':                       ['新时代与灵性成长'],
    '能类另语':                       ['新时代与灵性成长'],
    '能量的光环':                     ['新时代与灵性成长'],
    '你可以不生气':                   ['佛学与禅修', '心理成长'],
    '你可以更靠近我——教孩子怎样看待生命与死亡': ['心理成长'],
    '念力的秘密':                     ['新时代与灵性成长'],
    '全然接受——18个放下忧虑的...':    ['佛学与禅修', '心理成长'],
    '人类的迁移':                     ['新时代与灵性成长'],
    '塞莱斯廷预言':                   ['新时代与灵性成长'],
    '塞莱斯廷预言Ⅱ ——第十种洞察力': ['新时代与灵性成长'],
    '水知道答案(附清晰图55张)':        ['新时代与灵性成长'],
    '牧羊少年奇幻之旅':               ['心理成长', '新时代与灵性成长'],
    '480位禅宗大德悟道因缘（上）':     ['佛学与禅修'],
    '480位禅宗大德悟道因缘（下）':     ['佛学与禅修'],
}

SKILL_DESCRIPTIONS = {
    '佛学与禅修':       '🧘 Zen-Master — 打坐、念佛、公案、无我、觉察 → `agents/Zen-Master.md`',
    '道家生命学':       '☯️ Dao-Master — 道德经、庄子、无为、辟谷、精气神 → `agents/Dao-Master.md`',
    '中医养生':         '🌿 TCM-Master — 子午流注、阴阳五行、体质、作息 → `agents/TCM-Master.md`',
    '新时代与灵性成长': '✨ NewAge-Master — 赛斯、与神对话、信念、宽恕、意识 → `agents/NewAge-Master.md`',
    '心理成长':         '🪞 Psychology-Master — 焦虑、关系、情绪、自我认知 → `agents/Psychology-Master.md`',
}

SKILL_FILE_MAP = {
    '佛学与禅修':       'Zen-Master',
    '道家生命学':       'Dao-Master',
    '中医养生':         'TCM-Master',
    '新时代与灵性成长': 'NewAge-Master',
    '心理成长':         'Psychology-Master',
}

EMOJI = {
    '佛学与禅修': '🧘', '道家生命学': '☯️', '中医养生': '🌿',
    '新时代与灵性成长': '✨', '心理成长': '🪞',
}


def get_skills(title, category):
    """获取一本书的 Skill 域归属"""
    # 先去前缀匹配（[全][节] 等）
    clean = re.sub(r'^\[[^\]]+\]', '', title).strip()
    if clean in TITLE_SKILL_OVERRIDE:
        return TITLE_SKILL_OVERRIDE[clean]
    if title in TITLE_SKILL_OVERRIDE:
        return TITLE_SKILL_OVERRIDE[title]
    cat_skills = CATEGORY_TO_SKILL.get(category, [])
    if cat_skills:
        return cat_skills
    return ['综合（待归类）']


def extract_summary(body):
    """提取第一段有意义正文，跳过标题、元数据、空行"""
    lines = body.strip().split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or len(line) < 15:
            continue
        # 跳过 Markdown 结构标记
        if line.startswith('#') or line.startswith('[') or line.startswith('- [') or line.startswith('> '):
            continue
        # 跳过 HTML 残留和各种导航
        if any(bad in line for bad in ('HTMLBUILERPART', '[ebook]', '[language]',
                                         '[Theme]', 'tree.dat', '上一页', '下一页',
                                         '上一篇', '下一篇', '-------------------',
                                         '****', '返回目录', '下一页', '上一页')):
            continue
        # 跳过 TOC 页码行
        if re.search(r'[．…\.]{4,}', line):
            continue
        # 跳过纯作者/出版信息行
        if re.match(r'^(作者|译者|出版社|出版|ISBN|著者|原著)[：:]', line):
            continue
        # 跳过乱码比例高的行（连续 ??? 或非法字符）
        if line.count('?') > 5 and len(line) < 40:
            continue
        if re.search(r'[�\x00-\x08\x0b\x0c\x0e-\x1f]', line):
            continue
        return line[:120]
    return ''


# ── 标签清洗：去除因 gen_tags() 关键词过泛导致的误标 ──
# 与 extract_all_books.py 的 CAT_TAGS 保持一致
CATEGORY_VALID_TAGS = {
    '与神对话':            {'灵性', '新时代', '基督教'},
    '奥修文集':            {'灵性', '禅修', '佛法', '哲学', '修行', '开悟'},
    '光的课程':            {'灵性', '能量', '新时代'},
    '奇迹课程资料':        {'奇迹课程', '灵性', '基督教'},
    '托尔特克(含唐望系列)': {'灵性', '修行', '新时代'},
    '克里希纳穆提':        {'哲学', '觉知', '心理学', '情绪', '关系'},
    '赛斯资料':            {'灵性', '通灵', '新时代', '生死'},
    '藏密':                {'佛法', '修行', '生死'},
    '瑜伽资料':            {'瑜伽', '灵性', '哲学'},
    '医学养生类':          {'养生', '健康', '道家'},
    '克里昂讯息':          {'通灵', '新时代', '灵性'},
    '吸引力法则':          {'灵性', '财富', '心理学', '成长'},
    '少有人走的路':        {'心理学', '成长', '情绪', '关系'},
    '生命花园':            {'关系', '心理学', '成长'},
    '第四道':              {'修行', '哲学', '心理学'},
    '门罗':                {'灵性', '通灵', '生死'},
    '阿米系列':            {'科幻', '灵性'},
    '欧林系列':            {'灵性', '新时代', '能量'},
    '佩玛丘卓':            {'佛法', '禅修', '心理学', '成长'},
    '肯·威尔伯':           {'哲学', '心理学', '灵性', '成长'},
    '苏菲亚布朗':          {'灵性', '通灵', '生死'},
    '乔斯坦贾德':          {'哲学', '心理学', '成长'},
    '布莱恩·魏斯':         {'灵性', '生死', '心理学'},
    '狄巴克·乔布拉':       {'灵性', '养生', '新时代'},
    '伊曼纽三本':          {'灵性', '新时代'},
    '透特':                {'通灵', '灵性', '新时代'},
    '钻石途径':            {'灵性', '心理学', '修行'},
    '张德芬&埃克哈特·托利': {'灵性', '心理学', '觉知', '情绪', '成长'},
    '宇宙之光&约书亚':     {'灵性', '新时代', '通灵'},
    '综合类一':            set(),
    '综合类二':            set(),
}

# 标签名统一映射
TAG_ALIASES = {
    '道教': '道家',
    '佛学': '佛法',
    '灵修': '灵性',
    '心理': '心理学',
}

def clean_tags(tags, category, title=''):
    """清除关键词过泛导致的误标，补全分类级标签"""
    valid = set(CATEGORY_VALID_TAGS.get(category, set()))
    cleaned = set()
    for t in tags:
        # 统一别名
        t = TAG_ALIASES.get(t, t)
        if not valid:
            # 未定义分类规则 → 保守保留，仅去除基督教
            if t == '基督教':
                continue
            cleaned.add(t)
        else:
            # 有分类规则 → 只保留在允许列表中的
            if t in valid:
                cleaned.add(t)
    # 补全分类级标签（如果前端缺失）
    for t in valid:
        if t in cleaned:
            continue
        # 不从已清洗列表中删除，由 CATEGORY_VALID_TAGS 决定
    return sorted(cleaned)[:8]


def guess_author(title, category, summary):
    """从书名/摘要推断作者"""
    # 按书名关键词推断
    author_map = {
        '奥修': '奥修 (Osho)', '克里希那穆提': '克里希那穆提 (J. Krishnamurti)',
        '赛斯': '赛斯 (Seth / Jane Roberts)', '欧林': '欧林 (Orin / Sanaya Roman)',
        '南怀瑾': '南怀瑾', '托利': '埃克哈特·托利 (Eckhart Tolle)',
        '张德芬': '张德芬', '刘力红': '刘力红', '吴清忠': '吴清忠',
        '门罗': '罗伯特·门罗 (Robert Monroe)', '唐望': '卡洛斯·卡斯塔尼达 (Carlos Castaneda)',
        '海灵格': '伯特·海灵格 (Bert Hellinger)',
    }
    t = title + ' ' + summary[:200]
    for kw, author in author_map.items():
        if kw in t:
            return author
    return ''


def main(local_path=None):
    local = local_path or DEFAULT_LOCAL
    books = []
    for root, dirs, files in os.walk(local):
        for fn in files:
            if not fn.endswith('.md') or fn in ('README.md',):
                continue
            fp = os.path.join(root, fn)
            fm, body = extract_frontmatter(fp)
            if not fm:
                continue
            title = fm.get('title', fn)
            category = fm.get('category', '')
            tags_raw = fm.get('tags', [])
            tags = clean_tags(tags_raw, category, title)
            tier = classify(title, category)
            skills = get_skills(title, category)
            summary = extract_summary(body)
            author = guess_author(title, category, summary)

            books.append({
                'title': title,
                'category': category,
                'tier': tier,
                'skills': skills,
                'tags': tags,
                'summary': summary,
                'author': author,
            })

    # 按 Skill 分组
    skill_groups = {
        '佛学与禅修': [], '道家生命学': [], '中医养生': [],
        '新时代与灵性成长': [], '心理成长': [], '综合（待归类）': [],
    }

    for b in books:
        for sk in b['skills']:
            if sk not in skill_groups:
                sk = '综合（待归类）'
            if b not in skill_groups[sk]:
                skill_groups[sk].append(b)

    # 统计
    stats = {}
    for b in books:
        t = b['tier']
        stats[t] = stats.get(t, 0) + 1

    # ── 写 README ──
    lines = []
    lines.append('# 新时代与灵修合集 V2.0 — 领域化总目')
    lines.append('')
    lines.append('> 📖 V1.1 (2010): 原始 EXE 版，30 个分类，400+ 本电子书')
    lines.append('> 📋 V2.0 (2026): 按五个 Master Skill 域重组，版权分级，面向 AI Agent')
    lines.append(f'> 🔗 全文（{len(books)} 本）仅存于本地库：`{local}`')
    lines.append('> 🤝 参与贡献 → 见 [`docs/HOW-EXTRACTION-WORKS.md`](../../docs/HOW-EXTRACTION-WORKS.md)')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## 架构说明')
    lines.append('')
    lines.append('V2.0 与 V1.1 的区别：')
    lines.append('')
    lines.append('| | V1.1 (2010) | V2.0 (2026) |')
    lines.append('|---|---|---|')
    lines.append('| 组织形式 | 按资料源分类（30 类） | 按 Skill 域重组（5 域） |')
    lines.append('| 版权标注 | 无 | 🟢A / 🟡B / 🔴C 三级 |')
    lines.append('| 与 AI 的关系 | 阅读器（人读） | 知识引擎（Agent 调用） |')
    lines.append('| 存放位置 | EXE 内嵌 | 公开元数据 + 本地全文 |')
    lines.append('')
    lines.append(f'### 版权档位')
    lines.append('')
    lines.append(f'| 档位 | 说明 | 本库公开 | 数量 |')
    lines.append(f'|---|---|---|---|')
    lines.append(f'| 🟢 A | 公版经典（原文） | ✅ 可传原文 | {stats.get("A", 0)} |')
    lines.append(f'| 🟡 B | 古籍整理/不确定 | ⚠️ 谨慎 | {stats.get("B", 0)} |')
    lines.append(f'| 🔴 C | 现代版权期内 | ❌ 不传全文 | {stats.get("C", 0)} |')
    lines.append('')
    lines.append('### 五个 Skill 域')
    lines.append('')
    lines.append('> ⚠️ 部分书籍跨多个域（如《当生命陷落时》同属佛学禅修+心理成长），域合计 > 总数 412。')
    lines.append('')
    lines.append('| 域 | Skill 文件 | 书籍数 | 核心方向 |')
    lines.append('|---|---|---|---|')
    for sk in ['佛学与禅修', '道家生命学', '中医养生', '新时代与灵性成长', '心理成长']:
        cnt = len(skill_groups.get(sk, []))
        desc = SKILL_DESCRIPTIONS.get(sk, '')
        lines.append(f'| {EMOJI.get(sk, "")} {sk} | `agents/{SKILL_FILE_MAP.get(sk, sk)}.md` | {cnt} | {desc} |')
    lines.append('')
    lines.append('---')
    lines.append('')

    # 按 Skill 域输出
    for sk in ['佛学与禅修', '道家生命学', '中医养生', '新时代与灵性成长', '心理成长']:
        sk_books = skill_groups.get(sk, [])
        if not sk_books:
            continue

        # 按版权档位排序
        sk_a = [b for b in sk_books if b['tier'] == 'A']
        sk_b = [b for b in sk_books if b['tier'] == 'B']
        sk_c = [b for b in sk_books if b['tier'] == 'C']

        lines.append(f'## {EMOJI.get(sk, "")} {sk}')
        lines.append('')
        lines.append(f'> {SKILL_DESCRIPTIONS.get(sk, "").split("—")[-1].strip()}')
        lines.append(f'> 共 {len(sk_books)} 本（🟢{len(sk_a)} 🟡{len(sk_b)} 🔴{len(sk_c)}）')
        lines.append('')

        for tier_code, tier_label in [('A', '🟢 公版经典'), ('B', '🟡 古籍整理/不确定'), ('C', '🔴 现代版权期')]:
            tier_books = [b for b in sk_books if b['tier'] == tier_code]
            if not tier_books:
                continue
            lines.append(f'### {tier_label}')
            lines.append('')

            # 按原始分类分组
            last_cat = ''
            for b in sorted(tier_books, key=lambda x: (x['category'], x['title'])):
                if b['category'] != last_cat:
                    last_cat = b['category']
                    lines.append(f'**{last_cat}**')
                    lines.append('')

                tags_str = ', '.join(b['tags'][:3]) if b['tags'] else ''
                author_str = f' — {b["author"]}' if b['author'] else ''
                lines.append(f'- **{b["title"]}**{author_str}  `{tags_str}`')
                if b['summary']:
                    lines.append(f'  > {b["summary"][:100]}')
            lines.append('')

    # 待归类
    misc = skill_groups.get('综合（待归类）', [])
    if misc:
        lines.append('## ⚪ 综合（待归类）')
        lines.append(f'> 共 {len(misc)} 本，尚未映射到 Skill 域')
        lines.append('')
        for b in sorted(misc, key=lambda x: (x['category'], x['title'])):
            lines.append(f'- **{b["title"]}** [{b["category"]}] `{b["tier"]}`')
        lines.append('')

    lines.append('---')
    lines.append('')
    lines.append('> 📅 生成时间：2026-06-15')
    lines.append('> 🛠️ 工具：`tools/generate_v2_catalog.py`')
    lines.append('> 📖 原始 V1.1 目录 → [`classics/合集总目录.md`](../合集总目录.md)')

    os.makedirs(OUT, exist_ok=True)
    out_fn = '身心灵经典库-V2.0.md'
    with open(os.path.join(OUT, out_fn), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f'OK: {OUT}/{out_fn}', flush=True)
    for sk in ['佛学与禅修', '道家生命学', '中医养生', '新时代与灵性成长', '心理成长']:
        cnt = len(skill_groups.get(sk, []))
        a = len([b for b in skill_groups.get(sk, []) if b['tier'] == 'A'])
        b = len([b for b in skill_groups.get(sk, []) if b['tier'] == 'B'])
        c = len([b for b in skill_groups.get(sk, []) if b['tier'] == 'C'])
        print(f'  [{sk}]: {cnt} books (A={a} B={b} C={c})', flush=True)
    misc_cnt = len(misc)
    if misc_cnt:
        print(f'  ⚪ 待归类: {misc_cnt} 本')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='从 xinshidai_library 生成 V2.0 领域化总目')
    parser.add_argument('--local', default=DEFAULT_LOCAL,
                        help=f'xinshidai_library 路径（默认: {DEFAULT_LOCAL}）')
    args = parser.parse_args()
    main(local_path=args.local)
