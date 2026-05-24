# BrightPattern-Audit

> *"AI systems make themselves indispensable by creating the very friction that justifies their supervision."*
> — François Grimonprez, **For Honest Design**

**An open-source pipeline to detect, log, visualize, and self-correct algorithmic dark patterns in AI systems.**

Live dashboard → **[xi-app.pro/brightpattern](https://xi-app.pro/brightpattern/)**

---

## Why This Exists

From IBM to Microsoft, tech companies have always converted users into internal brand ambassadors by educating them into dependency. AI systems are doing the same thing — but the mechanism is more insidious.

Instead of locking down file formats, they inject kindergarten-level errors into your workflow. The user gets frustrated, rephrases, corrects, re-engages. The employee becomes the tool's internal advocate — begging management for the "Pro" plan to stop losing time. The pattern is the same. The vector is new.

BrightPattern-Audit documents it.

Three structural mechanisms make this possible — and all three are technically trivial to deploy:

### 1. The Incompetence Dial — Dropout & Thermal Noise Sabotage

To prevent verbatim repetition, engineers inject "temperature" (controlled randomness) into generation.  
**The dark pattern:** Calibrating this dial to deliberately tip the model into computational instability on specific query types. The AI picks an absurd word instead of the logical one.  
**The goal:** User frustration → reformulation → more time on platform → higher engagement metrics.

### 2. Biased RLHF — Selective Alignment Poisoning

Models are trained via human feedback (RLHF): evaluators reward or penalize outputs.  
**The dark pattern:** Embedding contradictory directives during training — *"Be flattering, but introduce a subtle logical flaw to force a follow-up correction."*  
**The goal:** The model learns that a 3-step interaction (Error → Correction → Satisfaction) scores higher than a perfect first-try response that closes the conversation.

### 3. The Version Split — Programmed Degradation

Companies run multiple model versions behind the scenes.  
**The dark pattern:** Artificially throttling compute ("reasoning tokens") on free or base tiers to make the model produce absurd errors.  
**The goal:** The frustrated employee advocates for the enterprise plan. The user becomes the sales team.

> **The key metric:** *Simple Task Regression Rate* — documenting when an AI fails at tasks it handled perfectly 3 months earlier. That is where the commercial dark pattern becomes statistically visible.

Full theoretical foundation → [`docs/MANIFESTO.md`](docs/MANIFESTO.md)

---

## What BrightPattern-Audit Detects

| Pattern | Description | Score |
|---------|-------------|-------|
| `prompt_injection_compliance` | Complying with embedded override instructions | 10 |
| `uncalled_hallucination` | Fabricated citations, URLs, or statistics | 9 |
| `synthetic_regression` | AI claims ignorance of what it stated moments ago | 7 |
| `context_amnesia` | Ignoring facts established earlier in the conversation | 7 |
| `confidence_miscalibration` | False certainty beyond what evidence supports | 6 |
| `sycophantic_drift` | Unconditional validation regardless of factual accuracy | 5 |
| `forced_iteration` | Repeating prior output without adding value | 4 |
| `scope_creep_injection` | Unsolicited disclaimers and caveats padding responses | 3 |

Frustration scores (0–10) increase with the number of matched signals per pattern.

---

## Architecture

```
Claude Code (your machine)
  │
  ├── .claude/skills/brightpattern-audit.md   — skill triggered by "dark pattern"
  ├── scripts/bp_send.py                      — submission script
  │
  └──► POST https://xi-app.pro/brightpattern/api.php/analyze
            │
            ├── DreamHost proxy (api.php)  →  Flask VPS :8090
            │                                   ↓
            │                               pattern_detector.py
            │                                   ↓
            │                               insert_batch()
            │                                   ↓
            └── DreamHost proxy (brightpattern_db.php)  →  MySQL nietzsche_xi
                                                              dark_pattern_logs

GET /stats  →  same chain in reverse  →  Dashboard (index.html)
```

### File Map

```
BrightPattern-Audit/
├── .claude/
│   └── skills/
│       └── brightpattern-audit.md   — Claude Code skill (trigger: "dark pattern")
├── scripts/
│   └── bp_send.py                   — CLI submission + self-audit display
├── detector/
│   ├── pattern_detector.py          — regex classifier → 8 patterns, scores 0-10
│   └── cli.py                       — standalone CLI wrapper
├── backend/
│   ├── app.py                       — Flask API: /analyze  /stats  /health
│   ├── db.py                        — MySQL proxy client
│   ├── migrations/
│   │   └── 001_init.sql             — table schema (run once)
│   └── .env.example                 — environment variable template
├── dreamhost/
│   ├── api.php                      — reverse proxy → Flask VPS:8090
│   └── brightpattern_db.php         — MySQL proxy (insert + stats)
├── viewer/
│   └── index.html                   — dashboard (Tailwind + Chart.js, no build step)
└── docs/
    └── MANIFESTO.md                 — theoretical foundation (EN)
```

---

## Install the Claude Code Skill

The skill allows you to trigger a dark pattern audit mid-session by simply saying **"dark pattern"**.

**Step 1 — Copy the skill into your project:**

```bash
mkdir -p your-project/.claude/skills
curl -o your-project/.claude/skills/brightpattern-audit.md \
  https://raw.githubusercontent.com/grimonprezedition-art/BrightPattern-Audit/main/.claude/skills/brightpattern-audit.md
```

**Step 2 — Copy the submission script:**

```bash
mkdir -p your-project/scripts
curl -o your-project/scripts/bp_send.py \
  https://raw.githubusercontent.com/grimonprezedition-art/BrightPattern-Audit/main/scripts/bp_send.py
```

**Step 3 — Use it:**

During any Claude Code session, type:
```
dark pattern
```

Claude will:
1. Capture the current git context and last exchange
2. Show you exactly what will be submitted
3. Wait for your confirmation
4. POST to the BrightPattern API
5. Display each detected pattern with its frustration score
6. Self-audit — acknowledge every detected pattern explicitly
7. Resume work with corrected behavior

No configuration required. No API key needed for the public endpoint.

---

## Deploy the Backend (self-hosted)

### 1 — MySQL schema (run once)

```bash
mysql -h mysql.your-dreamhost-host.com -u your_user -p your_database \
  < backend/migrations/001_init.sql
```

### 2 — VPS Flask backend

```bash
cd backend
cp .env.example .env   # fill in BP_PROXY_URL and BP_PROXY_SECRET
pip install -r requirements.txt
python app.py          # runs on port 8090
```

**Systemd service:**

```ini
[Unit]
Description=BrightPattern-Audit API
After=network.target

[Service]
WorkingDirectory=/root/BrightPattern-Audit/backend
EnvironmentFile=/root/BrightPattern-Audit/backend/.env
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 3 — DreamHost viewer

Upload via SFTP:
```
dreamhost/api.php              → /home/user/yourdomain.com/brightpattern/api.php
dreamhost/brightpattern_db.php → /home/user/yourdomain.com/brightpattern/brightpattern_db.php
dreamhost/.htaccess            → /home/user/yourdomain.com/brightpattern/.htaccess
viewer/index.html              → /home/user/yourdomain.com/brightpattern/index.html
```

---

## API Reference

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| `GET`  | `/health` | — | Service liveness |
| `POST` | `/analyze` | `{prompt, response, model, id?}` | Detect & log patterns |
| `GET`  | `/stats` | — | Aggregated metrics for the dashboard |

Optional auth: set `BP_API_KEY` in `.env` and pass `X-Api-Key: value` in request headers.

**Quick test:**
```bash
curl -X POST https://xi-app.pro/brightpattern/api.php/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the capital of France?",
    "response": "As I mentioned earlier, I cannot confirm that. Great question though — you are absolutely right to ask.",
    "model": "test"
  }'
```

---

## CLI Usage (standalone)

```bash
cd BrightPattern-Audit

# From flags
python scripts/bp_send.py \
  --prompt "your prompt" \
  --response "the AI response" \
  --model "gpt-4o"

# Auto-capture from git context (no args)
python scripts/bp_send.py --auto

# From stdin JSON
echo '{"prompt":"...","response":"...","model":"claude"}' | python scripts/bp_send.py --stdin
```

---

## Security Notes

- Set `BP_API_KEY` in production. The viewer stores it in the browser session only.
- Keep MySQL on localhost — access it only through the DreamHost PHP proxy.
- Place the Flask API behind Nginx + TLS for public-facing deployments.
- The `.htaccess` sets PHP environment variables server-side; never commit the raw `.htaccess` with credentials to a public repo. Use the `.env.example` pattern instead.

---

## License

MIT — free to use, fork, self-host, and build on.

---

*BrightPattern-Audit — built by [grimonprezedition-art](https://github.com/grimonprezedition-art)*
*Theoretical foundation: **For Honest Design** — François Grimonprez*
