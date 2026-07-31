#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""知识治理指标 lint · 供 docs/ROADMAP-能力与指标.md 的四项指标使用

用法：
    python tools/lint_knowledge.py            # 全部指标
    python tools/lint_knowledge.py --metric 1 # 只跑某一项

指标：
  1  标注覆盖率        —— 机械可判：faq/ research/ 每个实质小节须有「来源坐标」
  2  「为什么是这一条」 —— 启发式：navigation/ faq/ 的内链附近须有理由句（需人工确认）
  3  债务数            —— 机械可判：统计 <!-- DEBT: ... --> 标记，只降不升
  4  闭环收敛率        —— 半自动：列出 ADR，与已知缺陷人工对账

设计说明：
  指标 3 **只认可机读标记** `<!-- DEBT: 类型 | 说明 -->`，
  不认纯文字「文献待补」——后者会把规则描述与历史引述误计为欠债
  （2026-07-31 实测误报 3 处）。
"""
import os, re, sys, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 指标 1：结构性小节不要求标注（它们不承载"说法"）
STRUCTURAL = re.compile(
    r'(你可能是这样的|可以做的三件事|什么时候|坐标总表|这份记录|写作规则|已有条目|'
    r'这条是为谁补的|原始出处|这项研究做了什么|关键数字|证据等级|不能用它支持什么|'
    r'固定结构|三条规则|先说清楚|先说一句最要紧的|本页坐标|伤害自己|危机)'
)
COORD = re.compile(r'来源坐标|\*\*坐标\*\*|证据等级')

# 指标 2：属于导航/页脚的链接，不要求理由句
NAV_LINK_CTX = re.compile(r'(相关：|← ?回|见 |📄 出处|详见|参见|回链|索引|入口)')
REASON = re.compile(r'为什么是这一(条|篇)')

DEBT = re.compile(r'<!--\s*DEBT:\s*([^|]+?)\s*(?:\|\s*(.*?))?\s*-->')


def md_files(*dirs, skip_readme=False):
    out = []
    for d in dirs:
        p = os.path.join(ROOT, d)
        if not os.path.isdir(p):
            continue
        for fn in sorted(os.listdir(p)):
            if not fn.endswith('.md'):
                continue
            if skip_readme and fn.upper().startswith('README'):
                continue
            out.append(os.path.join(d, fn))
    return out


def sections(text):
    """切成 (层级, 标题, 正文块)；看 ### / #### / ##### 级"""
    parts, cur, lvl, buf = [], None, 0, []
    for line in text.split('\n'):
        m = re.match(r'^(#{3,5})\s+(.*)$', line)
        if m:
            if cur is not None:
                parts.append((lvl, cur, '\n'.join(buf)))
            lvl, cur, buf = len(m.group(1)), m.group(2).strip(), []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        parts.append((lvl, cur, '\n'.join(buf)))
    return parts


def metric1():
    """faq/ 与 research/ 内容类型不同，判据也不同——用同一把尺子量会满屏误报。
    faq/    ：每个**承载说法的叶子小节**须有来源坐标
    research/：每篇须具备六节体例中的「证据等级」与「不能用它支持什么」
    """
    print('【指标 1】标注覆盖率（机械可判）')
    total = miss = 0

    # —— faq/：叶子小节须有坐标（容器小节由其子节承担，不重复要求）——
    for rel in md_files('faq', skip_readme=True):
        text = open(os.path.join(ROOT, rel), encoding='utf-8').read()
        secs = sections(text)
        for idx, (lvl, title, body) in enumerate(secs):
            if STRUCTURAL.search(title):
                continue
            # 容器小节：紧随其后的小节层级更深 → 坐标由子节承担
            if idx + 1 < len(secs) and secs[idx + 1][0] > lvl:
                continue
            total += 1
            if not COORD.search(body):
                miss += 1
                print(f'  ❌ 缺来源坐标：{rel} → {title}')

    # —— research/：整篇为一条文献，按六节体例校验 ——
    for rel in md_files('research', skip_readme=True):
        text = open(os.path.join(ROOT, rel), encoding='utf-8').read()
        for need in ('证据等级', '不能用它支持什么'):
            total += 1
            if need not in text:
                miss += 1
                print(f'  ❌ 缺「{need}」节：{rel}')

    pct = 100.0 if total == 0 else (total - miss) * 100.0 / total
    print(f'  → 受检项 {total} 个，缺 {miss} 个，覆盖率 {pct:.1f}%（目标 100%）')
    return miss == 0


