# Make

Make's **Webhooks → Custom webhook** module receives Fwrd's texts.

1. In Make, create a scenario. Add the module **Webhooks → Custom webhook**, click **Add**,
   name it "Fwrd", and save. Copy the address (`https://hook.<zone>.make.com/…`).
2. Make now waits for a sample. On your iPhone, open Fwrd, tap **+**, choose **Webhook**,
   paste the address, save, and tap **Send Test Message**. Make reads the structure:
   `content` and `text` (the same message twice; use either), plus `sender` if
   **Include Who Sent It** is on in Fwrd's Settings.
3. Add the next module: Google Sheets **Add a Row**, Slack, Notion, an HTTP request.
   To pull out a code, use **Text parser → Match pattern** with
   `(\d{3,4})[ -]?(\d{3,4})|(\d{4,8})`.
4. Turn the scenario on (**Immediately as data arrives**).

More: <https://www.fwrdsms.com/iphone-sms-to-zapier-make-n8n>
