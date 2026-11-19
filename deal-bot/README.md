# Deal Bot

A Telegram bot that answers deal requests in your shopping groups around the clock. It replies with an Amazon link carrying your affiliate tag, and every reply includes the required disclosure.

**What it answers**
- `/deal ipad air under 450` in any group it's in.
- Direct messages to the bot: just type what you want.
- Optional: "looking for an air fryer under $100" style messages, in groups where you switch this on.

**What it won't do**
- Post anywhere it wasn't added.
- Quote prices. Amazon doesn't allow prices copied from its pages; live prices come later through Amazon's product API (see step 7).

## Setup (about 20 minutes, all free)

### 1. Amazon Associates
Sign up at affiliate-program.amazon.com. Under **Websites and mobile apps**, list your Telegram groups and the bot's link (`t.me/YourBotName`). Copy your tracking ID (looks like `yourname-20`).

### 2. Make the bot
In Telegram, message **@BotFather** → `/newbot` → choose a name. Copy the **token** it gives you. Never share it or paste it in a group.

### 3. Cloudflare account
Sign up free at dash.cloudflare.com. Then, on a computer with Node.js installed:
```
cd deal-bot
npm install -g wrangler
wrangler login
```

### 4. Configure and deploy
Edit `wrangler.toml` and set `AMAZON_TAG` to your tracking ID. Then:
```
wrangler secret put TELEGRAM_TOKEN     # paste the BotFather token
wrangler secret put WEBHOOK_SECRET     # type any long random string, and save it for step 5
wrangler deploy
```
Wrangler prints your bot's address, like `https://deal-bot.yourname.workers.dev`.

### 5. Connect Telegram to it
Open this in a browser, with your values filled in:
```
https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://deal-bot.yourname.workers.dev&secret_token=<WEBHOOK_SECRET>
```
You should see `"ok":true`. Message your bot `/start` to test it.

### 6. Add it to your groups
- Add the bot to each group, with the admin's OK. Pin a note: "This group's deal bot uses affiliate links. I earn a small commission at no cost to you."
- Type `/chatid` in each group and put the ids in `ALLOWED_CHATS`, so the bot works only there.
- **To also answer "looking for…" messages:** set `LISTEN_PHRASES = "true"`, and in @BotFather choose `/setprivacy` → your bot → **Disable**. Then remove and re-add the bot to the group. Only do this in groups that agreed to it, because the bot can then read every message there.
- Run `wrangler deploy` again after any change to `wrangler.toml`.

### 7. After your first 3 sales
Amazon opens its product API (PA-API) to accounts with qualifying sales. With it, the bot can show live prices, discounts and specific products instead of a search page.

## Rules that keep the account safe
- The disclosure stays on every reply (it's built in; don't remove it).
- Only groups that asked for deals, and only with the admin's OK.
- No WhatsApp groups. There's no allowed bot access there, and unofficial tools get numbers banned.
- Don't add the bot to groups you don't run or weren't invited to.

## Tests
```
npm test
```
