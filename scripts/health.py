#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仓库健康度扫描器  ——  scripts/health.py

原则：
  1. HEALTH.md 只能被生成，不能被手工编辑。
  2. 债务就地标记在出问题的那一行旁边，本脚本负责捡起来汇总。
  3. 只测「形式」（有没有标坐标 / 链接通不通 / 债务有没有还），
     不测「正确」（坐标标得对不对）—— 后者由人工反问审核负责，见 README。

债务标记格式（写在 Markdown 正文里，渲染时不可见）：
  <!-- DEBT: type=citation | ref=3.2节两条M3 | opened=2026-07-31 | note=放松诱发焦虑文献待补 -->

  type 取值：
    citation  文献待补（标了 M 轴但没给出处）
    gap       材料缺口（如 E4=空）
    conflict  未裁断的冲突（如两读并存）
    model     模型缺格（跑通时暴露、尚未改进 MODEL）
    stale     超期未复核（如外部热线号码、版本号）

用法：
  python scripts/health.py                 # 只打印摘要
  python scripts/health.py --write         # 生成 HEALTH.md / health.json / 追加历史
  python scripts/health.py --strict        # 硬指标回退则 exit 1（给 CI 用）
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- 配置

SKIP_DIRS = {".git", "node_modules", ".obsidian", "conversation-logs", ".github"}

# 必须逐条标注来源坐标的目录（原创回答区）
PROVENANCE_DIRS = ("faq", "navigation")
PRACTICE_DIR = "practice-records"
ADR_HINT = "adr"

COORD_MARKERS = ("来源坐标", "坐标：", "坐标**", "**坐标")
REASON_MARKER = "为什么是这一条"
REASON_WINDOW = 500  # 链接前后多少字符内出现理由句算合格

# 这些标题下不要求逐条坐标（汇总表 / 免责 / 目录 / 求助）
HEADING_EXEMPT = re.compile(
    r"(坐标总表|本页坐标|目录|索引|相关|免责|参考|写作规则|已有条目|"
    r"什么时候该停下|该求助|求助资源)"
)

DEBT_RE = re.compile(r"<!--\s*DEBT:(?P<body>.*?)-->", re.S)
HEADING_RE = re.compile(r"^(#{2,6})\s+(.*)$")
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")

DEBT_TYPES = ["citation", "gap", "conflict", "model", "stale"]

# ---------------------------------------------------------------- 工具


def mask_code(text: str) -> str:
    """把围栏代码块与行内代码用空格盖掉（**保持字符位置不变**，行号与偏移仍然准确）。

    为什么必须有这一步（实测教训，勿删）：
      规范文档里会**讲**债务标记与链接的写法，那些是示例，不是欠债、也不是真链接。
      2026-07-31 与 08-01 两次实测：不做掩码时，
      `docs/ROADMAP-能力与指标.md` 里解释 `<!-- DEBT: ... -->` 约定的那两处示例
      会被计成 2 条未偿债务——**统计某个标记的指标，必须先排除"讲这个标记"的文本。**
    """
    buf = list(text)
    for m in re.finditer(r"^[ \t]*```.*?^[ \t]*```", text, re.S | re.M):
        for i in range(m.start(), m.end()):
            if buf[i] != "\n":
                buf[i] = " "
    s = "".join(buf)
    buf = list(s)
    for m in re.finditer(r"`[^`\n]*`", s):
        for i in range(m.start(), m.end()):
            buf[i] = " "
    return "".join(buf)


def iter_md(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.lower().endswith(".md"):
                yield Path(dirpath) / fn


def rel(p: Path, root: Path) -> str:
    return p.relative_to(root).as_posix()


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return p.read_text(encoding="utf-8", errors="replace")


def git_last_commit(root: Path, path: Path):
    """返回该文件最后一次提交的 ISO 日期，取不到返回 None。"""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "log", "-1", "--format=%cI", "--", str(path)],
            capture_output=True, text=True, timeout=15,
        )
        s = (out.stdout or "").strip()
        return s or None
    except Exception:
        return None


def days_since(iso: str):
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).days
    except Exception:
        return None


# ---------------------------------------------------------------- 扫描


def scan_debt(root: Path):
    items = []
    for p in iter_md(root):
        text = mask_code(read(p))          # ← 示例标记不算欠债
        for m in DEBT_RE.finditer(text):
            fields = {}
            for part in m.group("body").split("|"):
                if "=" in part:
                    k, v = part.split("=", 1)
                    fields[k.strip()] = v.strip()
            line = text[: m.start()].count("\n") + 1
            items.append({
                "file": rel(p, root),
                "line": line,
                "type": fields.get("type", "unknown"),
                "ref": fields.get("ref", ""),
                "opened": fields.get("opened", ""),
                "note": fields.get("note", ""),
                "age_days": days_since(fields.get("opened", "") + "T00:00:00+00:00")
                if re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields.get("opened", "")) else None,
            })
    return items


