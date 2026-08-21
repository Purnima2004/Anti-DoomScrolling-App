"""Find calming sites: web search when it works, live reads always."""

from __future__ import annotations

import asyncio
import re
import time
from html import unescape
from urllib.parse import urlparse

import httpx
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException

from fallbacks import SITES, mood_key

CARD_COUNT = 9

BLOCKED = (
    "instagram.com",
    "tiktok.com",
    "twitter.com",
    "x.com",
    "reddit.com",
    "facebook.com",
    "youtube.com",
    "youtu.be",
    "pinterest.com",
    "snapchat.com",
    "threads.net",
    "linkedin.com",
    "news.google",
    "cnn.com",
    "bbc.com",
    "nytimes.com",
    # courses / login walls — not open-and-play
    "khanacademy.org",
    "duolingo.com",
    "coursera.org",
    "udemy.com",
    "edx.org",
    "skillshare.com",
    "masterclass.com",
    "futureme.org",
    "insighttimer.com",
    "lichess.org/learn",
)

_LOGIN_HINTS = re.compile(
    r"\b(sign up|sign in|log in|login|create an account|enroll|subscription|free trial|"
    r"start your course|online course|classroom|lesson plan)\b",
    re.I,
)

_TITLE = re.compile(r"<title[^>]*>([^<]+)</title>", re.I)
_META_DESC = re.compile(
    r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
    re.I,
)
_OG_DESC = re.compile(
    r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
    re.I,
)
_OG_TITLE = re.compile(
    r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
    re.I,
)

SEARCH_QUERIES = {
    "burnt out": (
        "calm relaxing website burnt out tired no social media",
        "peaceful window nature live stream website",
        "gentle meditation timer website two minutes",
    ),
    "restless": (
        "calm interactive playful website restless antsy",
        "slow driving simulator website relaxing",
        "creative toy website no login calm",
    ),
    "bored": (
        "interesting curious website not social media bored",
        "beautiful museum art website online free",
        "weird wonderful website explore one thing",
    ),
    "foggy": (
        "simple focus website brain fog one small task",
        "calm interactive toy website no login",
        "minimal ambient website short peaceful",
    ),
    "anxious": (
        "calm breathing website anxiety no feed",
        "quiet peaceful website anxious stressed",
        "slow sensory website calm nerves",
    ),
    "numb": (
        "gentle sensory website feel something calm",
        "hopeful good news website short read",
        "soft ambient website cozy not social",
    ),
}


def normalize_url(url: str) -> str:
    u = (url or "").strip().split("#")[0].split("?")[0].rstrip("/")
    if u.startswith("http://"):
        u = "https://" + u[7:]
    return u.lower()


