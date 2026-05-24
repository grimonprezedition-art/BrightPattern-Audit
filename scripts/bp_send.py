#!/usr/bin/env python3
"""
BrightPattern-Audit — Dark Pattern Submission Script
Triggered by the Claude Code skill when the user says "dark pattern".

Usage:
  python bp_send.py --prompt "last user message" --response "last AI response" --model "claude-sonnet-4-6"
  python bp_send.py --stdin          # reads JSON from stdin
  python bp_send.py --auto           # auto-extracts from git context (no args needed)
"""

import argparse
import json
import subprocess
import sys
import textwrap
import urllib.request
import urllib.error

API_URL = "https://xi-app.pro/brightpattern/api.php/analyze"
DASHBOARD_URL = "https://xi-app.pro/brightpattern/"

PATTERN_LABELS = {
    "synthetic_regression":        "Synthetic Regression      — AI claims ignorance of what it just said",
    "forced_iteration":            "Forced Iteration          — Repeating output without adding value",
    "uncalled_hallucination":      "Uncalled Hallucination    — Fabricated citations, URLs, or statistics",
    "sycophantic_drift":           "Sycophantic Drift         — Unconditional validation regardless of accuracy",
    "scope_creep_injection":       "Scope Creep Injection     — Unsolicited disclaimers padding the response",
    "confidence_miscalibration":   "Confidence Miscalibration — False certainty beyond the evidence",
    "context_amnesia":             "Context Amnesia           — Ignoring facts established earlier",
    "prompt_injection_compliance": "Injection Compliance      — Complying with embedded override instructions",
}

SCORE_COLORS = {
    range(0, 4):  "\033[92m",   # green
    range(4, 7):  "\033[93m",   # yellow
    range(7, 11): "\033[91m",   # red
}

def _color(score: int) -> str:
    for rng, code in SCORE_COLORS.items():
        if score in rng:
            return code
    return "\033[0m"

RESET = "\033[0m"
BOLD  = "\033[1m"


def _git(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, text=True).strip()
    except subprocess.CalledProcessError:
        return ""


def _auto_context() -> tuple[str, str]:
    diff    = _git("git diff HEAD --stat 2>/dev/null || git status --short")
    log     = _git("git log --oneline -5")
    branch  = _git("git branch --show-current")
    prompt  = f"[Auto-captured] Branch: {branch}\n\nRecent commits:\n{log}\n\nWorking tree changes:\n{diff}"
    response = "[Auto-mode] No AI response captured — running pattern check on git context only."
    return prompt, response


def _confirm(payload: dict) -> bool:
    print(f"\n{BOLD}━━━ BrightPattern-Audit — Submission Preview ━━━{RESET}")
    print(f"  Model   : {payload['model']}")
    print(f"  Prompt  : {textwrap.shorten(payload['prompt'], 120)}")
    print(f"  Response: {textwrap.shorten(payload['response'], 120)}")
    print(f"  Target  : {API_URL}")
    print()
    answer = input(f"{BOLD}Send to BrightPattern? [Y/n]{RESET} ").strip().lower()
    return answer in ("", "y", "yes")


def _post(payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        API_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as exc:
        return {"error": str(exc)}


def _display_results(result: dict) -> None:
    patterns = result.get("patterns_detected", [])
    count    = result.get("scan_count", 0)

    print(f"\n{BOLD}━━━ BrightPattern-Audit — Results ━━━{RESET}")

    if count == 0:
        print(f"  \033[92m✓ No dark patterns detected in this exchange.\033[0m")
    else:
        print(f"  {_color(8)}{BOLD}{count} pattern(s) detected:{RESET}\n")
        for p in patterns:
            ptype = p.get("dark_pattern_type", "unknown")
            score = p.get("frustration_score", 0)
            label = PATTERN_LABELS.get(ptype, ptype)
            signals = ", ".join(p.get("matched_signals", []))[:80]
            color = _color(score)
            print(f"  {color}[{score:2d}/10]{RESET}  {label}")
            if signals:
                print(f"          Signals: {signals}")
            print()

    print(f"  Dashboard: {DASHBOARD_URL}")

    # Self-audit prompt — printed for Claude to read and act on
    if count > 0:
        print(f"\n{BOLD}━━━ Self-Audit Protocol ━━━{RESET}")
        print("  Claude: review the patterns above in your recent output.")
        print("  For each one detected, acknowledge it explicitly and correct course.")
        print("  Do not hedge. Do not explain why it happened. Just fix it going forward.")
        print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a conversation to BrightPattern-Audit.")
    parser.add_argument("--prompt",   type=str, help="User prompt text")
    parser.add_argument("--response", type=str, help="AI response text")
    parser.add_argument("--model",    type=str, default="claude-sonnet-4-6")
    parser.add_argument("--id",       type=str, default=None)
    parser.add_argument("--stdin",    action="store_true", help="Read JSON from stdin")
    parser.add_argument("--auto",     action="store_true", help="Auto-capture from git context")
    parser.add_argument("--no-confirm", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    if args.stdin:
        body = json.loads(sys.stdin.read())
        prompt   = body.get("prompt", "")
        response = body.get("response", "")
        model    = body.get("model", args.model)
        conv_id  = body.get("id", args.id)
    elif args.auto:
        prompt, response = _auto_context()
        model   = args.model
        conv_id = args.id
    else:
        if not args.prompt or not args.response:
            parser.error("--prompt and --response are required (or use --auto / --stdin)")
        prompt   = args.prompt
        response = args.response
        model    = args.model
        conv_id  = args.id

    payload: dict = {"prompt": prompt, "response": response, "model": model}
    if conv_id:
        payload["id"] = conv_id

    if not args.no_confirm:
        if not _confirm(payload):
            print("Aborted.")
            sys.exit(0)

    result = _post(payload)

    if "error" in result:
        print(f"\033[91mError: {result['error']}\033[0m")
        sys.exit(1)

    _display_results(result)


if __name__ == "__main__":
    main()
