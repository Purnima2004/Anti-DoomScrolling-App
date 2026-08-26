"""Paper Reset API: mood -> nine cards from real websites on the web."""

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

from discover import (
    CARD_COUNT,
    discover_sites,
    is_blocked,
    normalize_url,
    pick_sites_for_llm,
    site_host,
    sites_for_prompt,
    top_up_sites,
)
from fallbacks import fallback_cards

load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
# Free-tier TPM limits (Aug 2026): scout 30k, 70b 12k, gpt-oss 8k — see console.groq.com/docs/rate-limits
GROQ_MODEL = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
GROQ_MODEL_FALLBACKS = (
    "meta-llama/llama-4-scout-17b-16e-instruct",  # 30,000 TPM
    "llama-3.3-70b-versatile",  # 12,000 TPM
    "openai/gpt-oss-20b",  # 8,000 TPM
)

app = FastAPI(title="Paper Reset")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResetIn(BaseModel):
    mood: str = Field(min_length=1, max_length=80)


def _pollinations_key() -> str:
    return (
        os.getenv("POLLINATIONS_API_KEY", "").strip()
        or os.getenv("POLLINATION_API_KEY", "").strip()
    )


def image_url(prompt: str, seed: int) -> str:
    clean = (prompt or "warm quiet room, no text").strip()[:280]
    path = quote(clean, safe="")
    key = _pollinations_key()
    base = f"https://gen.pollinations.ai/image/{path}?model=flux&width=768&height=768&seed={seed}"
    if key:
        return f"{base}&key={quote(key, safe='')}"
    return f"https://image.pollinations.ai/prompt/{path}?model=flux&width=768&height=768&seed={seed}"


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _system_prompt(sites_block: str) -> str:
    return f"""Escape Instagram doomscrolling. Pick all 9 sites below (use each once).
Every site must be open-and-play: no login, signup, courses, or classes. User opens the tab and feels good immediately.
Return ONLY JSON: {{"cards":[...9]}}
Fields per card: site_index (1-9 from the list), title, micro_action (2 min), why, site_why (hook), image_prompt (no text).
Do not invent URLs. Use site_index only.

Sites:
{sites_block}
"""


def _groq_models() -> list[str]:
    primary = GROQ_MODEL.strip()
    out = [primary] if primary else []
    for m in GROQ_MODEL_FALLBACKS:
        if m not in out:
            out.append(m)
    return out


def _parse_groq_cards(content: str) -> list[dict] | None:
    data = json.loads(_strip_fences(content))
    cards = data.get("cards") if isinstance(data, dict) else data
    if not isinstance(cards, list) or len(cards) < 3:
        return None
    return cards


async def _groq_request(payload: dict, timeout: float) -> httpx.Response:
    key = os.getenv("GROQ_API_KEY", "").strip()
    async with httpx.AsyncClient(timeout=timeout) as client:
        return await client.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload,
        )


def _resolve_site_index(raw_cards: list, pick: list[dict]) -> list[dict]:
    """Map Groq's site_index onto our URLs so a typo can't invent a domain."""
    by_index = {i: s for i, s in enumerate(pick, 1)}
    resolved: list[dict] = []
    for raw in raw_cards:
        if not isinstance(raw, dict):
            continue
        site = None
        try:
            site = by_index.get(int(raw.get("site_index")))
        except (TypeError, ValueError):
            site = None
        if not site:
            url = normalize_url(str(raw.get("site_url") or ""))
            host = site_host(url)
            site = next((s for s in pick if s["url"] == url or site_host(s["url"]) == host), None)
        if not site:
            continue
        resolved.append({**raw, "site_url": site["url"], "site_name": site["name"]})
    return resolved


async def groq_cards(mood: str, sites: list[dict]) -> list[dict] | None:
    if not os.getenv("GROQ_API_KEY", "").strip() or len(sites) < CARD_COUNT:
        return None
    # Exactly 9 sites, compact lines — keeps input under 8k tokens on gpt-oss-20b
    pick = pick_sites_for_llm(sites, CARD_COUNT)
    sites_block = sites_for_prompt(pick)
    user = f'Mood: "{mood}". Write 9 cards, one per site_index 1-{len(pick)}. Return only JSON.'
    timeout = 55 if os.getenv("VERCEL") else 90

    for model in _groq_models():
        payload = {
            "model": model,
            "temperature": 0.9,
            "max_tokens": 3500,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": _system_prompt(sites_block)},
                {"role": "user", "content": user},
            ],
        }
        try:
            r = await _groq_request(payload, timeout)
            if r.status_code == 413:
                continue  # prompt too large for this model — try next
            if r.status_code == 429:
                continue  # rate limited — try next model
            r.raise_for_status()
            content = r.json()["choices"][0]["message"].get("content") or ""
            parsed = _parse_groq_cards(content)
            if parsed:
                return _resolve_site_index(parsed, pick)
        except (httpx.HTTPError, KeyError, json.JSONDecodeError, TypeError, ValueError):
            continue
    return None