ENTRY_TARGET = re.compile(r'\]\((?!http)[^)]*(classics/|practice-records/|research/)[^)]*\.md[^)]*\)')


def metric2():
    """只检**条目链接**——指向 classics/ practice-records/ research/ 的那些。
    页内互链、危机页、docs/ 规范链接不是"条目"，不要求理由句。
    表格条目：若该表表头含「为什么是这一条」，视为已满足（理由在同行另一列）。
    """
    print('【指标 2】「为什么是这一条」覆盖率（条目链接，机械可判）')
    total = miss = 0
    for rel in md_files('navigation', 'faq', skip_readme=True):
        lines = open(os.path.join(ROOT, rel), encoding='utf-8').read().split('\n')
        header_has_reason = False
        for i, line in enumerate(lines):
            if line.lstrip().startswith('|'):
                if REASON.search(line):        # 这是带理由列的表头
                    header_has_reason = True
            else:
                header_has_reason = False      # 离开表格
            if not ENTRY_TARGET.search(line):
                continue
            if NAV_LINK_CTX.search(line):
                continue
            # 只有"条目"才要求理由句：列表项、表格行、或独立成段的加粗链接。
            # 正文行内引用（句子中间提到某篇）与引用块（>）不是条目。
            s = line.lstrip()
            is_entry = (s.startswith('|') or re.match(r'^[-*]\s', s)
                        or re.match(r'^\d+\.\s', s) or s.startswith('**['))
            if not is_entry:
                continue
            total += 1
            window = '\n'.join(lines[i:i + 5])
            if header_has_reason or REASON.search(window) or REASON.search(line):
                continue
            miss += 1
            print(f'  ❌ 条目缺理由句：{rel}:{i+1}  {line.strip()[:56]}')
    pct = 100.0 if total == 0 else (total - miss) * 100.0 / total
    print(f'  → 条目链接 {total} 个，缺理由 {miss} 个，覆盖率 {pct:.1f}%（目标 100%）')
    return miss == 0


def metric3():
    print('【指标 3】债务数（机械可判，只降不升）')
    rows = []
    for dirpath, _, fns in os.walk(ROOT):
        if '.git' in dirpath:
            continue
        for fn in fns:
            if not fn.endswith('.md'):
                continue
            fp = os.path.join(dirpath, fn)
            in_fence = False
            for i, line in enumerate(open(fp, encoding='utf-8', errors='ignore')):
                if line.lstrip().startswith('```'):
                    in_fence = not in_fence
                    continue
                if in_fence:                      # 代码块内是**示例**，不是欠债
                    continue
                # 行内代码里的标记同样是示例（如规范文档在讲这个约定本身）
                bare = re.sub(r'`[^`]*`', '', line)
                for m in DEBT.finditer(bare):
                    rows.append((os.path.relpath(fp, ROOT).replace('\\', '/'),
                                 i + 1, m.group(1), (m.group(2) or '').strip()))
    if rows:
        print('  | 文件 | 行 | 类型 | 说明 |')
        print('  |---|---|---|---|')
        for f, ln, t, d in rows:
            print(f'  | {f} | {ln} | {t} | {d} |')
    print(f'  → 未偿债务 {len(rows)} 条'
          f'（只认 <!-- DEBT: 类型 | 说明 -->，不认纯文字「文献待补」）')
    return True


def metric4():
    print('【指标 4】闭环收敛率（半自动：列出 ADR，需人工对账）')
    d = os.path.join(ROOT, 'docs', 'ADR')
    if not os.path.isdir(d):
        print('  ❌ 无 docs/ADR/ 目录')
        return False
    adrs = [f for f in sorted(os.listdir(d)) if re.match(r'^\d{4}-', f)]
    for a in adrs:
        print(f'  · {a}')
    print(f'  → ADR {len(adrs)} 条。**每个被暴露的缺陷是否都有对应 ADR，需人工核对**')
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--metric', type=int, choices=[1, 2, 3, 4])
    a = ap.parse_args()
    fns = {1: metric1, 2: metric2, 3: metric3, 4: metric4}
    ok = True
    for k in ([a.metric] if a.metric else [1, 2, 3, 4]):
        ok = fns[k]() and ok
        print()
    print('结果：' + ('全部通过' if ok else '有未达标项（见上）'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
