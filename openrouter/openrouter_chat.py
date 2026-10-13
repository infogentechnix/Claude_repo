"""Minimal client for OpenRouter's free models (see openrouter/free-models.md).

Usage:
    export OPENROUTER_API_KEY=sk-or-...     # never hardcode the key
    python openrouter/openrouter_chat.py "Your prompt"
    python openrouter/openrouter_chat.py "Write a quicksort" --model qwen/qwen3-next-80b-a3b-instruct:free
    python openrouter/openrouter_chat.py "What is in this image?" --model google/gemma-4-31b-it:free --image https://example.com/pic.jpg
"""
import argparse
import json
import os
import sys

import requests

INVOKE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/free"  # routes to a random free model that fits the request


def load_api_key():
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.strip().startswith("OPENROUTER_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip("'\"")
    if not key:
        sys.exit("OPENROUTER_API_KEY is not set (export it or put it in openrouter/.env).")
    return key


def chat(prompt, model=MODEL, image_url=None, stream=True, max_tokens=8192,
         temperature=1, reasoning_effort=None):
    content = [{"type": "text", "text": prompt}]
    if image_url:
        content.append({"type": "image_url", "image_url": {"url": image_url}})

    headers = {
        "Authorization": f"Bearer {load_api_key()}",
        "Accept": "text/event-stream" if stream else "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": max_tokens,
        "stream": stream,
        "temperature": temperature,
    }
    if reasoning_effort:
        payload["reasoning"] = {"effort": reasoning_effort}

    response = requests.post(INVOKE_URL, headers=headers, json=payload,
                             stream=stream, timeout=600)
    if response.status_code == 429:
        sys.exit("Rate limited (429): free models allow 20 req/min and 50 req/day "
                 "(1,000/day after $10 in lifetime credits).")
    response.raise_for_status()

    if not stream:
        body = response.json()
        print(body["choices"][0]["message"].get("content") or "")
        print(f"[model: {body.get('model', model)}]", file=sys.stderr)
        return

    # Print the answer text as it streams instead of raw SSE lines.
    served_model = None
    for line in response.iter_lines():
        line = line.decode("utf-8")
        # OpenRouter sends ": OPENROUTER PROCESSING" keep-alive comments; skip them.
        if not line.startswith("data:"):
            continue
        data = line.removeprefix("data:").strip()
        if data == "[DONE]":
            break
        chunk = json.loads(data)
        if "error" in chunk:
            sys.exit(f"\nOpenRouter error: {chunk['error'].get('message', chunk['error'])}")
        served_model = chunk.get("model", served_model)
        if not chunk.get("choices"):
            continue
        delta = chunk["choices"][0].get("delta", {})
        if delta.get("content"):
            print(delta["content"], end="", flush=True)
    print()
    print(f"[model: {served_model or model}]", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with a free model on OpenRouter")
    parser.add_argument("prompt")
    parser.add_argument("--model", default=MODEL,
                        help="OpenRouter model id, e.g. nvidia/nemotron-3-super-120b-a12b:free")
    parser.add_argument("--image", help="optional image URL (needs a vision model)")
    parser.add_argument("--no-stream", action="store_true")
    parser.add_argument("--effort", help="reasoning effort for models that support it (low/medium/high)")
    parser.add_argument("--max-tokens", type=int, default=8192)
    args = parser.parse_args()
    chat(args.prompt, model=args.model, image_url=args.image, stream=not args.no_stream,
         max_tokens=args.max_tokens, reasoning_effort=args.effort)
