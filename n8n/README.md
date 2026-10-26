# n8n

Two workflows to import:

- `fwrd-sms-to-n8n.workflow.json`: a **Webhook** node that receives each text from Fwrd, and a
  **Code** node that pulls out the verification code. Add your own nodes after it (Slack, an AI
  Agent, an HTTP Request to your API).
- `fwrd-sms-to-google-sheets.workflow.json`: the same, then **Google Sheets → Append** adds one
  row per text with `received_at`, `sender`, `code` and `text`. Make a sheet with those four
  column headers in row 1, paste its URL into the Google Sheets node, and connect your Google
  account in n8n.

## Set it up

1. In n8n, open **Workflows → Import from File** (or paste the JSON onto the canvas) and pick
   one of the two workflow files.
2. Open the **Fwrd webhook** node. Copy the **Production URL**. It ends in `/webhook/fwrd-sms`
   (or `/webhook/fwrd-sms-sheet`).
   (The test URL only listens while you have the editor open and click "Listen for test event".)
3. **Activate** the workflow (the toggle at the top). Production URLs only answer when it's active.
4. On your iPhone, open Fwrd, tap **+**, choose **Webhook**, paste the production URL, and save.
   n8n Cloud and any self-hosted n8n with a public `https://` address both work. Fwrd doesn't
   post to `localhost`, IP addresses or `.local` names.
5. Make the Shortcuts Message automation if you haven't: <https://www.fwrdsms.com/guides/automation>.

Each text then arrives as one execution. In the Code node, `$json.body.content` is the message
and `$json.body.sender` is who sent it (only when **Include Who Sent It** is on in Fwrd's Settings).

## Make it private

Fwrd sends no auth header. Either use a long, unguessable path instead of `fwrd-sms`, or add
`?token=<long random string>` to the URL you paste into Fwrd and check it with an **If** node
on `{{$json.query.token}}`.

More: <https://www.fwrdsms.com/iphone-sms-to-zapier-make-n8n> ·
[n8n's Webhook node docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)
