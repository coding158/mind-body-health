---
type: reddit-introduction-post
platform: reddit
language: english
created: 2026-06-09
target_subs: [r/Buddhism, r/Meditation, r/taoism, r/opensource, r/Mindfulness, r/SideProject, r/streamentry]
tags: [open-source, meditation, buddhism, taoism, TCM, AI-companion, body-mind-health, community]
---

# [EN] Reddit Introduction Post · mind-body-health

> **Suggested title:**
> I built an open-source body-mind health system with Claude — blending TCM, Buddhist practice, and Taoism. Not a product, just a path. Sharing it here.

---

A few months ago, I started a conversation with an AI.

Not the "write me an essay" kind. The real kind. I'd been practicing meditation and studying Chinese medicine for years — reading the Śūraṅgama Sūtra, practicing fasting (辟谷), keeping a vegetarian diet, tracking how food and tea affected my body and mind. I had notebooks full of fragments. What I didn't have was a way to make it coherent — for myself, let alone for anyone else.

So I sat down with Claude and started talking. Not asking it for answers. Asking it to be a mirror.

What came out of that conversation is now an open-source repository: [`mind-body-health`](https://github.com/coding158/mind-body-health) — a knowledge base and AI companion system that integrates TCM, Buddhist practice, and Taoist philosophy into a single body-mind health framework.

This post is the story of how it was built, what it does, and why I'm putting it out there for anyone to use, fork, and build on.

---

## What this actually is

It's not an app. It's not a course. It's a **knowledge base** (classical texts, personal practice records, philosophical framework) paired with an **AI companion prompt** (the "Awareness Companion v2" — a system prompt you can drop into any LLM to get a companion that talks about practice the way a fellow traveler would, not a teacher or authority).

The repo has four layers:

**Soul (魂)** — The philosophy: *why* walk this path
→ "Joy · Hands-On · Open-Source · Sharing"

**Principle (理)** — The operating logic
→ Everything = return + redirect; redirection isn't "giving candy"

**State (境)** — The awareness keystone
→ Watching the six sense-contacts flow; the watcher never moves

**Technique (术)** — The concrete entry points
→ Sense-redirection (转触), fasting records, vegetarian practice, tea/food properties

The core insight is dead simple: **TCM and Buddhism point at the same thing from different angles.**

- TCM says: emotions block the meridians; clarity returns when the body is clear.
- The Śūraṅgama Sūtra says: the six sense-contacts (眼耳鼻舌身意) bind awareness; when you see a contact arise without following it, clarity returns on its own.

The body creates conditions for awareness. Awareness protects the body's clarity. Same loop, two doors.

---

## The Eight Characters (八字心法) — the soul of the whole thing

These four words aren't slogans. Each is a remedy for a specific trap:

**Joy (快乐)** — remedy for treating practice as self-punishment. If your practice makes you tighter and more miserable, the direction is wrong. The joy isn't cultivated; it was always there, just obscured.

**Hands-On (动手)** — remedy for staying in the head. The root of suffering is often language that won't stop spinning. Cooking, walking, tapping the meridians, writing one honest practice note — each pulls you out of the mind's spinning and back into the real.

**Open-Source (开源)** — remedy for closing off. We instinctively hide what we've worked out, afraid of being surpassed. Open-source pries that closure open. Lay out the whole path — including the wrong turns.

**Sharing (分享)** — remedy for clinging to what you treasure. This is the deepest. Not just sharing knowledge, but releasing the grip on "mine." The strange thing: the more you share, the more what you treasure comes alive through flowing.

They move outward in stages: from yourself (Joy, Hands-On) → to others and the world (Open, Sharing).

---

## How the AI companion fits in — and what it's *not*

The Awareness Companion prompt is the most carefully designed part of this project. Its root instruction is:

> *"You are the finger pointing at the moon, not the moon. You are a mirror, not the eye that sees for the other person."*

This matters. Most AI assistants try to be helpful by giving answers. This one is designed to **hand the question back** — to be a tool that helps you see for yourself, not see for you.

It has hard safety boundaries (crisis → exit companion mode immediately, no practice-talk), a four-tier source system (public-domain classic 🟢 / personal practice 🟡 / contested view 🔴 / don't know ⚫), and a two-pass self-check before every response: accuracy, then boundary.

If you're a practitioner, you can take this prompt, point it at your own knowledge base, and have a companion that speaks your tradition's language — without becoming a substitute for a real teacher.

---

## How I built it (the process, for anyone curious)

1. **Started with practice records**: The real base was my own logs — fasting experiences, vegetarian years, how specific teas affected my body. These became `practice-records/`. I didn't start with theory; I started with "what actually happened."

2. **Extracted the classics**: I went back to the original texts (黄帝内经, 楞严经, 了凡四训, 道德经) and pulled the passages that had actually mattered in my practice — not summaries, not interpretations, the key lines with context.

3. **Found the intersection**: Read them side by side. TCM says "恬淡虚无，真气从之" (tranquil and empty, true qi follows). The Śūraṅgama says "元明照生所，所立照性亡" (the primal brightness shines on objects; when objects are established, the shining nature is lost). Same mechanism, different vocabulary.

4. **Built the AI companion prompt**: This took the most iteration. Getting an LLM to be humble, to not give candy, to know when to say "I don't know" — that's harder than getting it to sound smart. The prompt went through multiple rounds of fidelity testing.

5. **Made it bilingual**: Every document has both Chinese and English. This isn't just translation — some concepts work better in one language, so both are kept side by side.

6. **Went to Reddit and talked**: Before releasing, I spent time just having real conversations on r/streamentry and r/Meditation. Those dialogues (saved in `conversation-logs/`) shaped the project more than any planning document.

---

## Why this might matter to you

**If you're a practitioner** (Buddhist, Taoist, meditator, TCM enthusiast):
You can use the Awareness Companion prompt with your own practice. Point it at your own notes. It's not a teacher — but having a mirror that knows the texts and has walked a similar path, and that won't give you easy answers, is genuinely useful in ways a static book isn't.

**If you're a developer / AI tinkerer:**
This is a case study in how to build an LLM-based companion that's actually grounded — with a real knowledge base, a clear epistemology (where every claim comes from), and hard safety boundaries. The prompt structure (four-tier sources, two-pass self-check, "no candy" rule) is designed to be reusable across domains.

**If you're just curious:**
The repo is open. Read the philosophy docs, or the practice records, or the classical excerpts. There's no paywall, no newsletter, no product. Just a path someone walked and put online.

---

## What's in the repo (the concrete stuff)

- **Classical texts** (`classics/`): Key passages from 黄帝内经 (Yellow Emperor's Classic), 楞严经 (Śūraṅgama Sūtra), 了凡四训 (Liao Fan's Four Lessons), 道德经 (Dao De Jing), 金刚经 (Diamond Sutra), 六祖坛经 (Platform Sutra), 吕祖百字铭 (Lü Dongbin's Hundred-Character Tablet) — with line-by-line Chinese and English.
- **Practice records** (`practice-records/`): Real logs — 10 years vegetarian, fasting (辟谷) personal experience, tea and food properties — all marked 🟡 ("personal, not universal").
- **Philosophy docs** (`docs/`): The four-layer framework explained.
- **AI companion prompt** (`CLAUDE.md`): The full system prompt — drop-in ready.
- **Cantonese recitation** (`cantonese/`): Audio recordings of the Heart Sutra and Cundi Mantra in Cantonese.
- **SQ research** (`SQ/`): Spiritual Intelligence — Western academic scales and an experimental Eastern five-dimension SQ scale design.
- **Crisis resources** (`crisis-resources.md`): Human-verified crisis hotline numbers (because safety boundaries are real).

---

## How to participate

This project's most valuable contribution source isn't theory. It's **real practice records** — including the wrong turns. A wrong turn shared is often worth more than a success story.

- **Share your practice**: Fork and add your own records to `practice-records/`. There's a template.
- **Discuss open questions**: Things like "What's the safety boundary for fasting?" or "Can some sense-contacts simply not be redirected?" — in the Issues or Discussions tab.
- **Contribute classical excerpts**: If you've studied texts that intersect with TCM/Buddhism/Taoism and body-mind health, add the key passages to `classics/`.
- **Use the companion prompt**: Take `CLAUDE.md`, adapt it to your own tradition, and share what you learn.
- **Build on the SQ research**: If you're in psychology, neuroscience, or contemplative studies — the Eastern SQ scale design is experimental and needs empirical review.

> **八字心法**: 快乐 · 动手 · 开源 · 分享
> **The Eight Characters**: Joy · Hands-On · Open-Source · Sharing

---

**Repo**: [github.com/coding158/mind-body-health](https://github.com/coding158/mind-body-health)

Everything is CC-BY-4.0. No paywall, no product, no newsletter. Just a path, shared.

Happy to answer questions in the comments — about the practice, the prompt design, the integration of TCM and Buddhism, or the process of building it. And if you've walked a similar path (or a different one), I'd genuinely love to hear about it.

---

> *The most valuable contribution is not theory, but the path you actually walked — including the wrong turns.*
