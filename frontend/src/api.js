export async function fetchReset(mood) {
  const res = await fetch("/api/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mood }),
  });
  if (!res.ok) {
    throw new Error("Could not make cards");
  }
  return res.json();
}
