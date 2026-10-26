# Fwrd SMS webhook examples

Working examples for receiving iPhone text messages from **[Fwrd](https://www.fwrdsms.com)**'s
webhook destination: n8n, Zapier, Make, a Cloudflare Worker, small Node and Python servers, an
SMS-code inbox for AI agents, and a curl script that sends exactly what Fwrd sends.

Fwrd is an iPhone app that forwards incoming SMS to Email, another phone or iMessage, WhatsApp,
Slack, Discord, Microsoft Teams, Telegram, or your own webhook. It runs from one Message
automation in Apple's Shortcuts app. There's no Fwrd account and no Fwrd server: the iPhone
posts each text straight to your URL.

[Download Fwrd on the App Store](https://apps.apple.com/app/apple-store/id6759069713?pt=128544281&ct=github-examples&mt=8) ·
[Webhook setup guide](https://www.fwrdsms.com/guides/webhook) ·
[Zapier, Make and n8n](https://www.fwrdsms.com/iphone-sms-to-zapier-make-n8n) ·
[Shortcuts automation guide](https://www.fwrdsms.com/guides/automation)

## What Fwrd sends

One HTTPS `POST` per forwarded text:

```http
POST /your/path HTTP/1.1
Content-Type: application/json
Idempotency-Key: 6F9619FF-8B86-D011-B42D-00C04FC964FF

{"content":"Your verification code is 482913. It expires in 10 minutes.","text":"Your verification code is 482913. It expires in 10 minutes."}
```

With **Include Who Sent It** turned on in Fwrd's Settings (off by default) and the Sender field
set on Fwrd's action in Shortcuts, the body gets one more field:

```json
{"content":"Your verification code is 482913. It expires in 10 minutes.","text":"Your verification code is 482913. It expires in 10 minutes.","sender":"+15555550123"}
```

That's all of it. `content` is the message exactly as it arrived, line breaks kept, with nothing
added: no title, no timestamp, no phone number unless you turn on `sender`. `text` is the same
message again, so tools that read `text` (Mattermost and Rocket.Chat incoming webhooks) work
directly. Read either one; they're always identical. The JSON Schema is in
[`payload/fwrd-webhook.schema.json`](payload/fwrd-webhook.schema.json).

### Rules your endpoint should know

These come from the Fwrd iOS app's source, checked on 2026-10-25 against the shipped 1.2.1 and 1.3.1.

| | |
|---|---|
| Address | `https://` only, on a public hostname. Not `localhost`, IP addresses, `.local`, `.lan`, `.internal` or `.test` names. No `user:password@` in the URL, no `#fragment`. |
| Auth | None sent. Put a long random secret in the path or query (`?token=…`). Fwrd stores the whole URL in the iPhone's Keychain. |
| Success | Any `2xx`. Answer within 15 seconds. |
| Redirects | Not followed. A `301`/`302` counts as a failure, so paste the final URL. |
| Retries | On `429`, `5xx` or a dropped connection, at most twice, with short backoff (and `Retry-After` honoured). The same `Idempotency-Key` is kept across retries, so dedupe on it. |
| Which texts | Only new texts that match the Shortcuts automation, and, if you set them, Fwrd's filters on this destination (certain words, looks like a verification code, time of day). |
| When | As each text arrives, while the iPhone is on and online. |
| Google Chat | A `chat.googleapis.com` webhook URL gets only `{"text": …}`, because Google Chat rejects fields it doesn't know. Every other URL gets the body above. |

## Examples

| Folder | What it is |
|---|---|
| [`curl/`](curl/send-like-fwrd.sh) | Send your endpoint the same request Fwrd sends, to build and debug without a real SMS |
| [`node/`](node/server.mjs) | Minimal receiver, no dependencies: token check, dedupe, code extraction |
| [`python/`](python/server.py) | The same in Python, standard library only |
| [`cloudflare-worker/`](cloudflare-worker/worker.js) | A Worker that receives texts and sends them on to another webhook with the code pulled out |
| [`n8n/`](n8n/) | Two importable workflows: pull out the code, or add each text as a Google Sheets row |
| [`zapier/`](zapier/README.md) | Catch Hook → Google Sheets, Notion, Slack… |
| [`make/`](make/README.md) | Custom webhook → any Make module |
| [`ai-agent/`](ai-agent/) | An SMS-code inbox plus a `wait_for_sms_code` tool an AI agent can call during a login |

## Try it in two minutes

```sh
cd node
FWRD_TOKEN=change-me node server.mjs
# in another terminal
../curl/send-like-fwrd.sh "http://localhost:8787/fwrd?token=change-me" "Your code is 123456"
```

Fwrd itself needs a public `https://` address, so for the real thing deploy the receiver (or the
Worker), or use n8n, Zapier or Make.

## Use it responsibly

Forward only texts you're allowed to share, from a phone you own or manage with its owner's
agreement. Where a service offers an authenticator app, passkeys or API tokens, prefer those
over SMS codes. Some banks' terms forbid sharing one-time codes; check before you forward them.

## Pricing

Fwrd is free for 15 forwarded texts a month (one text counts once, however many places it goes).
Fwrd Pro is $4.99 a month or $29.99 a year (US prices, October 2026). These examples are MIT
licensed.

Questions: support@fwrdsms.com · <https://www.fwrdsms.com>
