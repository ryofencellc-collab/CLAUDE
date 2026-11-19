import { test } from "node:test";
import assert from "node:assert/strict";
import { extractQuery, amazonUrl, handleUpdate, DISCLOSURE } from "../src/worker.js";

const env = { AMAZON_TAG: "test-20", LISTEN_PHRASES: "true", ALLOWED_CHATS: "" };
const groupMsg = text => ({ message: { message_id: 7, text, chat: { id: -100, type: "supergroup" }, from: { is_bot: false } } });

test("finds requests in natural messages", () => {
  assert.deepEqual(extractQuery("Looking for iPad Air under $450 for my son"), { query: "iPad Air", min: null, max: 450 });
  assert.equal(extractQuery("anyone know a good deal on air fryers?").query, "air fryers");
  assert.equal(extractQuery("Need a PS5 controller pls").query, "PS5 controller");
  assert.deepEqual(extractQuery("deals for kids headphones budget $20-$40"), { query: "kids headphones budget", min: 20, max: 40 });
});

test("ignores ordinary chat", () => {
  assert.equal(extractQuery("happy thanksgiving everyone!"), null);
  assert.equal(extractQuery("lol same"), null);
});

test("builds a tagged search link with a price filter in cents", () => {
  const u = new URL(amazonUrl({ query: "ipad air", min: null, max: 450 }, "test-20"));
  assert.equal(u.searchParams.get("k"), "ipad air");
  assert.equal(u.searchParams.get("rh"), "p_36:-45000");
  assert.equal(u.searchParams.get("tag"), "test-20");
});

test("replies in groups with link and disclosure", async () => {
  const out = await handleUpdate(groupMsg("looking for a robot vacuum under 200"), env);
  assert.ok(out.text.includes(DISCLOSURE));
  assert.equal(out.reply_to_message_id, 7);
  assert.match(out.reply_markup.inline_keyboard[0][0].url, /tag=test-20/);
});

test("stays quiet when listening is off, answers /deal", async () => {
  const off = { ...env, LISTEN_PHRASES: "false" };
  assert.equal(await handleUpdate(groupMsg("looking for a robot vacuum"), off), null);
  const out = await handleUpdate(groupMsg("/deal@MyDealBot robot vacuum under 200"), off);
  assert.match(out.text, /robot vacuum/);
});

test("respects the allowed-chat list", async () => {
  assert.equal(await handleUpdate(groupMsg("/deal tv"), { ...env, ALLOWED_CHATS: "-555" }), null);
});
