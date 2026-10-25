# Zapier

Zapier's **Webhooks by Zapier → Catch Hook** trigger receives Fwrd's texts. No code needed.

1. In Zapier, create a Zap. For the trigger choose **Webhooks by Zapier**, event **Catch Hook**.
2. Leave "Pick off a Child Key" empty. Continue, and copy the webhook URL
   (`https://hooks.zapier.com/hooks/catch/…`).
3. On your iPhone, open Fwrd, tap **+**, choose **Webhook**, paste the URL, and save. Tap
   **Send Test Message** so Zapier has a sample to map.
4. Back in Zapier, click **Test trigger**. You'll see `content` and `text` (the same message
   twice; use either) and `sender` if **Include Who Sent It** is on in Fwrd's Settings.
5. Add your action: a Google Sheets row, a Notion page, a Gmail draft, a Slack message.
   To pull out just the code, add **Formatter by Zapier → Text → Extract Number**, or a
   **Code by Zapier** step with the regex from [`../node/server.mjs`](../node/server.mjs).
6. Publish the Zap.

Webhooks by Zapier availability depends on your Zapier plan; check Zapier's pricing page.

More: <https://www.fwrdsms.com/iphone-sms-to-zapier-make-n8n>
