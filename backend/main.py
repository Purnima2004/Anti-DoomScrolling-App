"""Paper Reset API: mood -> nine visual idea cards."""

from __future__ import annotations

import json
import os
import random
import re
from urllib.parse import quote

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from fallbacks import fallback_cards, resolve_site, sites_for_prompt

load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-20b"
CARD_COUNT = 9

app = FastAPI(title="Paper Reset")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResetIn(BaseModel):
    mood: str = Field(min_length=1, max_length=80)


def image_url(prompt: str, seed: int) -> str:
    clean = (prompt or "warm quiet room, no text").strip()[:280]
    path = quote(clean, safe="")
    return (
        f"https://image.pollinations.ai/prompt/{path}"
        f"?model=flux&width=768&height=768&seed={seed}"
    )


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _normalize_card(raw: dict, mood: str, used_urls: set[str], seed: int) -> dict:
    site = resolve_site(
        str(raw.get("site_url") or ""),
        str(raw.get("site_name") or ""),
        used_urls,
        mood,
    )
    used_urls.add(site["url"])
    prompt = str(raw.get("image_prompt") or f"warm illustration matching {mood}, no text")
    return {
        "title": str(raw.get("title") or "A small reset").strip()[:80],
        "micro_action": str(raw.get("micro_action") or "Step away for two minutes.").strip()[:240],
        "why": str(raw.get("why") or "A short, finished loop beats an endless one.").strip()[:240],
        "image_url": image_url(prompt, seed),
        "site_name": site["name"],
        "site_url": site["url"],
        "site_why": str(raw.get("site_why") or "A short visit, then you can leave.").strip()[:160],
    }


def pack_cards(raw_cards: list, mood: str) -> list[dict]:
    used: set[str] = set()
    out = []
    for i, raw in enumerate(raw_cards):
        if not isinstance(raw, dict):
            continue
        out.append(_normalize_card(raw, mood, used, seed=random.randint(1, 10_000_000) + i))
        if len(out) == CARD_COUNT:
            return out
    for fb in fallback_cards(mood):
        if fb["site_url"] in used:
            continue
        out.append(_normalize_card(fb, mood, used, seed=random.randint(1, 10_000_000)))
        if len(out) == CARD_COUNT:
            break
    while len(out) < CARD_COUNT:
        filler = resolve_site("", "", used, mood)
        if filler["url"] in used:
            break
        out.append(
            _normalize_card(
                {
                    "title": filler["name"],
                    "micro_action": f"Spend two minutes on {filler['name']}, then close the tab.",
                    "why": "A short finished visit beats an endless feed.",
                    "image_prompt": f"warm illustration inspired by {filler['name']}, no text",
                    "site_name": filler["name"],
                    "site_why": "A small visit, then leave.",
                },
                mood,
                used,
                seed=random.randint(1, 10_000_000),
            )
        )
    return out[:CARD_COUNT]


def _system_prompt() -> str:
    return f"""You help someone who is doomscrolling and low-energy.
Return ONLY JSON: {{"cards":[...9 objects...]}} with exactly 9 cards.
Each card:
- title: short, catchy
- micro_action: one concrete thing, 2 minutes or less. Physical, sensory, or a short visit to the site. Never "open social media", news, or a long study session.
- why: one sentence on why this helps THIS mood
- image_prompt: vibrant illustration, no words or letters in the image
- site_name, site_url, site_why: pick from the allowlist only. Nine DIFFERENT sites.
Never invent URLs. No Instagram, TikTok, Twitter, Reddit, YouTube, Facebook, or news homepages.

Allowlist:
{sites_for_prompt()}
"""


async def groq_cards(mood: str) -> list[dict] | None:
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        return None
    payload = {
        "model": GROQ_MODEL,
        "temperature": 1,
        "max_completion_tokens": 8192,
        "top_p": 1,
        "reasoning_effort": "medium",
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": _system_prompt()},
            {
                "role": "user",
                "content": (
                    f'Mood: "{mood}". '
                    "Pick nine different allowlisted sites that fit this mood. "
                    "Restless=movement/play, burnt out=stillness/nature, bored=curiosity, "
                    "anxious=slow/breath, numb=gentle sensory, foggy=one small clear task. "
                    "Return only the JSON object."
                ),
            },
        ],
    }
    try:
        timeout = 20 if os.getenv("VERCEL") else 90
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json=payload,
            )
            r.raise_for_status()
            msg = r.json()["choices"][0]["message"]
            content = msg.get("content") or ""
        data = json.loads(_strip_fences(content))
        cards = data.get("cards") if isinstance(data, dict) else data
        if not isinstance(cards, list) or len(cards) < 2:
            return None
        return cards
    except (httpx.HTTPError, KeyError, json.JSONDecodeError, TypeError, ValueError):
        return None


@app.get("/api/health")
@app.get("/health")
def health():
    return {"ok": True, "groq": bool(os.getenv("GROQ_API_KEY", "").strip())}


@app.post("/api/reset")
@app.post("/reset")
async def reset(body: ResetIn):
    mood = body.mood.strip()[:80]
    raw = await groq_cards(mood)
    source = "groq" if raw else "fallback"
    cards = pack_cards(raw or fallback_cards(mood), mood)
    return {"mood": mood, "cards": cards, "source": source}


def _self_check() -> None:
    url = image_url("a red apple on a windowsill", 7)
    assert "image.pollinations.ai" in url
    assert "apple" in url
    used: set[str] = set()
    evil = resolve_site("https://evil.example", "Nope", used, "burnt out")
    assert evil["url"].startswith("https://")
    assert "evil" not in evil["url"]
    used.add(evil["url"])
    cards = pack_cards(fallback_cards("burnt out"), "burnt out")
    assert len(cards) == 9
    assert len({c["site_url"] for c in cards}) == 9
    assert all(c["image_url"].startswith("https://image.pollinations.ai/") for c in cards)
    junk = pack_cards(
        [{"title": "X", "site_url": "https://tiktok.com", "site_name": "TikTok"}],
        "anxious",
    )
    assert len(junk) == 9
    assert all("tiktok" not in c["site_url"].lower() for c in junk)
    print("self-check ok")


if __name__ == "__main__":
    _self_check()
