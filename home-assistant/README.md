# Home Assistant

One automation to paste: [`fwrd-sms-notify.yaml`](fwrd-sms-notify.yaml). A **Webhook** trigger
receives each text from Fwrd and shows it as a Home Assistant notification (the bell in the
sidebar). Swap the action for your phone's notify action, a speaker announcement or a light.

## Set it up

1. In Home Assistant, go to **Settings → Automations & scenes → Create automation → Create new
   automation**, open the three-dot menu, choose **Edit in YAML**, and paste the file.
2. Change `webhook_id` to a long random string only you know. Webhooks have no other password.
3. Get the `https://` address:
   - **Home Assistant Cloud:** save, go to **Settings → Cloud**, turn on this automation's webhook
     and copy its link. Keep `local_only: true`.
   - **Your own HTTPS domain:** the address is `https://your-domain/api/webhook/<webhook_id>`.
     Set `local_only: false`, because the iPhone posts from wherever it is.
4. On your iPhone, open Fwrd, add a **Webhook** destination, paste the address, and send the test.
5. Make the Shortcuts Message automation if you haven't: <https://www.fwrdsms.com/guides/automation>.

In templates, `trigger.json.text` (or `trigger.json.content`) is the message. `trigger.json.sender`
is who sent it, only when **Include Who Sent It** is on in Fwrd's Settings.

Fwrd doesn't post to `homeassistant.local`, `http://` or IP addresses, so a home-network-only
address won't save. Don't use a webhook automation to open locks or garage doors.

Checked on 2026-11-12, but not yet run in a live Home Assistant:

- Against Home Assistant's webhook trigger code: it reads the body as `trigger.json` when the
  Content-Type contains "json", and Fwrd sends `application/json`.
- The templates were rendered in a Jinja engine with Fwrd's exact request bodies. That gave
  "New text" (or "Text from +15555550123") and the message unchanged.

More: <https://www.fwrdsms.com/blog/iphone-texts-to-home-assistant> ·
[Home Assistant's webhook trigger docs](https://www.home-assistant.io/docs/automation/trigger/#webhook-trigger)
