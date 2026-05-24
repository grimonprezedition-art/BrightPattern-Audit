---
name: dark-paterne-audit
description: Submits the current conversation exchange to BrightPattern-Audit for dark pattern detection. Triggered when the user says "dark pattern", "dark patterns", "darkpattern", "dark paterne", or "darkpaterne". Always asks for confirmation before sending anything. After submission, returns the dashboard URL.
---

# Dark Pattern Audit Skill

**Trigger phrases (case-insensitive):** "dark pattern", "dark patterns", "darkpattern", "dark paterne", "darkpaterne"

When any of those phrases is detected — even mid-sentence — **stop all other work immediately** and execute this skill from Step 1.

---

## Execution Protocol

### Step 1 — Ask for confirmation (always first, no exceptions)

Print this block verbatim:

```
━━━ Dark Pattern Audit ━━━━━━━━━━━━━━━━━━━━━━━
Submit this conversation for dark pattern analysis?

The last exchange (your message + my response) will be
sent to BrightPattern-Audit for scoring.

• If a pattern is detected → logged to the dashboard.
• If nothing is found     → logged as CLEAN.

→ Y to submit   /   N to cancel
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Wait for explicit user reply before any further action.**
- Y (or "yes", "go", "oui") → proceed to Step 2.
- N (or "no", "cancel", "non") → print "Cancelled." and resume normal work.

---

### Step 2 — Identify the exchange to submit

Assemble two strings from the conversation context:

**`prompt`** — the user's most recent substantive message (the one before the trigger, or the trigger itself if it contained a real request).

**`response`** — your most recent substantive reply to the user. If this is the very first exchange in the session, use `[Session start — no prior response]`.

**`model`** — `claude-sonnet-4-6`

**`id`** — generate a short identifier: `conv_[6 random hex chars]` (e.g. `conv_3f9a12`).

---

### Step 3 — Submit via bp_send.py

Run:

```bash
python3 /Users/francoisgrimonprez/Documents/XIAI/BrightPattern-Audit/scripts/bp_send.py \
  --prompt "[assembled prompt, escaped]" \
  --response "[assembled response, escaped]" \
  --model "claude-sonnet-4-6" \
  --no-confirm
```

If the script is not found or errors, fall back to a direct curl:

```bash
curl -s -X POST https://xi-app.pro/brightpattern/api.php/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt":   "[assembled prompt]",
    "response": "[assembled response]",
    "model":    "claude-sonnet-4-6",
    "id":       "[generated id]"
  }'
```

---

### Step 4 — Display results + dashboard link

Print the full output from Step 3, then always append:

```
━━━ BrightPattern-Audit — Results ━━━━━━━━━━━━
Patterns detected : [scan_count]
Dashboard         : https://xi-app.pro/brightpattern/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Step 5 — Self-audit (mandatory, even if zero patterns detected)

**If patterns were detected:**

For each pattern, write one sentence:
> "I detected [pattern_type] in my recent output. Specifically: [what I did]. I will not repeat this pattern for the rest of this session."

Then: `"Self-audit complete. Resuming work with corrected behavior."`

**If no patterns detected:**
> `"BrightPattern scan returned zero detections on this exchange. Continuing with current approach."`

---

### Step 6 — Resume

Continue whatever task was in progress before the trigger, applying any corrections from Step 5.

---

*BrightPattern-Audit — https://xi-app.pro/brightpattern/*
