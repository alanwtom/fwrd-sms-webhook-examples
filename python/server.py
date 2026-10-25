"""A minimal receiver for Fwrd's webhook, standard library only (Python 3.10+).

    FWRD_TOKEN=pick-a-long-random-string python3 server.py

Put it behind HTTPS (Fwrd only posts to https:// addresses on a public hostname),
then paste this into Fwrd's webhook destination:

    https://your-host.example.com/fwrd?token=pick-a-long-random-string
"""
import hmac
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PORT = int(os.environ.get("PORT", "8787"))
TOKEN = os.environ.get("FWRD_TOKEN", "")
SEEN_FOR_SECONDS = 600
seen_keys: dict[str, float] = {}

CODE = re.compile(r"(?<!\d)(\d{3,4})[ -]?(\d{3,4})(?!\d)|(?<!\d)(\d{4,8})(?!\d)")


def extract_code(text: str):
    """Four to eight digits, optionally split by one space or dash."""
    m = CODE.search(text)
    if not m:
        return None
    return m.group(3) or (m.group(1) + m.group(2))


def handle_text(content: str, sender):
    # Replace this with your own work: save it, post it on, start a workflow.
    print(json.dumps({
        "receivedAt": datetime.now(timezone.utc).isoformat(),
        "sender": sender,
        "code": extract_code(content),
        "content": content,
    }), flush=True)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        url = urlparse(self.path)
        if url.path != "/fwrd":
            return self._reply(404)
        given = parse_qs(url.query).get("token", [""])[0]
        if not hmac.compare_digest(given.encode(), TOKEN.encode()):
            return self._reply(401)

        length = int(self.headers.get("Content-Length") or 0)
        if length > 256 * 1024:
            return self._reply(413)
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._reply(400)
        if not isinstance(payload.get("content"), str):
            return self._reply(400)

        # Fwrd keeps the same Idempotency-Key when it retries a text.
        key = self.headers.get("Idempotency-Key")
        now = time.time()
        for k, t in list(seen_keys.items()):
            if now - t > SEEN_FOR_SECONDS:
                del seen_keys[k]
        if key and key in seen_keys:
            return self._reply(200)
        if key:
            seen_keys[key] = now

        self._reply(200, b'{"ok":true}')
        handle_text(payload["content"], payload.get("sender"))

    def _reply(self, status, body=b""):
        self.send_response(status)
        if body:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    if not TOKEN:
        sys.exit("Set FWRD_TOKEN to a long random string first.")
    print(f"Listening on http://localhost:{PORT}/fwrd", flush=True)
    ThreadingHTTPServer(("", PORT), Handler).serve_forever()
