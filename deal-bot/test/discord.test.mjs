import { test } from "node:test";
import assert from "node:assert/strict";
import { webcrypto } from "node:crypto";
import { verifyDiscord, handleDiscord, DISCLOSURE } from "../src/worker.js";

const env = { AMAZON_TAG: "test-20", ALLOWED_GUILDS: "" };
const deal = item => ({ type: 2, guild_id: "g1", data: { name: "deal", options: [{ name: "item", value: item }] } });

test("answers Discord's ping", () => {
  assert.deepEqual(handleDiscord({ type: 1 }, env), { type: 1 });
});

test("/deal returns a tagged link button and the disclosure", () => {
  const out = handleDiscord(deal("ipad air under 450"), env);
  assert.equal(out.type, 4);
  assert.ok(out.data.content.includes(DISCLOSURE));
  assert.match(out.data.content, /under \$450/);
  const url = new URL(out.data.components[0].components[0].url);
  assert.equal(url.searchParams.get("tag"), "test-20");
  assert.equal(url.searchParams.get("rh"), "p_36:-45000");
});

test("blocks servers not on the list", () => {
  const out = handleDiscord(deal("tv"), { ...env, ALLOWED_GUILDS: "other" });
  assert.equal(out.data.flags, 64);
  assert.match(out.data.content, /isn't enabled/);
});

test("verifies Discord request signatures", async () => {
  const kp = await webcrypto.subtle.generateKey({ name: "Ed25519" }, true, ["sign", "verify"]);
  const pub = Buffer.from(await webcrypto.subtle.exportKey("raw", kp.publicKey)).toString("hex");
  const body = JSON.stringify({ type: 1 }), ts = "1700000000";
  const sig = Buffer.from(await webcrypto.subtle.sign("Ed25519", kp.privateKey, new TextEncoder().encode(ts + body))).toString("hex");
  const req = h => ({ headers: { get: k => h[k] } });
  assert.equal(await verifyDiscord(req({ "X-Signature-Ed25519": sig, "X-Signature-Timestamp": ts }), body, pub), true);
  assert.equal(await verifyDiscord(req({ "X-Signature-Ed25519": sig, "X-Signature-Timestamp": ts }), body + " ", pub), false);
});
