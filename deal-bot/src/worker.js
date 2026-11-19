// Deal Bot: a Telegram bot that answers deal requests in groups that asked for it.
// Runs on Cloudflare Workers (free tier). Telegram sends each message to this worker by webhook.
//
// Secrets / vars (set with wrangler):
//   TELEGRAM_TOKEN   bot token from @BotFather            (secret)
//   WEBHOOK_SECRET   any random string, checked on every request (secret)
//   AMAZON_TAG       your Associates tracking id, e.g. yourname-20
//   ALLOWED_CHATS    optional comma-separated chat ids the bot may answer in ("" = any chat it is added to)
//   LISTEN_PHRASES   "true" to also answer "looking for ..." messages (needs bot privacy mode OFF in that group)

export const DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases.";

const TRIGGERS = [
  /\b(?:looking for|searching for|in the market for|need|want)\s+(?:an?\s+|some\s+|the\s+)?(.{3,80})/i,
  /\b(?:any(?:one|body)?\s+(?:know|seen|found|have)\s+(?:of\s+)?(?:a\s+|any\s+)?(?:good\s+)?deals?\s+(?:on|for))\s+(?:an?\s+|the\s+)?(.{3,80})/i,
  /\bdeals?\s+(?:on|for)\s+(?:an?\s+|the\s+)?(.{3,80})/i,
];

// Pull "under $300", "below 300", "$200-$400", "max 250" out of the text.
export function parseBudget(text) {
  let min = null, max = null, rest = text;
  const range = rest.match(/\$?\s?(\d{1,5}(?:\.\d{1,2})?)\s?(?:-|to)\s?\$?\s?(\d{1,5}(?:\.\d{1,2})?)\b/i);
  if (range && /\$|budget|price|range/i.test(rest)) {
    min = Number(range[1]); max = Number(range[2]); rest = rest.replace(range[0], " ");
  } else {
    const cap = rest.match(/\b(?:under|below|less than|max(?:imum)?|up to|<)\s*\$?\s?(\d{1,5}(?:\.\d{1,2})?)/i);
    if (cap) { max = Number(cap[1]); rest = rest.replace(cap[0], " "); }
  }
  return { min, max, rest };
}

