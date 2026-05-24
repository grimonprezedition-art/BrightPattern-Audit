"""
BrightPattern-Audit — CLI Entry Point
Usage: python cli.py --prompt "..." --response "..." --model "gpt-4o"
       cat payload.json | python cli.py --stdin
"""

import argparse
import json
import sys

from pattern_detector import detect_to_json


def parse_args():
    parser = argparse.ArgumentParser(
        prog="brightpattern-detect",
        description="Detect AI dark patterns in a conversation turn.",
    )
    parser.add_argument("--prompt", type=str, help="User prompt text")
    parser.add_argument("--response", type=str, help="AI response text")
    parser.add_argument("--model", type=str, default="unknown", help="AI model name")
    parser.add_argument("--id", type=str, default=None, help="Optional conversation ID")
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read JSON payload from stdin: {prompt, response, model, id}",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.stdin:
        raw = sys.stdin.read()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            print(json.dumps({"error": f"Invalid JSON input: {exc}"}))
            sys.exit(1)
        prompt = payload.get("prompt", "")
        response = payload.get("response", "")
        model = payload.get("model", "unknown")
        conv_id = payload.get("id", None)
    else:
        if not args.prompt or not args.response:
            print(json.dumps({"error": "--prompt and --response are required unless --stdin is used"}))
            sys.exit(1)
        prompt = args.prompt
        response = args.response
        model = args.model
        conv_id = args.id

    result = detect_to_json(prompt, response, model, conv_id)
    print(result)


if __name__ == "__main__":
    main()