def _match_allowed(url: str, allowed: dict[str, dict]) -> dict | None:
    url = normalize_url(url)
    if url in allowed:
        return allowed[url]
    host = site_host(url)
    for u, site in allowed.items():
        if site_host(u) == host:
            return site
    return None


def _normalize_card(
    raw: dict,
    mood: str,
    used_urls: set[str],
    seed: int,
    allowed: dict[str, dict],
) -> dict | None:
    url = normalize_url(str(raw.get("site_url") or ""))
    site = _match_allowed(url, allowed)
    if not site or is_blocked(url):
        return None
    url = site["url"]
    if url in used_urls:
        return None
    used_urls.add(url)
    prompt = str(raw.get("image_prompt") or f"warm illustration for {site['name']}, no text")
    return {
        "title": str(raw.get("title") or site["name"]).strip()[:80],
        "micro_action": str(raw.get("micro_action") or f"Open {site['name']} for two minutes, then leave.").strip()[:240],
        "why": str(raw.get("why") or f"A small visit that fits feeling {mood}.").strip()[:240],
        "image_url": image_url(prompt, seed),
        "site_name": str(raw.get("site_name") or site["name"]).strip()[:80],
        "site_url": url,
        "site_why": str(raw.get("site_why") or site.get("description", "")[:160]).strip()[:160],
    }


def pack_cards(raw_cards: list, mood: str, allowed: dict[str, dict]) -> list[dict]:
    used: set[str] = set()
    out: list[dict] = []
    for i, raw in enumerate(raw_cards):
        if not isinstance(raw, dict):
            continue
        card = _normalize_card(raw, mood, used, random.randint(1, 10_000_000) + i, allowed)
        if card:
            out.append(card)
        if len(out) == CARD_COUNT:
            return out

    # Fill gaps from discovered sites the model skipped
    for site in allowed.values():
        if len(out) == CARD_COUNT:
            break
        url = site["url"]
        if url in used:
            continue
        used.add(url)
        out.append(
            {
                "title": site["name"][:80],
                "micro_action": f"Spend two minutes on {site['name']}, then close the tab.",
                "why": f"A real site we found that fits feeling {mood}.",
                "image_url": image_url(f"calm illustration inspired by {site['name']}, no text", random.randint(1, 10_000_000)),
                "site_name": site["name"][:80],
                "site_url": url,
                "site_why": (site.get("description") or "Worth opening instead of the feed.")[:160],
            }
        )
    return out[:CARD_COUNT]


@app.get("/api/health")
@app.get("/health")
def health():
    return {
        "ok": True,
        "groq": bool(os.getenv("GROQ_API_KEY", "").strip()),
        "groq_model": GROQ_MODEL,
        "pollinations": bool(_pollinations_key()),
    }


@app.post("/api/reset")
@app.post("/reset")
async def reset(body: ResetIn):
    mood = body.mood.strip()[:80]
    discovered, web_count = await discover_sites(mood)
    discovered = top_up_sites(discovered, mood, CARD_COUNT)
    allowed = {s["url"]: s for s in discovered}

    if len(discovered) >= CARD_COUNT and os.getenv("GROQ_API_KEY", "").strip():
        raw = await groq_cards(mood, discovered)
        if raw:
            cards = pack_cards(raw, mood, allowed)
            if len(cards) >= CARD_COUNT:
                source = "web" if web_count >= 3 else "groq"
                return {"mood": mood, "cards": cards[:CARD_COUNT], "source": source}

    # Last resort — static text if search reads and Groq both failed
    fb_allowed = {
        normalize_url(c["site_url"]): {
            "url": normalize_url(c["site_url"]),
            "name": c["site_name"],
            "description": c.get("site_why", ""),
        }
        for c in fallback_cards(mood)
    }
    cards = pack_cards(fallback_cards(mood), mood, fb_allowed)
    return {"mood": mood, "cards": cards, "source": "fallback"}


def _self_check() -> None:
    url = image_url("a red apple on a windowsill", 7)
    assert "pollinations" in url
    assert is_blocked("https://www.instagram.com")
    assert is_blocked("https://example.com/login")
    assert is_blocked("https://ok.com", html='<input type="password">')
    assert not is_blocked("https://www.window-swap.com")
    fb = fallback_cards("burnt out")
    allowed = {normalize_url(c["site_url"]): {"url": normalize_url(c["site_url"]), "name": c["site_name"], "description": c.get("site_why", "")} for c in fb}
    cards = pack_cards(fb, "burnt out", allowed)
    assert len(cards) == 9
    assert all("tiktok" not in c["site_url"] for c in cards)
    resolved = _resolve_site_index(
        [{"site_index": 1, "title": "x", "micro_action": "y", "why": "z"}],
        [{"url": "https://www.window-swap.com", "name": "WindowSwap"}],
    )
    assert resolved[0]["site_url"] == "https://www.window-swap.com"
    print("self-check ok")


if __name__ == "__main__":
    _self_check()
