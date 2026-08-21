import { useEffect, useState } from "react";
import { fetchReset } from "./api.js";

const MOODS = ["burnt out", "restless", "bored", "foggy", "anxious", "numb"];
const DEFAULTS = ["/defaults/window.png", "/defaults/road.png", "/defaults/sky.png"];

function Card({ card, index, showImage }) {
  const fallback = DEFAULTS[index % DEFAULTS.length];
  const [src, setSrc] = useState(fallback);

  useEffect(() => {
    setSrc(fallback);
    if (!showImage) return undefined;
    const probe = new Image();
    probe.onload = () => setSrc(card.image_url);
    probe.onerror = () => setSrc(fallback);
    probe.src = card.image_url;
    return () => {
      probe.onload = null;
      probe.onerror = null;
    };
  }, [card.image_url, fallback, showImage]);

  return (
    <article className={`postcard tilt-${index % 3}`}>
      <div className="stamp">{String(index + 1).padStart(2, "0")}</div>
      <div className="photo">
        <img src={src} alt="" className="in" />
      </div>
      <h2>{card.title}</h2>
      <p className="action">{card.micro_action}</p>
      <p className="why">{card.why}</p>
      <div className="postage">
        <div>
          <strong>{card.site_name}</strong>
          <span>{card.site_why}</span>
        </div>
        <a href={card.site_url} target="_blank" rel="noopener noreferrer">
          Open site
        </a>
      </div>
    </article>
  );
}

export default function App() {
  const [mood, setMood] = useState("burnt out");
  const [custom, setCustom] = useState("");
  const [pack, setPack] = useState(null);
  const [visible, setVisible] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const activeMood = custom.trim() || mood;

  async function generate() {
    const asked = activeMood.slice(0, 80);
    if (!asked) return;
    setLoading(true);
    setError("");
    setVisible(0);
    try {
      const data = await fetchReset(asked);
      setPack(data);
    } catch {
      setError("The desk is quiet. Try again in a moment.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!pack?.cards?.length) return undefined;
    setVisible(1);
    const timers = pack.cards.slice(1).map((_, i) =>
      setTimeout(() => setVisible(i + 2), (i + 1) * 1800),
    );
    return () => timers.forEach(clearTimeout);
  }, [pack]);

  return (
    <div className="desk">
      <header className="letterhead">
        <p className="mark">Paper Reset</p>
        <h1>Put the feed down. Pick a mood.</h1>
        <p className="lede">
          Nine postcards. A two-minute idea on each. A website that ends when you close the tab.
        </p>
      </header>

      <section className="composer">
        <div className="chips" role="group" aria-label="Moods">
          {MOODS.map((m) => (
            <button
              key={m}
              type="button"
              className={mood === m && !custom.trim() ? "chip on" : "chip"}
              onClick={() => {
                setMood(m);
                setCustom("");
              }}
            >
              {m}
            </button>
          ))}
        </div>
        <label className="own">
          <span>Or say it your way</span>
          <input
            value={custom}
            onChange={(e) => setCustom(e.target.value)}
            placeholder="e.g. Sunday scaries, can't start"
            maxLength={80}
          />
        </label>
        <div className="row">
          <button type="button" className="go" onClick={generate} disabled={loading}>
            {loading ? "Developing…" : pack ? "Another set" : "generate and see the magic"}
          </button>
          {pack ? (
            <p className="source">
              {pack.source === "web"
                ? "Found on the web for you"
                : pack.source === "groq"
                  ? "Written fresh for your mood"
                  : "From the desk drawer"}
            </p>
          ) : null}
        </div>
        {error ? <p className="err">{error}</p> : null}
      </section>

      {pack ? (
        <section className="tray" aria-live="polite">
          {pack.cards.map((card, i) => (
            <Card key={`${pack.mood}-${card.site_url}-${i}`} card={card} index={i} showImage={visible > i} />
          ))}
        </section>
      ) : (
        <p className="empty">No cards on the desk yet. A mood is enough.</p>
      )}
    </div>
  );
}