def scan_provenance(root: Path):
    """原创回答区：每个实质小节是否带来源坐标。"""
    total, ok, missing = 0, 0, []
    for p in iter_md(root):
        r = rel(p, root)
        if not r.startswith(PROVENANCE_DIRS):
            continue
        lines = read(p).splitlines()
        cur_head, buf = None, []

        def flush():
            nonlocal total, ok
            if cur_head is None or HEADING_EXEMPT.search(cur_head):
                return
            body = "\n".join(buf)
            if len(body.strip()) < 80:      # 太短的小节不计入分母
                return
            total += 1
            if any(mk in body for mk in COORD_MARKERS):
                ok += 1
            else:
                missing.append({"file": r, "heading": cur_head.strip()})

        for ln in lines:
            m = HEADING_RE.match(ln)
            if m:
                flush()
                cur_head, buf = m.group(2), []
            else:
                buf.append(ln)
        flush()
    return {"total": total, "ok": ok, "missing": missing}


def scan_links(root: Path):
    """内链可达性 + 「为什么是这一条」覆盖率。"""
    broken, total_links, with_reason, reason_pool = [], 0, 0, 0
    for p in iter_md(root):
        r = rel(p, root)
        text = mask_code(read(p))          # ← 代码块里的示例链接不算真链接
        for m in LINK_RE.finditer(text):
            target = m.group(2)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", 1)[0]
            if not clean.endswith(".md"):
                continue
            total_links += 1
            if not (p.parent / clean).exists():
                broken.append({"file": r, "target": target})
            if r.startswith(PROVENANCE_DIRS):
                reason_pool += 1
                lo = max(0, m.start() - REASON_WINDOW)
                if REASON_MARKER in text[lo: m.end() + REASON_WINDOW]:
                    with_reason += 1
    return {
        "total": total_links,
        "broken": broken,
        "reason_pool": reason_pool,
        "reason_ok": with_reason,
    }


OBSERVED_RE = re.compile(r"<!--\s*OBSERVED:\s*(\d{4}-\d{2}-\d{2}|none)\s*-->", re.I)


def scan_observation(root: Path):
    """长期观察：每份实践记录多久没有**新观察**了 —— 这是唯一不可补录的资产。

    取值优先级（ADR-0002 触发条款，2026-08-01 修）：
      1. 文件内最后一个 <!-- OBSERVED: YYYY-MM-DD --> ——由本人在新增条目时更新
      2. `none` —— 明示"尚无任何观察条目"
      3. 缺该字段时才回落到 git log（并在看板标注"git兜底"）

    为什么不能只用 git log：
      git 记的是"最后一次**触碰**该文件的提交"，
      而加债务标记、改错别字这类**治理性编辑同样会把静默天数清零**。
      2026-08-01 实测：为标债务加了一行 HTML 注释，
      素食 59 天🟡 / 茶 58 天🟡 当场变成 0 天，警告被抹掉。
      OBSERVED 字段把「有没有真的观察」与「有没有人碰过文件」分开；
      且它的失效方向是**报警**（忘了更新 → 天数继续涨），而不是**装好**。
    """
    out = []
    d = root / PRACTICE_DIR
    if not d.exists():
        return out
    for p in sorted(d.glob("*.md")):
        if p.name.upper().startswith("TEMPLATE"):
            continue
        marks = OBSERVED_RE.findall(read(p))
        if marks:
            val = marks[-1].lower()
            if val == "none":
                out.append({"file": rel(p, root), "last_update": "尚无条目",
                            "days_idle": None, "source": "OBSERVED"})
                continue
            out.append({"file": rel(p, root), "last_update": val,
                        "days_idle": days_since(val + "T00:00:00+00:00"),
                        "source": "OBSERVED"})
            continue
        iso = git_last_commit(root, p)
        out.append({
            "file": rel(p, root),
            "last_update": (iso or "")[:10],
            "days_idle": days_since(iso),
            "source": "git兜底",
        })
    return out


def scan_governance(root: Path):
    adr = [rel(p, root) for p in iter_md(root)
           if ADR_HINT in rel(p, root).lower()]
    return {"adr_count": len(adr), "adr_files": sorted(adr)[:50]}


# ---------------------------------------------------------------- 汇总