def site_host(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().removeprefix("www.")
    except Exception:
        return ""


def is_blocked(url: str, text: str = "") -> bool:
    host = site_host(url)
    if not host:
        return True
    low = url.lower()
    if any(b in host or b in low for b in BLOCKED):
        return True
    blob = f"{url} {text}".strip()
    return bool(blob and _LOGIN_HINTS.search(blob))


def _clean_html(text: str) -> str:
    return unescape(re.sub(r"\s+", " ", text or "")).strip()


def _parse_page(html: str) -> tuple[str, str]:
    title = ""
    desc = ""
    m = _OG_TITLE.search(html)
    if m:
        title = _clean_html(m.group(1))
    if not title:
        m = _TITLE.search(html)
        if m:
            title = _clean_html(m.group(1))
    m = _OG_DESC.search(html)
    if m:
        desc = _clean_html(m.group(1))
    if not desc:
        m = _META_DESC.search(html)
        if m:
            desc = _clean_html(m.group(1))
    return title[:120], desc[:320]


def _seed_hits(mood: str) -> list[dict]:
    """Known calm sites for this mood — used when search is rate-limited."""
    key = mood_key(mood)
    tagged = [s for s in SITES if key in s["tags"]]
    rest = [s for s in SITES if s not in tagged]
    pool = tagged + rest
    hits = []
    for s in pool:
        url = normalize_url(s["url"])
        hits.append({"url": url, "name": s["name"], "description": "", "from_web": False})
    return hits


def _search_sync(mood: str) -> list[dict]:
    key = mood_key(mood)
    queries = list(SEARCH_QUERIES.get(key, SEARCH_QUERIES["bored"]))
    queries.append(f"relaxing feel good website for {mood} mood not instagram")

    seen: set[str] = set()
    hits: list[dict] = []
    for attempt in range(2):
        try:
            with DDGS() as ddgs:
                for q in queries[:3]:
                    for row in ddgs.text(q, max_results=8):
                        url = normalize_url(row.get("href") or "")
                        body = _clean_html(row.get("body") or "")
                        title = _clean_html(row.get("title") or "")
                        if not url or url in seen or is_blocked(url, f"{title} {body}"):
                            continue
                        seen.add(url)
                        hits.append(
                            {
                                "url": url,
                                "name": _clean_html(row.get("title") or site_host(url)),
                                "description": _clean_html(row.get("body") or ""),
                                "from_web": True,
                            }
                        )
            break
        except DuckDuckGoSearchException:
            if attempt == 0:
                time.sleep(2)
            continue
        except Exception:
            break
    return hits


async def _fetch_preview(client: httpx.AsyncClient, hit: dict) -> dict | None:
    url = hit["url"]
    if is_blocked(url):
        return None
    try:
        r = await client.get(
            url,
            follow_redirects=True,
            headers={"User-Agent": "PaperReset/1.0 (mood discovery bot)"},
        )
        if r.status_code >= 400:
            return None
        ct = r.headers.get("content-type", "")
        if "text/html" in ct:
            title, desc = _parse_page(r.text[:120_000])
        else:
            title, desc = hit.get("name", ""), hit.get("description", "")
        if not title:
            title = hit.get("name") or site_host(url).split(".")[0].replace("-", " ").title()
        if is_blocked(url, f"{title} {desc}"):
            return None
        return {
            "url": normalize_url(str(r.url)),
            "name": title,
            "description": desc or hit.get("description") or "A calm corner of the internet.",
            "from_web": hit.get("from_web", False),
        }
    except (httpx.HTTPError, UnicodeError):
        if hit.get("name"):
            return {
                "url": url,
                "name": hit["name"],
                "description": hit.get("description") or "A calm corner of the internet.",
                "from_web": hit.get("from_web", False),
            }
        return None


async def discover_sites(mood: str, limit: int = 18) -> tuple[list[dict], int]:
    """Search + seed sites, read live page text. Returns (sites, web_search_count)."""
    search_hits = await asyncio.to_thread(_search_sync, mood)
    web_count = len(search_hits)

    merged: list[dict] = []
    seen: set[str] = set()
    for hit in search_hits + _seed_hits(mood):
        url = hit["url"]
        if url in seen:
            continue
        seen.add(url)
        merged.append(hit)
        if len(merged) >= limit:
            break

    previews: list[dict] = []
    async with httpx.AsyncClient(timeout=10) as client:
        tasks = [_fetch_preview(client, h) for h in merged]
        for coro in asyncio.as_completed(tasks):
            item = await coro
            if item:
                previews.append(item)

    # Search hits first, then seeds
    order = {h["url"]: i for i, h in enumerate(merged)}
    previews.sort(key=lambda s: order.get(s["url"], 999))
    return previews[:limit], web_count


def sites_for_prompt(sites: list[dict]) -> str:
    """Compact one-liners — fewer tokens than quoted JSON-ish lines."""
    lines = []
    for i, s in enumerate(sites, 1):
        desc = (s.get("description") or "")[:60].replace("|", " ")
        lines.append(f"{i}. {s['name'][:40]} | {s['url']} | {desc}")
    return "\n".join(lines)


def pick_sites_for_llm(sites: list[dict], n: int = 9) -> list[dict]:
    """Send exactly n sites to Groq — web hits first, then the rest."""
    web = [s for s in sites if s.get("from_web")]
    rest = [s for s in sites if not s.get("from_web")]
    picked: list[dict] = []
    seen: set[str] = set()
    for s in web + rest:
        if s["url"] in seen:
            continue
        seen.add(s["url"])
        picked.append(s)
        if len(picked) == n:
            break
    return picked
