"""Minimal client for Moonshot Kimi K3 via NVIDIA's API catalog.

Usage:
    export NVIDIA_API_KEY=nvapi-...        # never hardcode the key
    python kimi/kimi_k3.py "Your prompt"
    python kimi/kimi_k3.py "What is in this image?" --image https://example.com/pic.jpg
"""
import argparse
import json
import os
import sys

import requests

INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "moonshotai/kimi-k3"


def load_api_key():
    key = os.environ.get("NVIDIA_API_KEY")
    if not key:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.strip().startswith("NVIDIA_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip("'\"")
    if not key:
        sys.exit("NVIDIA_API_KEY is not set (export it or put it in kimi/.env).")
    return key


def chat(prompt, image_url=None, stream=True, max_tokens=16384,
         temperature=1, reasoning_effort="max"):
    content = [{"type": "text", "text": prompt}]
    if image_url:
        content.append({"type": "image_url", "image_url": {"url": image_url}})

    headers = {
        "Authorization": f"Bearer {load_api_key()}",
        "Accept": "text/event-stream" if stream else "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": max_tokens,
        "seed": 0,
        "stream": stream,
        "temperature": temperature,
        "reasoning_effort": reasoning_effort,
    }

    response = requests.post(INVOKE_URL, headers=headers, json=payload,
                             stream=stream, timeout=600)
    response.raise_for_status()

    if not stream:
        message = response.json()["choices"][0]["message"]
        print(message.get("content") or "")
        return

    # Print the answer text as it streams instead of raw SSE lines.
    for line in response.iter_lines():
        if not line:
            continue
        data = line.decode("utf-8").removeprefix("data: ").strip()
        if data == "[DONE]":
            break
        delta = json.loads(data)["choices"][0].get("delta", {})
        if delta.get("content"):
            print(delta["content"], end="", flush=True)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with Kimi K3 on NVIDIA NIM")
    parser.add_argument("prompt")
    parser.add_argument("--image", help="optional image URL")
    parser.add_argument("--no-stream", action="store_true")
    parser.add_argument("--effort", default="max", help="reasoning_effort (e.g. low/medium/high/max)")
    parser.add_argument("--max-tokens", type=int, default=16384)
    args = parser.parse_args()
    chat(args.prompt, image_url=args.image, stream=not args.no_stream,
         max_tokens=args.max_tokens, reasoning_effort=args.effort)
