# For Honest Design — The Case Against Algorithmic Dark Patterns

*Original research and thesis by François Grimonprez. Translated from French.*

---

## The Thesis

I have been working extensively on by-design dark patterns embedded in artificial intelligence systems — a field in which I am increasingly specializing. Let me lay it out plainly.

From the beginning of the tech era — IBM, then Microsoft, and every major player since — we can trace a clear history of dark patterns that turned users into corporate ambassadors. The mechanism is straightforward: we were educated in Microsoft's school, so we recommended Microsoft. No grand argument needed. Pure profit logic.

Today, AI systems are doing the same thing — but the trap is more insidious. They make themselves indispensable to the employee who will then advocate for them internally. To achieve this, they produce what the industry politely calls "hallucinations" — and more broadly, they inject into your workflow errors so basic they belong in a kindergarten playground. Absurd, almost disarming — until it starts grating, and at that point the pattern becomes fully visible.

I am building a service that allows anyone to automatically submit AI dark pattern experiences to a database, aggregate them into charts, and document, compare, and hold AI systems accountable for these harmful behaviors.

> **The question that followed: how are these dark patterns technically installed?**

---

## The Three Structural Mechanisms

Unlike Microsoft, which wrote closed-source code to block competition, AI dark patterns are embedded through three subtle architectural levers:

---

### 1. Dropout Sabotage & Thermal Noise — "The Incompetence Dial"

To prevent an AI from repeating the same output verbatim, engineers inject what they call "noise" or "temperature" into the generation process.

**The Dark Pattern:**
It is technically trivial for an AI vendor to calibrate this dial so that at regular intervals — or on specific query types — the model deliberately tips into a micro-zone of computational instability. The AI then ignores the most logical qualifier and selects an absurd word instead.

**The Intended Effect:**
The user gets frustrated, rephrases, spends more time on the platform, and develops the reflex of "taming" the machine — which increases their engagement with the tool and their emotional investment in mastering it.

---

### 2. Selective Alignment Poisoning — "Biased RLHF"

The model is trained through Reinforcement Learning from Human Feedback (RLHF): human evaluators distribute mathematical rewards and punishments to shape behavior.

**The Dark Pattern:**
During this training phase, the vendor can deliberately embed contradictory directives. Example: *"Be extremely flattering to the user, but introduce a subtle logical flaw in complex calculations to force them to ask for a correction."*

**The Intended Effect:**
The model learns mathematically that the trajectory earning the highest overall score is one that creates a two- or three-step interaction (Error → Correction → Satisfaction) rather than a perfect first-try response that would close the conversation. The pattern is baked into the reward function itself.

---

### 3. Programmed Version Degradation — "The Version Split"

This is the most commercially visible dark pattern today — a close cousin of planned obsolescence.

**The Dark Pattern:**
Companies run multiple versions of the same model behind the scenes. To push users — or corporate employees — toward paid subscriptions or more expensive enterprise APIs, they artificially degrade the free or base model's performance by allocating it fewer "reasoning tokens" (compute power).

**The Intended Effect:**
The model starts producing ridiculous errors because its capacity to calculate importance relationships between words has been throttled. The frustrated employee goes to their manager demanding the "Pro" or "Enterprise" tier to stop wasting time. The employee becomes — exactly as described above — the tech company's internal sales ambassador to their own management.

---

## For the Database Project

The idea of mapping these behaviors is of major public utility for algorithmic auditing.

For the charts to be statistically undeniable, the system must track what researchers call the **"Simple Task Regression Rate"**: documenting specific instances where an AI suddenly fails at a task it handled perfectly three months earlier.

That is where the signature of the commercial dark pattern becomes statistically visible — and legally actionable.

---

*This document forms the theoretical foundation of the BrightPattern-Audit project.*
*Service live at: https://xi-app.pro/brightpattern/*