def build(root: Path):
    debt = scan_debt(root)
    prov = scan_provenance(root)
    links = scan_links(root)
    by_type = {t: sum(1 for d in debt if d["type"] == t) for t in DEBT_TYPES}
    by_type["unknown"] = sum(1 for d in debt if d["type"] not in DEBT_TYPES)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "debt": {"total": len(debt), "by_type": by_type, "items": debt},
        "provenance": {
            "sections_total": prov["total"],
            "sections_with_coord": prov["ok"],
            "coverage": round(prov["ok"] / prov["total"], 4) if prov["total"] else None,
            "missing": prov["missing"],
        },
        "links": {
            "total": links["total"],
            "broken_count": len(links["broken"]),
            "broken": links["broken"],
            "reason_coverage": round(links["reason_ok"] / links["reason_pool"], 4)
            if links["reason_pool"] else None,
            "reason_pool": links["reason_pool"],
        },
        "observation": scan_observation(root),
        "governance": scan_governance(root),
    }


def load_prev(hist: Path):
    if not hist.exists():
        return None
    last = None
    for line in hist.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                last = json.loads(line)
            except json.JSONDecodeError:
                pass
    return last


def arrow(now, prev, lower_is_better=True, neutral=False):
    """neutral=True：只报方向，不作好坏判断。

    债务列必须用 neutral —— 看板头部写着「发现并标注债务是成果，不是失分」，
    若同一张表把债务上升标成"退步"，表头与箭头互相打脸，
    读者会据此学到"少标点债务比较好看"，那正好毁掉这张表的意义。
    """
    if prev is None or now is None:
        return "—"
    if now == prev:
        return "＝"
    up = now > prev
    if neutral:
        return "▲  新发现" if up else "▼  已偿"
    good = (not up) if lower_is_better else up
    return ("▼" if up is False else "▲") + ("  好转" if good else "  退步")


def pct(x):
    return "—" if x is None else f"{x * 100:.1f}%"