// Turn a message into a clean product query, or null if it isn't a request.
export function extractQuery(text, { command = false } = {}) {
  if (!text) return null;
  let q = text;
  if (!command) {
    const hit = TRIGGERS.map(r => q.match(r)).find(Boolean);
    if (!hit) return null;
    q = hit[1];
  }
  const { min, max, rest } = parseBudget(q);
  q = rest
    .split(/[.?!\n]|\b(?:for my|for a|for the|for christmas|for xmas|thanks|thx|pls|please)\b/i)[0]
    .replace(/[^\p{L}\p{N}\s'+\-\/".]/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
  if (q.length < 2 || q.split(" ").length > 12) return null;
  return { query: q, min, max };
}

export function amazonUrl({ query, min, max }, tag) {
  const u = new URL("https://www.amazon.com/s");
  u.searchParams.set("k", query);
  if (min != null || max != null) {
    // Amazon's price filter takes cents: p_36:MIN-MAX
    const lo = min != null ? Math.round(min * 100) : "";
    const hi = max != null ? Math.round(max * 100) : "";
    u.searchParams.set("rh", `p_36:${lo}-${hi}`);
  }
  u.searchParams.set("s", "review-rank");
  if (tag) u.searchParams.set("tag", tag);
  return u.toString();
}

const esc = s => String(s).replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

export function buildReply(req, tag) {
  const budget = req.max != null
    ? (req.min != null ? ` ($${req.min}–$${req.max})` : ` (under $${req.max})`)
    : "";
  const text =
    `🔎 <b>${esc(req.query)}</b>${esc(budget)}\n` +
    `Top-rated matches on Amazon, sorted by reviews. Check the price and seller before buying.\n\n` +
    `<i>${DISCLOSURE}</i>`;
  return {
    text,
    reply_markup: { inline_keyboard: [[{ text: "See deals on Amazon", url: amazonUrl(req, tag) }]] },
  };
}

const HELP =
  "I find deals on request.\n\n" +
  "• /deal ipad air under 450\n" +
  "• /deal kids headphones\n\n" +
  "In groups where the admin turned it on, I also answer messages like \"looking for an air fryer under $100\".\n\n" +
  `<i>${DISCLOSURE}</i>`;

async function tg(env, method, body) {
  const r = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_TOKEN}/${method}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  return r.ok;
}

export async function handleUpdate(update, env) {
  const msg = update.message || update.channel_post;
  if (!msg || !msg.text || msg.from?.is_bot) return null;
  const chatId = String(msg.chat.id);
  const allowed = (env.ALLOWED_CHATS || "").split(",").map(s => s.trim()).filter(Boolean);
  const isPrivate = msg.chat.type === "private";
  if (!isPrivate && allowed.length && !allowed.includes(chatId)) return null;

  const text = msg.text.trim();
  const cmd = text.match(/^\/(\w+)(?:@\w+)?\s*([\s\S]*)$/);
  let req = null;

  if (cmd) {
    const name = cmd[1].toLowerCase();
    if (name === "start" || name === "help") {
      return { chat_id: msg.chat.id, text: HELP, parse_mode: "HTML" };
    }
    if (name === "chatid") {
      return { chat_id: msg.chat.id, text: `This chat's id: ${chatId}` };
    }
    if (name === "deal" || name === "find") {
      req = extractQuery(cmd[2], { command: true });
      if (!req) return { chat_id: msg.chat.id, reply_to_message_id: msg.message_id, text: "Tell me what to look for, like: /deal ipad air under 450" };
    }
  } else if (isPrivate) {
    req = extractQuery(text, { command: true });
  } else if (env.LISTEN_PHRASES === "true") {
    req = extractQuery(text);
  }
  if (!req) return null;

  const reply = buildReply(req, env.AMAZON_TAG);
  return { chat_id: msg.chat.id, reply_to_message_id: msg.message_id, parse_mode: "HTML", disable_web_page_preview: true, ...reply };
}

// ---------- Discord (slash commands over HTTP interactions; no always-on connection needed) ----------

const hex = h => new Uint8Array((h.match(/../g) || []).map(b => parseInt(b, 16)));

export async function verifyDiscord(request, body, publicKeyHex) {
  const sig = request.headers.get("X-Signature-Ed25519");
  const ts = request.headers.get("X-Signature-Timestamp");
  if (!sig || !ts || !publicKeyHex) return false;
  try {
    const key = await crypto.subtle.importKey("raw", hex(publicKeyHex), { name: "Ed25519" }, false, ["verify"]);
    return await crypto.subtle.verify("Ed25519", key, hex(sig), new TextEncoder().encode(ts + body));
  } catch { return false; }
}

const mdEsc = s => String(s).replace(/([\\*_~`|>\[\]()])/g, "\\$1");

export function handleDiscord(interaction, env) {
  if (interaction.type === 1) return { type: 1 }; // PING
  if (interaction.type !== 2) return null;
  const allowed = (env.ALLOWED_GUILDS || "").split(",").map(s => s.trim()).filter(Boolean);
  if (allowed.length && interaction.guild_id && !allowed.includes(interaction.guild_id)) {
    return { type: 4, data: { content: "This bot isn't enabled in this server.", flags: 64 } };
  }
  const name = interaction.data?.name;
  if (name === "help") {
    return { type: 4, data: { flags: 64, content:
      "Use `/deal item:ipad air under 450` and I'll find top-rated matches on Amazon.\n\n*" + DISCLOSURE + "*" } };
  }
  if (name !== "deal") return null;
  const item = (interaction.data.options || []).find(o => o.name === "item")?.value || "";
  const req = extractQuery(item, { command: true });
  if (!req) return { type: 4, data: { flags: 64, content: "Tell me what to look for, like `/deal item:ipad air under 450`." } };
  const budget = req.max != null ? (req.min != null ? ` ($${req.min}–$${req.max})` : ` (under $${req.max})`) : "";
  return {
    type: 4,
    data: {
      content: `🔎 **${mdEsc(req.query)}**${budget}\nTop-rated matches on Amazon, sorted by reviews. Check the price and seller before buying.\n\n*${DISCLOSURE}*`,
      allowed_mentions: { parse: [] },
      components: [{ type: 1, components: [{ type: 2, style: 5, label: "See deals on Amazon", url: amazonUrl(req, env.AMAZON_TAG) }] }],
    },
  };
}

export const DISCORD_COMMANDS = [
  { name: "deal", description: "Find top-rated Amazon deals", options: [
    { type: 3, name: "item", description: "What you want, e.g. ipad air under 450", required: true } ] },
  { name: "help", description: "How to use the deal bot" },
];

export default {
  async fetch(request, env) {
    if (request.method !== "POST") return new Response("Deal Bot is running.");
    if (new URL(request.url).pathname === "/discord") {
      const body = await request.text();
      if (!(await verifyDiscord(request, body, env.DISCORD_PUBLIC_KEY))) return new Response("invalid signature", { status: 401 });
      let interaction;
      try { interaction = JSON.parse(body); } catch { return new Response("bad request", { status: 400 }); }
      const out = handleDiscord(interaction, env);
      return out ? Response.json(out) : new Response("unknown command", { status: 400 });
    }
    if (request.headers.get("X-Telegram-Bot-Api-Secret-Token") !== env.WEBHOOK_SECRET) {
      return new Response("forbidden", { status: 403 });
    }
    let update;
    try { update = await request.json(); } catch { return new Response("bad request", { status: 400 }); }
    const out = await handleUpdate(update, env);
    if (out) await tg(env, "sendMessage", out);
    return new Response("ok");
  },
};
