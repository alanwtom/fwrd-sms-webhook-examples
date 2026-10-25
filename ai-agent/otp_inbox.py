"""An SMS code inbox an AI agent can wait on, standard library only (Python 3.10+).

Fwrd posts each forwarded text here. Your agent calls GET /codes/next when a site
says "we've texted you a code", and gets the code as soon as the text arrives.

    FWRD_TOKEN=long-random-1 AGENT_TOKEN=long-random-2 python3 otp_inbox.py

Fwrd's webhook URL:  https://your-host.example.com/fwrd?token=long-random-1
Agent call:          GET https://your-host.example.com/codes/next?since=<unix seconds>&timeout=60
                     with the header  Authorization: Bearer long-random-2

Use it only for accounts you own or are allowed to automate. In Fwrd, add a filter
on the webhook destination ("looks like a verification code") so only code texts
leave the phone.
"""
import hmac
import json
import os
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PORT = int(os.environ.get("PORT", "8788"))
FWRD_TOKEN = os.environ.get("FWRD_TOKEN", "")
AGENT_TOKEN = os.environ.get("AGENT_TOKEN", "")
KEEP_SECONDS = 15 * 60  # Codes expire quickly; don't hold them longer than this.
CODE = re.compile(r"(?<!\d)(\d{3,4})[ -]?(\d{3,4})(?!\d)|(?<!\d)(\d{4,8})(?!\d)")

inbox: list[dict] = []
seen_keys: set[str] = set()
arrived = threading.Condition()


def extract_code(text: str):
    m = CODE.search(text)
    if not m:
        return None
    return m.group(3) or (m.group(1) + m.group(2))


def same(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode(), b.encode())


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        url = urlparse(self.path)
        if url.path != "/fwrd":
            return self._json(404, {})
        if not same(parse_qs(url.query).get("token", [""])[0], FWRD_TOKEN):
            return self._json(401, {})
        try:
            length = min(int(self.headers.get("Content-Length") or 0), 256 * 1024)
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._json(400, {})
        content = payload.get("content")
        if not isinstance(content, str):
            return self._json(400, {})

        key = self.headers.get("Idempotency-Key") or ""
        with arrived:
            if key and key in seen_keys:  # Fwrd retried a text we already have.
                return self._json(200, {"ok": True})
            if key:
                seen_keys.add(key)
            now = time.time()
            inbox[:] = [m for m in inbox if now - m["receivedAt"] < KEEP_SECONDS]
            inbox.append({
                "receivedAt": now,
                "code": extract_code(content),
                "content": content,
                "sender": payload.get("sender"),
            })
            arrived.notify_all()
        self._json(200, {"ok": True})

    def do_GET(self):
        url = urlparse(self.path)
        if url.path != "/codes/next":
            return self._json(404, {})
        auth = self.headers.get("Authorization", "")
        if not same(auth, f"Bearer {AGENT_TOKEN}"):
            return self._json(401, {})
        q = parse_qs(url.query)
        since = float(q.get("since", [time.time()])[0])
        timeout = min(float(q.get("timeout", ["60"])[0]), 120)
        contains = q.get("contains", [""])[0].lower()  # optional, e.g. the site's name

        def match():
            for m in inbox:
                if m["receivedAt"] > since and m["code"] and contains in m["content"].lower():
                    return m
            return None

        deadline = time.time() + timeout
        with arrived:
            found = match()
            while found is None and time.time() < deadline:
                arrived.wait(deadline - time.time())
                found = match()
        if found is None:
            return self._json(408, {"error": "no code arrived in time"})
        self._json(200, found)

    def _json(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    if not FWRD_TOKEN or not AGENT_TOKEN:
        sys.exit("Set FWRD_TOKEN and AGENT_TOKEN to two different long random strings.")
    print(f"Listening on http://localhost:{PORT}", flush=True)
    ThreadingHTTPServer(("", PORT), Handler).serve_forever()
