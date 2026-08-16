# Paper Reset

A small anti-doomscrolling app. You type a low-energy mood. It gives you **nine visual idea cards** — each with an image, a 2-minute action, and a feel-good website from a fixed allowlist. No social feeds. No paid APIs.

- **Text:** [Groq](https://console.groq.com) free key (`llama-3.1-8b-instant`)
- **Images:** [Pollinations](https://image.pollinations.ai) (no key)
- If Groq is missing or rate-limited, curated fallback cards still load

## Run

1. Get a free Groq key at [console.groq.com](https://console.groq.com) (no credit card).
2. Backend:

```bash
cd backend
copy .env.example .env
# paste GROQ_API_KEY=gsk_... into .env
python -m pip install -r requirements.txt
python main.py
uvicorn main:app --reload --port 8000
```

`python main.py` is the self-check (no Groq call). Then start uvicorn.

3. Frontend (second terminal):

```bash
cd frontend
npm install
npm run dev
```

4. Open the Vite URL (usually http://localhost:5173), tap a mood, get nine cards. Images load one after another so the free image host does not choke.

The Groq key stays in `backend/.env`. The browser never sees it.
