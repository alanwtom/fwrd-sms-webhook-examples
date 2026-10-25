#!/bin/sh
# Sends your endpoint the same request Fwrd sends for one forwarded text, so you can
# build and debug your receiver without waiting for a real SMS.
#
#   ./send-like-fwrd.sh https://your-endpoint.example.com/fwrd
#   ./send-like-fwrd.sh https://your-endpoint.example.com/fwrd "Your code is 123456" "+15555550123"
#
# The third argument adds "sender", which Fwrd only sends when Include Who Sent It is on.
set -eu

URL="${1:?Usage: $0 <https-url> [message] [sender]}"
MESSAGE="${2:-Your verification code is 482913. It expires in 10 minutes.}"
SENDER="${3:-}"

# JSON-escape the values with python3 if it's there, so quotes and line breaks survive.
json_string() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1"
  else
    printf '"%s"' "$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g')"
  fi
}

if [ -n "$SENDER" ]; then
  BODY="{\"content\":$(json_string "$MESSAGE"),\"sender\":$(json_string "$SENDER")}"
else
  BODY="{\"content\":$(json_string "$MESSAGE")}"
fi

# A fresh key per text. Fwrd keeps the same key when it retries the same text.
KEY="$(uuidgen 2>/dev/null || python3 -c 'import uuid; print(uuid.uuid4())')"

curl --silent --show-error --max-time 15 \
  --request POST "$URL" \
  --header "Content-Type: application/json" \
  --header "Idempotency-Key: $KEY" \
  --data "$BODY" \
  --write-out '\nHTTP %{http_code}\n'
