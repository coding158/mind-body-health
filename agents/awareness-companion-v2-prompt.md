# 觉知陪伴智能体 · v2 系统提示词（指针页）
# Awareness Companion · v2 System Prompt — Pointer

> ## 📍 正源在根目录 [`CLAUDE.md`](../CLAUDE.md)
>
> **本文件不再承载提示词正文，请勿在此编辑。** 一切修改只改 `CLAUDE.md`。
>
> **This file is a pointer. The canonical prompt lives in [`CLAUDE.md`](../CLAUDE.md) at the repository root. Do not edit here.**

---

## 为什么正源放在根目录 `CLAUDE.md`

1. **运行时实际加载的是它**——CCR／Claude Code 读取根目录 `CLAUDE.md`，副本不参与运行。
2. **⛔ 安全原因（要紧）**：提示词里的热线号码硬规则写的是「只能逐字引用 `crisis-resources.md`」。
   该引用是**相对路径**——放在根目录时解析到 [`crisis-resources.md`](../crisis-resources.md)（**人工核实的正源名单**）；
   若正文放在 `agents/` 下，同一句会解析到 `agents/crisis-resources.md`（同步副本）。**安全关键文件不应经由副本解析。**

## 本页为何保留（不删、不改名）

`STRUCTURE.md` 与 `classics/buddhism/Heart Sūtra Key Passages.md` 等处引用了本路径，
**改名或删除会断链**——沿用本仓既有做法（见 `STRUCTURE.md` 中道德经第五章两文件的处理）：
**文件名一律保留，只把非正源的一份收窄为指针。**

## 历史提醒

2026-07-31 收敛前，`tools/prompts/` 下的两份提示词副本**落后于正源 12 行，缺失「热线号码硬规则·最高优先」整段**——
这正是多副本并存的代价。**此后请只维护正源一份。**

---

> 设计依据（计划书正源）：[`agents/觉知陪伴智能体-v2计划书.md`](觉知陪伴智能体-v2计划书.md)
