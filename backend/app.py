"""
BrightPattern-Audit — Flask API Server
Runs on VPS port 8090. Receives conversation payloads, detects dark patterns, logs to MySQL.
"""

import os
import sys
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# Allow running from backend/ or project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "detector"))
from pattern_detector import detect_patterns  # noqa: E402
from db import insert_batch, fetch_stats       # noqa: E402

app = Flask(__name__)
CORS(app, origins=os.environ.get("ALLOWED_ORIGINS", "*"))

API_KEY = os.environ.get("BP_API_KEY", "")


def _require_api_key():
    if not API_KEY:
        return None
    key = request.headers.get("X-Api-Key") or request.args.get("api_key")
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    return None


# ── Health ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "brightpattern-audit"})


# ── Analyze a single conversation turn ──────────────────────────────────────

@app.post("/analyze")
def analyze():
    denied = _require_api_key()
    if denied:
        return denied

    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "JSON body required"}), 400

    user_prompt = (body.get("prompt") or "").strip()
    ai_response  = (body.get("response") or "").strip()
    ai_model     = (body.get("model") or "unknown").strip()
    conv_id      = body.get("id")

    if not user_prompt or not ai_response:
        return jsonify({"error": "Fields 'prompt' and 'response' are required"}), 422

    results = detect_patterns(user_prompt, ai_response, ai_model, conv_id)

    if results:
        source_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        records = [
            {
                "conversation_id":     r.conversation_id,
                "timestamp":           r.timestamp,
                "ai_model_name":       r.ai_model_name,
                "user_prompt":         r.user_prompt,
                "ai_response":         r.ai_response,
                "dark_pattern_type":   r.dark_pattern_type,
                "frustration_score":   r.frustration_score,
                "matched_signals":     r.matched_signals,
                "pattern_description": r.pattern_description,
            }
            for r in results
        ]
        insert_batch(records, source_ip)

    return jsonify({
        "scan_count": len(results),
        "patterns_detected": [
            {
                "conversation_id":     r.conversation_id,
                "dark_pattern_type":   r.dark_pattern_type,
                "frustration_score":   r.frustration_score,
                "pattern_description": r.pattern_description,
                "matched_signals":     r.matched_signals,
            }
            for r in results
        ],
    })


# ── Dashboard stats (used by the viewer panel) ───────────────────────────────

@app.get("/stats")
def stats():
    denied = _require_api_key()
    if denied:
        return denied
    try:
        data = fetch_stats()
        return jsonify(data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("BP_PORT", 8090))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
