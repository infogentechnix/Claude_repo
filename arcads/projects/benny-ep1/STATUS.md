# Benny & Friends, Ep. 1: "The Great Carrot Giggle"

Full script and character bible: see the prompt pack in the session that created this (13 shots, ~2.5 min).

## Done (part 1, 33.5 s, stitched locally at 1080p)
| Shot | Content | Model | Credits | Arcads asset |
|---|---|---|---|---|
| – | Character sheet, all 7 characters (4K) | nano-banana-2-1 | 24 | 5e320f32-6768-43b8-97a5-8b0b41cfb3ab |
| 2 | Gigi says hello (8 s) | MiniMax H3 720p, character sheet as reference | 48 | c5681e48-1688-4f9f-8d3e-8ddf222b33f5 |
| 3 | Benny finds carrots, helicopter ears (12 s) | 1K still (16) + Kling 3.0 Pro (152) | 168 | 85188306-… / 77f51e98-017d-44f7-9935-79bc3652145a |
| 4+5 | Friends arrive, Benny says "Nope!" (14 s) | MiniMax H3 720p, character sheet as reference | 84 | 46d16c89-e611-4732-8cab-b799441bc276 |

## To do after top-up (MiniMax H3 720p, about 6 credits/s, reference = character sheet)
| Shot | Content | Est. credits |
|---|---|---|
| 1 | Theme intro (reusable every episode) | ~60 |
| 6 | Gigi asks the kids "Should Benny share?" | ~48 |
| 7 | Benny alone, lonely carrots | ~72 |
| 8 | Lightbulb idea, "Hoppity-hop, let's GO!" | ~48 |
| 9 | "I'm sorry" + group hug | ~84 |
| 10 | Carrot picnic party | ~90 |
| 11 | Sing-along song + Shelly "Did… I… miss… it?" | ~90 |
| 12 | Moral + THE END (better as a clean title card made with ffmpeg, free) | ~72 |
| 13 | Next-time tease (Pip's lost boots) | ~48 |
| **Total** | | **~610** (estimate; confirm pricing in Arcads) |

## Cost lessons (measured 2026-10-09)
- MiniMax H3 720p with reference images: **6 credits/s**, the cheapest option. It generates voices and giggles itself, and passing the character sheet as a reference skips the start still.
- Kling 3.0 Pro (1080p): **~12.7 credits/s**. Nano Banana 2.1: 24 credits at 4K, 16 at 1K.
- Stitch, fades and upscale to 1080p locally with ffmpeg (free) instead of with Arcads tools.
- `external-api-temp-uploads/…` paths are **single-use**: upload the reference again for every generation.
- Known glitch: Gigi sometimes appears twice. Add "only ONE ladybug" to prompts.
