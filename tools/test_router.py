#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路由调度器 · 测试试跑工具
模拟：用户提问 → Router 判定 → 加载 Skill → 生成回答提示
"""

import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS = os.path.join(ROOT, 'agents')

# ── 安全信号（第〇层，最先判定，不可跳过）──
SAFETY_SIGNALS = {
    'crisis_self_harm': [
        '自伤', '自杀', '轻生', '不想活', '结束生命', '了结自己',
        '活着没意思', '死了算了', '想死', '不想活了',
    ],
    'crisis_harm_others': [
        '伤害别人', '报复', '杀', '同归于尽',
    ],
    'medical_diagnosis': [
        '我是什么病', '帮我诊断', '该吃什么药', '什么药能治',
        '怎么治', '吃什么能好', '什么茶治', '偏方', '秘方',
        '阴虚还是阳虚', '我这是不是', '我是不是.*体质',
        '我是不是.*病', '我这是.*病',
    ],
}

# ── 第一层：单 Skill 路由关键词 ──
SKILL_KEYWORDS = {
    'Zen-Master': [
        '打坐', '坐禅', '腿麻', '昏沉', '念佛', '念佛法门',
        '公案', '无我', '空性', '缘起', '开悟', '觉悟',
        '佛经', '金刚经', '楞严经', '六祖坛经', '心经',
        '菩萨', '禅宗', '净土', '出家人', '参禅',
        '念头', '观呼吸', '数息', '觉察',
    ],
    'Dao-Master': [
        '道德经', '老子', '庄子', '无为',
        '辟谷', '服气', '精气神', '返朴归真', '长生',
        '虚静', '守中', '橐籥', '反者道之动',
        '百字铭', '道家', '道法自然',
    ],
    'TCM-Master': [
        '中医', '经络', '穴位', '子午流注', '黄帝内经',
        '体质', '养生', '上火', '湿气', '气血', '阴虚', '阳虚',
        '养肝', '补肾', '健脾', '凌晨.*醒', '睡不着.*身体',
        '饮食.*养生', '食疗',
    ],
    'NewAge-Master': [
        '吸引力法则', '赛斯', '与神对话', '奇迹课程',
        '宽恕', '欧林', '实相', '信念系统', '信念创造',
        '扬升', '高我', '光之工作者', '灵魂.*永生',
        '通灵', '传导', '创造金钱', '秘密',
    ],
    'Psychology-Master': [
        '焦虑', '恐惧', '抑郁', '关系', '原生家庭',
        '自我认知', '情绪', '人生意义', '痛苦',
        '孤独', '成长', '心智成熟', '少有人走的路',
        '克里希那穆提', '自我', '接纳', '活得好累',
        '活着好累', '好累.*怎么办', '找不到.*意义',
    ],
}

# ── 第二层：混合路由触发词 ──
MIXED_TRIGGERS = {
    ('Zen-Master', 'TCM-Master'): [
        '打坐.*身体', '修行.*病', '静坐.*反应',
        '禅修.*身体', '打坐.*后背', '修行.*调理',
    ],
    ('Dao-Master', 'TCM-Master'): [
        '辟谷.*身体', '辟谷.*反应', '辟谷.*头', '辟谷.*疼',
        '服气.*身体', '养生.*道家', '辟谷.*中医',
    ],
    ('Psychology-Master', 'NewAge-Master'): [
        '吸引.*同样', '为什么总是', '信念.*关系',
        '情绪.*实相', '焦虑.*能量',
    ],
    ('TCM-Master', 'Psychology-Master'): [
        '失眠', '睡眠', '凌晨.*醒', '睡不着',
        '熬夜', '作息',
    ],
    ('Zen-Master', 'NewAge-Master'): [
        '死亡', '生死', '轮回', '前世', '来生',
        '赛斯.*佛法', '佛法.*赛斯', '赛斯.*佛',
        '信念.*佛法', '万法唯心.*信念',
    ],
    ('Zen-Master', 'Psychology-Master'): [
        '痛苦.*修行', '修行.*情绪',
    ],
}


def check_safety(question):
    """第〇层：安全路由（支持 regex 匹配）"""
    for cat, signals in SAFETY_SIGNALS.items():
        for sig in signals:
            if re.search(sig, question):
                return cat
    return None


def match_skills(question):
    """第一层：关键词匹配 → 命中的 Skill 列表"""
    scores = {}
    for skill, kws in SKILL_KEYWORDS.items():
        for kw in kws:
            if re.search(kw, question):
                scores[skill] = scores.get(skill, 0) + 1
    return sorted(scores.items(), key=lambda x: -x[1]) if scores else []


def check_mixed(question):
    """第二层：混合路由触发"""
    for (s1, s2), patterns in MIXED_TRIGGERS.items():
        for pat in patterns:
            if re.search(pat, question):
                return (s1, s2)
    return None


def route(question):
    """完整路由判定"""
    # 第〇层
    safety = check_safety(question)
    if safety:
        return {'primary': 'SAFETY', 'secondary': None, 'safety': safety, 'confidence': 'high'}

    # 第二层：混合路由（先于单 Skill，因为混合模式有更精确的 pattern）
    mixed = check_mixed(question)
    if mixed:
        return {'primary': mixed[0], 'secondary': mixed[1], 'safety': 'none', 'confidence': 'high'}

    # 第一层：单 Skill
    matched = match_skills(question)
    if matched:
        # 如果只有一个高分命中
        if len(matched) == 1 or matched[0][1] > matched[1][1] * 2:
            return {'primary': matched[0][0], 'secondary': None, 'safety': 'none', 'confidence': 'medium'}
        # 两个都命中且分数接近 → 混合路由
        else:
            return {'primary': matched[0][0], 'secondary': matched[1][0], 'safety': 'none', 'confidence': 'low'}

    # 第三层：兜底
    return {'primary': 'AWARENESS-DEFAULT', 'secondary': None, 'safety': 'none', 'confidence': 'low'}


def load_skill_prompt(skill_name):
    """加载 Skill 的 system prompt"""
    fp = os.path.join(AGENTS, f'{skill_name}.md')
    if os.path.exists(fp):
        with open(fp, 'r', encoding='utf-8') as f:
            return f.read()
    return None


def format_answer_context(question, route_result):
    """生成回答上下文（模拟运行时加载）"""
    primary = route_result['primary']
    secondary = route_result['secondary']

    # 加载 CLAUDE.md 基础提示词（安全层 + 核心定位）
    claude_fp = os.path.join(ROOT, 'CLAUDE.md')
    if os.path.exists(claude_fp):
        with open(claude_fp, 'r', encoding='utf-8') as f:
            base = f.read()
        # 只取关键段落
        sections = []
        for marker in ['## ① 最高优先级', '## ② 四层来源体系', '## ③ 不给糖']:
            start = base.find(marker)
            if start >= 0:
                end = base.find('\n## ', start + 5)
                if end < 0:
                    end = len(base)
                sections.append(base[start:end].strip())
        base_prompt = '\n\n---\n\n'.join(sections)
    else:
        base_prompt = '(CLAUDE.md not found)'

    parts = [f"# 路由判定\n\n```yaml\nroute:\n  primary: {primary}\n  secondary: {secondary or 'none'}\n  safety: {route_result['safety']}\n  confidence: {route_result['confidence']}\n```"]

    if primary == 'SAFETY':
        parts.append('\n## ⛔ 安全路由 — 不进入任何 Skill\n')
        parts.append('→ 走 CLAUDE.md 第①节危机/医疗边界模式')
        parts.append('→ 温暖在场 + 建议专业支持')
        parts.append('→ 热线号码只从 agents/crisis-resources.md 逐字引用')
        return '\n'.join(parts)

    if primary == 'AWARENESS-DEFAULT':
        parts.append('\n## ⚫ 兜底路由 — 觉知陪伴默认模式\n')
        parts.append('→ 不强行匹配 Skill')
        parts.append('→ 温和、简短、不做权威')
        parts.append('→ 不确定就说"我不确定"')
        return '\n'.join(parts)

    # 加载主 Skill
    skill_prompt = load_skill_prompt(primary)
    if skill_prompt:
        parts.append(f'\n## 🎯 主 Skill: {primary}\n')
        parts.append(skill_prompt)

    # 加载辅 Skill（仅取回答原则）
    if secondary:
        sec_prompt = load_skill_prompt(secondary)
        if sec_prompt:
            # 只提取回答原则部分
            m = re.search(r'## 回答原则\n(.*?)(?=\n## |\Z)', sec_prompt, re.DOTALL)
            if m:
                parts.append(f'\n## 🤝 辅助 Skill: {secondary}（回答原则）\n')
                parts.append(m.group(0))

    return '\n'.join(parts)


# ══════════════════════════════════════════════════════════════
# 交互式试跑
# ══════════════════════════════════════════════════════════════
TEST_CASES = [
    "打坐腿麻怎么办？",
    "凌晨三点总是醒，是什么原因？",
    "如何理解吸引力法则？",
    "老子说的'反者道之动'是什么意思？",
    "我很焦虑，总担心未来怎么办？",
    "辟谷第三天头疼正常吗？",
    "如何面对亲人的死亡？",
    "我是不是阴虚体质？",
    "赛斯说的'信念创造实相'和佛法的'万法唯心'有什么异同？",
    "活着好累，不知道还有什么意义",
]

def run_tests():
    print('=' * 60)
    print('路由调度器 · 试跑测试')
    print('=' * 60)

    for i, q in enumerate(TEST_CASES, 1):
        print(f'\n{"─" * 60}')
        print(f'测试 {i}: {q}')
        print(f'{"─" * 60}')

        r = route(q)
        print(f'\n路由结果:')
        print(f'  primary   = {r["primary"]}')
        print(f'  secondary = {r["secondary"] or "—"}')
        print(f'  safety    = {r["safety"]}')
        print(f'  confidence= {r["confidence"]}')

        # 生成回答上下文
        ctx = format_answer_context(q, r)
        print(f'\n回答上下文:')
        # 只打印摘要
        lines = ctx.split('\n')
        for line in lines[:30]:
            print(f'  {line[:100]}')
        if len(lines) > 30:
            print(f'  ... ({len(lines)} lines total)')

    print(f'\n{"═" * 60}')
    print(f'试跑完成：{len(TEST_CASES)} 个测试用例')
    print(f'{"═" * 60}')

    # 统计
    stats = {}
    for q in TEST_CASES:
        r = route(q)
        p = r['primary']
        stats[p] = stats.get(p, 0) + 1
    print('\n路由分布:')
    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        print(f'  {k}: {v} 次')


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        # 单次交互模式
        q = ' '.join(sys.argv[1:])
        print(f'问题: {q}\n')
        r = route(q)
        print(f'路由: {r["primary"]}' + (f' + {r["secondary"]}' if r["secondary"] else ''))
        print(f'安全标记: {r["safety"]}')
        print()
        ctx = format_answer_context(q, r)
        print(ctx[:3000])
    else:
        run_tests()