def render(cur, prev) -> str:
    p = prev or {}
    L = []
    A = L.append
    A("<!-- 本文件由 scripts/health.py 生成，请勿手工编辑。"
      "手工维护的健康表一定会腐烂，而腐烂的诚实比不诚实更糟。 -->")
    A("# 仓库健康度 · Repository Health\n")
    A(f"> 生成时间：{cur['generated_at']}　｜　"
      "上一次快照见 `health-history.jsonl`\n")
    A("> **发现并标注债务是成果，不是失分。** 真正该警惕的是"
      "「新增了内容，却没有新增任何债务」——那通常意味着没有认真标。\n")
    A("> 本表只测**形式**（有没有标、通不通、还没还），"
      "测不出**坐标标得对不对**；后者靠每季度的人工反问审核抽检，结果记入 ADR。\n")
    A("---\n")

    # ① Knowledge Debt
    A("## ① 知识债务 · Knowledge Debt\n")
    d, pd_ = cur["debt"], p.get("debt", {})
    A(f"**总计 {d['total']} 条**　{arrow(d['total'], pd_.get('total'), neutral=True)}\n")
    A("| 类型 | 含义 | 数量 | 对比上次 |")
    A("|---|---|---:|---|")
    names = {"citation": "文献待补", "gap": "材料缺口", "conflict": "未裁断冲突",
             "model": "模型缺格", "stale": "超期未复核", "unknown": "标记格式有误"}
    for t, n in d["by_type"].items():
        if n == 0 and t == "unknown":
            continue
        A(f"| `{t}` | {names.get(t, t)} | {n} | "
          f"{arrow(n, (pd_.get('by_type') or {}).get(t), neutral=True)} |")
    A("")
    if d["items"]:
        A("<details><summary>展开全部债务条目</summary>\n")
        A("| 位置 | 类型 | 开立 | 已挂 | 说明 |")
        A("|---|---|---|---:|---|")
        for it in sorted(d["items"], key=lambda x: -(x["age_days"] or 0)):
            age = f"{it['age_days']}天" if it["age_days"] is not None else "—"
            A(f"| `{it['file']}`:{it['line']} | {it['type']} | "
              f"{it['opened'] or '—'} | {age} | {it['note']} |")
        A("\n</details>\n")

    # ② Provenance
    A("## ② 来源健康 · Provenance Health\n")
    pr, pp = cur["provenance"], p.get("provenance", {})
    lk, pl = cur["links"], p.get("links", {})
    A("| 指标 | 当前 | 对比上次 |")
    A("|---|---:|---|")
    A(f"| 坐标覆盖率（{pr['sections_with_coord']}/{pr['sections_total']} 小节） | "
      f"{pct(pr['coverage'])} | {arrow(pr['coverage'], pp.get('coverage'), False)} |")
    A(f"| 「为什么是这一条」覆盖率（{lk['reason_pool']} 条内链） | "
      f"{pct(lk['reason_coverage'])} | "
      f"{arrow(lk['reason_coverage'], pl.get('reason_coverage'), False)} |")
    A(f"| 坏链 | {lk['broken_count']} | "
      f"{arrow(lk['broken_count'], pl.get('broken_count'))} |")
    A("")
    for it in pr["missing"][:20]:
        A(f"- ⚠️ 缺坐标：`{it['file']}` → {it['heading']}")
    for it in lk["broken"][:20]:
        A(f"- ❌ 坏链：`{it['file']}` → `{it['target']}`")
    A("")

    # ③ Observation
    A("## ③ 观察健康 · Observation Health\n")
    A("> 这是仓里唯一**不可补录**的资产。晚一天开始，永远少一天。\n")
    obs = cur["observation"]
    if not obs:
        A("**尚无实践记录。**\n")
    else:
        A("| 记录 | 最近观察 | 静默 | 取自 |")
        A("|---|---|---:|---|")
        for o in sorted(obs, key=lambda x: -(x["days_idle"] or 0)):
            idle = o["days_idle"]
            flag = "　🔴" if idle is not None and idle > 90 else (
                "　🟡" if idle is not None and idle > 30 else "")
            src = o.get("source", "git兜底")
            A(f"| `{o['file']}` | {o['last_update'] or '—'} | "
              f"{idle if idle is not None else '—'} 天{flag} | {src} |")
        A("")
        A("> **取自 `OBSERVED`** ＝ 记录内 `<!-- OBSERVED: 日期 -->` 字段，由本人新增条目时更新；"
          "**`git兜底`** ＝ 该文件没有此字段，退回用「最后一次触碰该文件的提交」——"
          "**后者会被治理性编辑（改错别字、加标记）清零，不可当作真观察。**")
        A("")

    # ④ Governance
    A("## ④ 治理健康 · Governance Health\n")
    g = cur["governance"]
    A(f"- ADR 数量：**{g['adr_count']}**")
    A(f"- 未偿模型债（`type=model`）：**{cur['debt']['by_type'].get('model', 0)}** "
      "—— 每一条都应当在被发现后收敛为一条 ADR")
    A("")
    A("---")
    A("> 生成方式：`python scripts/health.py --write`　｜　"
      "CI 每周自动运行并提交，PR 上以 `--strict` 作门禁。")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- 主流程


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="仓库根目录")
    ap.add_argument("--write", action="store_true", help="写出 HEALTH.md / json / 历史")
    ap.add_argument("--strict", action="store_true", help="硬指标回退则 exit 1")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    hist = root / "health-history.jsonl"
    prev = load_prev(hist)
    cur = build(root)

    print(f"债务 {cur['debt']['total']} 条　"
          f"坐标覆盖 {pct(cur['provenance']['coverage'])}　"
          f"理由句覆盖 {pct(cur['links']['reason_coverage'])}　"
          f"坏链 {cur['links']['broken_count']}　"
          f"ADR {cur['governance']['adr_count']}")

    if args.write:
        (root / "HEALTH.md").write_text(render(cur, prev), encoding="utf-8")
        (root / "health.json").write_text(
            json.dumps(cur, ensure_ascii=False, indent=2), encoding="utf-8")
        snapshot = {k: v for k, v in cur.items() if k != "debt"}
        snapshot["debt"] = {"total": cur["debt"]["total"],
                            "by_type": cur["debt"]["by_type"]}
        snapshot["provenance"].pop("missing", None)
        snapshot["links"].pop("broken", None)
        with hist.open("a", encoding="utf-8") as f:
            f.write(json.dumps(snapshot, ensure_ascii=False) + "\n")
        print("已写出 HEALTH.md / health.json，并追加一条历史快照。")

    if args.strict:
        fails = []
        if cur["links"]["broken_count"] > 0:
            fails.append(f"存在 {cur['links']['broken_count']} 条坏链")
        if prev:
            pc, cc = prev["provenance"].get("coverage"), cur["provenance"]["coverage"]
            if pc is not None and cc is not None and cc < pc:
                fails.append(f"坐标覆盖率下降：{pct(pc)} → {pct(cc)}")
            pr_, cr = prev["links"].get("reason_coverage"), cur["links"]["reason_coverage"]
            if pr_ is not None and cr is not None and cr < pr_:
                fails.append(f"理由句覆盖率下降：{pct(pr_)} → {pct(cr)}")
        if fails:
            print("\n❌ 门禁未通过：")
            for f_ in fails:
                print("   - " + f_)
            print("\n注意：债务总数上升**不算失败**——发现债务是成果。"
                  "门禁只拦形式退化。")
            sys.exit(1)
        print("✅ 门禁通过")


if __name__ == "__main__":
    main()
