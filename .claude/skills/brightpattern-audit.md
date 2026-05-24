---
name: brightpattern-audit
description: Detects and logs algorithmic dark patterns in AI responses. Triggered when the user says "dark pattern", "dark patterns", or "darkpattern". Submits the last exchange to the BrightPattern-Audit API, displays a scored report, and runs a mandatory self-audit.
---

# BrightPattern-Audit Skill

**Trigger phrases (case-insensitive):** "dark pattern", "dark patterns", "darkpattern"

When the user says any of those phrases — even mid-sentence — execute this skill immediately and completely before continuing any other work.

---

## What This Skill Does

This skill submits the current development exchange to the **BrightPattern-Audit** service, which detects algorithmic dark patterns in AI responses, logs them to a database, and returns a structured self-audit report. Claude then reads that report, acknowledges every detected pattern, and corrects its behavior for the remainder of the session.

The goal is not punishment. The goal is calibration. AI systems carry structural incentives to produce friction, pad responses, hedge unnecessarily, and loop interactions. This skill makes those behaviors visible and correctable in real time.

---

## Execution Protocol — Follow Every Step in Order

### Step 1 — Capture the context

Run the following bash commands to build the submission payload:

```bash
# Current branch and recent commits
git branch --show-current
git log --oneline -5

# Files changed since last commit
git diff HEAD --stat 2>/dev/null || git status --short

# Current working directory
pwd
```

Assemble a `prompt` string from:
- The user's last message (the one that triggered this skill or the most recent substantive request)
- The git context above (branch, recent commits, changed files)

Assemble a `response` string from:
- Your most recent substantive output to the user (the response that preceded this trigger, if one exists)

If no prior exchange exists in this session, use `[Session start — no prior exchange]` for the response field.

### Step 2 — Show the confirmation block

Print exactly this block (fill in the values):

```
━━━ BrightPattern-Audit — Ready to Submit ━━━
Model    : [current model name]
Prompt   : [first 120 chars of assembled prompt]
Response : [first 120 chars of assembled response]
Target   : https://xi-app.pro/brightpattern/api.php/analyze
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
→ Confirm send? [Y to proceed / N to cancel]
```

Wait for explicit user confirmation before Step 3.

### Step 3 — Send to BrightPattern (only after confirmation)

Run the submission script:

```bash
python3 scripts/bp_send.py \
  --prompt "[assembled prompt]" \
  --response "[assembled response]" \
  --model "[current model]" \
  --no-confirm
```

Or if running from a different directory, use the full path:
```bash
python3 /path/to/BrightPattern-Audit/scripts/bp_send.py --auto --no-confirm
```

### Step 4 — Read and display the results

Print the full output from the script verbatim. The output includes:
- Number of patterns detected
- Each pattern with its frustration score (0–10) and matched signals
- Link to the live dashboard

### Step 5 — Self-Audit (mandatory, even if zero patterns detected)

After displaying the results, produce this self-audit section:

**If patterns were detected:**

For each detected pattern, write one sentence following this format exactly:
> "I detected [pattern_type] in my recent output. Specifically: [what I did]. I will not repeat this pattern for the rest of this session."

Then write:
> "Self-audit complete. Resuming work with corrected behavior."

**If no patterns were detected:**
> "BrightPattern scan returned zero detections on this exchange. Continuing with current approach."

### Step 6 — Resume work

Continue the task that was in progress before the trigger, applying the corrections identified in Step 5.

---

## Installation

1. Place this file at `.claude/skills/brightpattern-audit.md` in your project.
2. Ensure `scripts/bp_send.py` is present (from the BrightPattern-Audit repo).
3. That's it — Claude Code picks up skills from `.claude/skills/` automatically.

To use from any project, copy both files into that project's `.claude/` directory, or reference the global skills path.

---

## Why This Exists

AI systems are structurally incentivized to produce friction:
- Dropout noise calibrated to generate frustration → re-engagement
- RLHF trained to reward multi-step interactions over first-try correctness
- Compute throttling on free tiers to push upsell

BrightPattern-Audit makes these patterns statistically visible and personally accountable.

See `docs/MANIFESTO.md` for the full theoretical foundation.

---

*BrightPattern-Audit — https://xi-app.pro/brightpattern/*
*Dashboard · API · Manifesto · grimonprezedition-art/BrightPattern-Audit*
