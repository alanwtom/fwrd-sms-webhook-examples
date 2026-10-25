// A minimal receiver for Fwrd's webhook, with no dependencies (Node 18+).
//
//   FWRD_TOKEN=pick-a-long-random-string node server.mjs
//
// Put it behind HTTPS (Fwrd only posts to https:// addresses on a public hostname),
// then paste this into Fwrd's webhook destination:
//   https://your-host.example.com/fwrd?token=pick-a-long-random-string
//
// Fwrd sends no auth header, so the secret lives in the URL. Fwrd keeps the whole
// URL in the iPhone's Keychain.
import { createServer } from "node:http";
import { timingSafeEqual } from "node:crypto";

const PORT = Number(process.env.PORT ?? 8787);
const TOKEN = process.env.FWRD_TOKEN ?? "";
if (!TOKEN) {
  console.error("Set FWRD_TOKEN to a long random string first.");
  process.exit(1);
}

// Fwrd retries a text at most twice on a 429, a 5xx or a dropped connection, and
// keeps the same Idempotency-Key, so remembering recent keys stops duplicates.
const seenKeys = new Map();
const SEEN_FOR_MS = 10 * 60 * 1000;

// Four to eight digits, optionally split by one space or dash (123 456, 123-456).
export function extractCode(text) {
  const match = text.match(/(?<!\d)(\d{3,4})[ -]?(\d{3,4})(?!\d)|(?<!\d)(\d{4,8})(?!\d)/);
  if (!match) return null;
  return match[3] ?? `${match[1]}${match[2]}`;
}

function tokenMatches(given) {
  const a = Buffer.from(given ?? "");
  const b = Buffer.from(TOKEN);
  return a.length === b.length && timingSafeEqual(a, b);
}

function handleText({ content, sender }) {
  // Replace this with your own work: save it, post it on, start a workflow.
  const code = extractCode(content);
  console.log(JSON.stringify({ receivedAt: new Date().toISOString(), sender: sender ?? null, code, content }));
}

createServer((req, res) => {
  const url = new URL(req.url ?? "/", "http://localhost");
  if (req.method !== "POST" || url.pathname !== "/fwrd") {
    res.writeHead(404).end();
    return;
  }
  if (!tokenMatches(url.searchParams.get("token"))) {
    res.writeHead(401).end();
    return;
  }

  let body = "";
  req.setEncoding("utf8");
  req.on("data", (chunk) => {
    body += chunk;
    if (body.length > 256 * 1024) req.destroy();
  });
  req.on("end", () => {
    let payload;
    try {
      payload = JSON.parse(body);
    } catch {
      res.writeHead(400).end();
      return;
    }
    if (typeof payload?.content !== "string") {
      res.writeHead(400).end();
      return;
    }

    const key = req.headers["idempotency-key"];
    const now = Date.now();
    for (const [k, t] of seenKeys) if (now - t > SEEN_FOR_MS) seenKeys.delete(k);
    if (typeof key === "string" && seenKeys.has(key)) {
      res.writeHead(200).end(); // Already handled: a retry of the same text.
      return;
    }
    if (typeof key === "string") seenKeys.set(key, now);

    // Answer quickly with a 2xx. Fwrd waits up to 15 seconds, and doesn't follow redirects.
    res.writeHead(200, { "Content-Type": "application/json" }).end('{"ok":true}');
    handleText(payload);
  });
}).listen(PORT, () => console.log(`Listening on http://localhost:${PORT}/fwrd`));
