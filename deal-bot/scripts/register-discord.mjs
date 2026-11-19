// Registers the /deal and /help slash commands with Discord. Run once, and again if commands change:
//   DISCORD_APP_ID=... DISCORD_BOT_TOKEN=... node scripts/register-discord.mjs
import { DISCORD_COMMANDS } from "../src/worker.js";

const { DISCORD_APP_ID, DISCORD_BOT_TOKEN } = process.env;
if (!DISCORD_APP_ID || !DISCORD_BOT_TOKEN) {
  console.error("Set DISCORD_APP_ID and DISCORD_BOT_TOKEN first.");
  process.exit(1);
}
const r = await fetch(`https://discord.com/api/v10/applications/${DISCORD_APP_ID}/commands`, {
  method: "PUT",
  headers: { "content-type": "application/json", authorization: `Bot ${DISCORD_BOT_TOKEN}` },
  body: JSON.stringify(DISCORD_COMMANDS),
});
console.log(r.ok ? "Commands registered: /deal, /help" : `Discord said ${r.status}: ${await r.text()}`);
