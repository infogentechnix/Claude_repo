> Made by Omnideck. Find out how in [this video](https://youtu.be/1R61g29fnhk).

# OpenRouter Free Models — Comprehensive Guide

## Rate Limits (All Free Models)

| Credits Purchased (lifetime) | Requests / Minute | Requests / Day |
|---|---|---|
| **Less than $10** | 20 | 50 |
| **$10 or more** | 20 | 1,000 |

- Limits are **account-wide**, not per-model — making extra API keys doesn't help.
- If your credit balance goes **negative**, you may get `402` errors even on free models.
- **Paid variants** of the same models have **no platform-level request cap**.
- Rate limit errors return `429` with `X-RateLimit-*` headers.

---

## General Purpose / Reasoning

| Model | Context | Max Output | Modalities | Notes |
|---|---|---|---|---|
| **NVIDIA Nemotron 3 Ultra** (`nvidia/nemotron-3-ultra-550b-a55b:free`) | 1M | 65K | Text→Text | 550B MoE (55B active). Hybrid Transformer-Mamba. Largest free model. |
| **NVIDIA Nemotron 3 Super** (`nvidia/nemotron-3-super-120b-a12b:free`) | 262K (provider-limited) | 262K | Text→Text | 120B MoE (12B active). Great for multi-agent apps. |
| **Tencent Hy3** (`tencent/hy3:free`) | 262K | 262K | Text→Text | 295B MoE (21B active). Top-ranked in academia & marketing. ⚠️ *Deprecating July 2026.* |
| **Qwen3 Next 80B** (`qwen/qwen3-next-80b-a3b-instruct:free`) | 262K | — | Text→Text | 80B MoE (3B active). Multilingual, no "thinking" traces. |
| **OpenAI gpt-oss-20b** (`openai/gpt-oss-20b:free`) | 131K | 32K | Text→Text | 21B MoE (3.6B active). Apache 2.0 license. |
| **Meta Llama 3.3 70B** (`meta-llama/llama-3.3-70b-instruct:free`) | 65K (provider-limited) | — | Text→Text | Multilingual. ⚠️ *Deprecating July 2026.* |
| **Meta Llama 3.2 3B** (`meta-llama/llama-3.2-3b-instruct:free`) | 131K | — | Text→Text | Smallest free model by params. ⚠️ *Deprecating July 2026.* |
| **NVIDIA Nemotron Nano 9B V2** (`nvidia/nemotron-nano-9b-v2:free`) | 128K | — | Text→Text | Unified reasoning + non-reasoning. |
| **NVIDIA Nemotron Nano 30B A3B** (`nvidia/nemotron-3-nano-30b-a3b:free`) | 256K | — | Text→Text | 30B MoE (3B active). High compute efficiency. |
| **Nous Hermes 3 405B** (`nousresearch/hermes-3-llama-3.1-405b:free`) | 131K | — | Text→Text | Based on Llama 3.1 405B. Great for roleplay & agentic tasks. ⚠️ *Deprecating July 2026.* |

---

## Coding

| Model | Context | Max Output | Notes |
|---|---|---|---|
| **Qwen3 Coder 480B** (`qwen/qwen3-coder:free`) | 262K (provider-limited) | 262K | 480B MoE (35B active). **Largest context of any free model.** ⚠️ *Deprecating July 2026.* |
| **Poolside Laguna M.1** (`poolside/laguna-m.1:free`) | 262K | 32K | Flagship coding agent. Highest token volume of any free model. |
| **Poolside Laguna XS 2.1** (`poolside/laguna-xs-2.1:free`) | 262K | 32K | Compact coding agent (33B-A3B category). |
| **Cohere North Mini Code** (`cohere/north-mini-code:free`) | 256K | 64K | 30B MoE (3B active). **Only free model with content moderation enabled.** |

---

## Multimodal (Vision / Video / Audio)

| Model | Context | Modalities | Notes |
|---|---|---|---|
| **NVIDIA Nemotron 3 Nano Omni** (`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`) | 256K | **Text + Image + Audio + Video** → Text | Most modalities of any free model. |
| **NVIDIA Nemotron Nano 12B VL** (`nvidia/nemotron-nano-12b-v2-vl:free`) | 128K | Text + Image + Video → Text | Hybrid Transformer-Mamba. Great for video understanding. |
| **Google Gemma 4 31B** (`google/gemma-4-31b-it:free`) | 262K | Text + Image + Video → Text | Dense 30.7B model. Configurable thinking mode + function calling. |
| **Google Gemma 4 26B A4B** (`google/gemma-4-26b-a4b-it:free`) | 131K (provider-limited) | Text + Image + Video → Text | MoE 25.2B (3.8B active). Near-31B quality at lower compute. |

---

## Specialized

| Model | Context | Purpose | Notes |
|---|---|---|---|
| **NVIDIA Nemotron 3.5 Content Safety** (`nvidia/nemotron-3.5-content-safety:free`) | 128K | Content moderation / guardrails | 4B params, fine-tuned from Gemma-3-4B. **Not a general chat model.** |
| **Venice Dolphin Mistral 24B** (`cognitivecomputations/dolphin-mistral-24b-venice-edition:free`) | 32K | Uncensored chat / roleplay | ⚠️ *Deprecating July 2026.* Smallest context window. |

---

## Meta / Router

| Model | Context | Notes |
|---|---|---|
| **OpenRouter Free Router** (`openrouter/free`) | 200K | Not a model — **routes to random free models** matching your request. Good for general-purpose use without picking a specific model. |

---

## ⚠️ Not Truly Free (Music Generation)

| Model | Real Cost |
|---|---|
| **Google Lyria 3 Pro Preview** (`google/lyria-3-pro-preview`) | $0.08 per full song |
| **Google Lyria 3 Clip Preview** (`google/lyria-3-clip-preview`) | $0.04 per 30-second clip |

These show $0 token pricing in the API but charge **per generation**.

---

## Models Being Deprecated

| Model | Deprecation Date |
|---|---|
| `tencent/hy3:free` | July 21, 2026 |
| `qwen/qwen3-coder:free` | July 19, 2026 |
| `cognitivecomputations/dolphin-mistral-24b-venice-edition:free` | July 19, 2026 |
| `meta-llama/llama-3.3-70b-instruct:free` | July 19, 2026 |
| `meta-llama/llama-3.2-3b-instruct:free` | July 19, 2026 |
| `nousresearch/hermes-3-llama-3.1-405b:free` | July 19, 2026 |

---

## Key Takeaways

1. **21 truly free models** are available (plus the router and 2 paid-per-generation music models).
2. **Default limit: 50 requests/day** — bump it to **1,000/day** by purchasing ≥$10 in credits (you don't have to spend them on free models).
3. **6 models are being deprecated** around July 19-21, 2026 — the older generation (Llama 3.x, Hermes 3, Qwen3 Coder, Dolphin Mistral, Tencent Hy3).
4. **Best for coding:** Qwen3 Coder (largest context), Poolside Laguna M.1 (highest usage), Cohere North Mini Code.
5. **Best for multimodal:** Nemotron 3 Nano Omni (accepts text, image, audio, and video).
6. **Best for raw reasoning:** Nemotron 3 Ultra (550B, 1M context) or Tencent Hy3 (295B).
7. **Easiest option:** `openrouter/free` — just let OpenRouter pick the model for you.
