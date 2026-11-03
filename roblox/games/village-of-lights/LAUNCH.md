# Village of Lights: launch checklist (Diwali, ~Nov 8)

Publish by **Nov 5–6**. Holiday searches peak in the days before the festival.

## 1. Build and test (10 min)

1. In this folder, run `rojo build -o VillageOfLights.rbxlx` and open the file in Roblox Studio.
2. Press **Play** and check the core loop:
   - fill your jar at a glowing press;
   - light a diya by the houses (coins tick up while it burns);
   - open Collection and Trails;
   - claim the daily reward.
3. **Test → Start (2–3 players):** the fireworks show starts when the village is 90% lit. While testing,
   you can lower `fireworksAt` in `src/shared/Config.luau`.

## 2. Publish (10 min)

1. In Studio: **File → Publish to Roblox → New experience**, named **"Village of Lights 🪔 Diwali"**.
2. In Studio, **Game Settings → Security → Enable Studio Access to API Services** (needed for saving).
3. On the Creator Hub:
   - upload `art/icon_512.png` as the icon and `art/thumbnail_1920x1080.png` as a thumbnail;
   - genre: Simulation;
   - devices: all;
   - complete the **Maturity & Compliance questionnaire** (mild fantasy, no violence; expect "Minimal").
4. Description to paste:

   > Light up the village for Diwali! 🪔 Fill your oil jar at the presses, light diyas in front of every
   > house, and earn coins while they glow. When the whole server lights 90% of the village, a giant
   > fireworks show rewards everyone with Sparkles for Rangoli Trails.
   > Every diya you light has a chance to drop a collectible. Common Marigolds, Rare Peacock Feathers,
   > Epic Golden Diyas, Legendary Lotus of Light... and the Mythic **Star of Diwali (1 in 1,000,000)**.
   > Each one you own boosts your income forever. Exact odds are shown in-game.
   > Upgrade your jar, press and wick, rebirth for +50% income, and keep your 7-day festival streak.
   > Shubh Deepavali! ✨

## 3. Turn on purchases (10 min)

On the Creator Hub, open the game → **Monetization**, create the items below, put their ids into
`src/shared/Config.luau`, then rebuild and publish again.

| Item | Type | Suggested price | Config key |
|---|---|---:|---|
| 2x Coins | Game pass | 199 Robux | `passes.doubleCoins` |
| Double Oil Jar | Game pass | 149 Robux | `passes.bigJar` |
| VIP (speed + gold title) | Game pass | 299 Robux | `passes.vip` |
| Coin Pack (10 min of income) | Developer product | 49 Robux | `products.coinPack` |

No paid item changes the drop odds. That keeps us outside Roblox's paid random items rules.

## 4. Get it seen (day 1)

1. Run a **sponsored ad** on the Creator Hub (Ads Manager), $20–50 over 3 days, targeting all ages.
2. Watch **Creator Hub → Analytics**:
   - next-day return (D1): keep investing if it is **≥ 15%** (the median game is about 10%, the top 1%
     about 22%);
   - average session length;
   - payer conversion.
3. Send me the numbers, and I'll tune `Config.luau` (prices, upgrade costs, odds of the common items) for
   the next version.

## 5. Next year

Turn the event off after the festival, then relaunch it in late October 2027 with new items. Owned
collectibles carry over, so returning players come back.
