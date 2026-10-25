// A Cloudflare Worker that receives Fwrd's webhook and forwards each text to another
// webhook you own (for example a Google Chat space, or your own API), adding the code
// it finds. Workers get an https:// address on a public hostname, which is what Fwrd needs.
//
// Settings (wrangler secret put …):
//   FWRD_TOKEN   a long random string; Fwrd's URL ends with ?token=<it>
//   NEXT_URL     where to send each text on (optional; without it the text is only logged)
//
// Paste into Fwrd's webhook destination: https://<worker>.<you>.workers.dev/fwrd?token=<FWRD_TOKEN>

const CODE = /(?<!\d)(\d{3,4})[ -]?(\d{3,4})(?!\d)|(?<!\d)(\d{4,8})(?!\d)/;

function extractCode(text) {
  const m = text.match(CODE);
  return m ? (m[3] ?? m[1] + m[2]) : null;
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (request.method !== "POST" || url.pathname !== "/fwrd") {
      return new Response(null, { status: 404 });
    }
    if (!env.FWRD_TOKEN || url.searchParams.get("token") !== env.FWRD_TOKEN) {
      return new Response(null, { status: 401 });
    }

    let payload;
    try {
      payload = await request.json();
    } catch {
      return new Response(null, { status: 400 });
    }
    if (typeof payload?.content !== "string") {
      return new Response(null, { status: 400 });
    }

    const out = {
      content: payload.content,
      sender: payload.sender ?? null,
      code: extractCode(payload.content),
      idempotencyKey: request.headers.get("Idempotency-Key"),
    };

    if (env.NEXT_URL) {
      // Answer Fwrd straight away and send it on in the background.
      ctx.waitUntil(
        fetch(env.NEXT_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(out),
        }),
      );
    } else {
      console.log(JSON.stringify(out));
    }
    return Response.json({ ok: true });
  },
};
