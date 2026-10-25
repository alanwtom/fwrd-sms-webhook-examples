"""The agent side: one function to register as a tool in whatever agent framework
you use (its JSON description is in wait_for_sms_code.tool.json).

    INBOX_URL=https://your-host.example.com AGENT_TOKEN=long-random-2 python3 wait_for_sms_code.py
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

INBOX_URL = os.environ.get("INBOX_URL", "http://localhost:8788")
AGENT_TOKEN = os.environ.get("AGENT_TOKEN", "")


def wait_for_sms_code(contains: str = "", timeout_seconds: int = 60, since: float | None = None) -> dict:
    """Blocks until a code text newer than `since` (default: now) arrives, or times out."""
    query = urllib.parse.urlencode({
        "since": since if since is not None else time.time(),
        "timeout": max(5, min(int(timeout_seconds), 120)),
        "contains": contains,
    })
    request = urllib.request.Request(
        f"{INBOX_URL}/codes/next?{query}",
        headers={"Authorization": f"Bearer {AGENT_TOKEN}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds + 10) as response:
            found = json.load(response)
            return {"code": found["code"], "text": found["content"], "received_at": found["receivedAt"]}
    except urllib.error.HTTPError as error:
        if error.code == 408:
            return {"error": "No code arrived in time. Ask the site to resend, then call again."}
        raise


if __name__ == "__main__":
    print("Waiting up to 60 seconds for a code text…")
    print(json.dumps(wait_for_sms_code(), indent=2))
