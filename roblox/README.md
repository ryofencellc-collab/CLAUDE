# Roblox game factory

Many distinct games built on one shared engine; each is tested cheaply and kept only if its numbers are
good. All games follow Roblox's rules:

- prices are shown before purchase;
- no paid random items or loot boxes;
- every purchase is granted exactly once;
- everything that decides an outcome runs on the server.

## Layout

| Path | What it is |
|---|---|
| `framework/` | Shared engine. `Data` saves progress (autosave, safe retries, never overwrites a save it failed to read). `Economy` handles coins, multipliers and rebirth. `DailyReward` handles streaks. `Monetization` handles game passes and developer products. `Analytics` reports to Roblox's analytics dashboard. |
| `games/<name>/` | One game: `default.project.json` (Rojo), `src/shared/Config.luau` (every tunable number), `src/server`, `src/client`. |

## Game #1: Grow & Sell

Plant, wait, harvest and sell, then buy better seeds and more soil. Rebirth costs 1M coins and gives a
permanent +50% income. It has a 7-day login streak, an optional 2x Coins pass, an Auto-Harvest pass and
coin packs. The map is built in code, so no hand-made assets are needed.

## Running it (your computer, about 10 minutes the first time)

1. Install **Roblox Studio** (free) and sign in.
2. Install **Rojo**, which turns these files into a Studio place: <https://rojo.space/docs/v7/getting-started/installation/>.
   Install both the command-line tool and the Studio plugin.
3. Open a terminal in `roblox/games/grow-and-sell`, then either:
   - run `rojo build -o GrowAndSell.rbxlx` and open that file in Studio; or
   - run `rojo serve`, open a new Baseplate in Studio, and click **Connect** in the Rojo plugin (this
     keeps it live-synced while I edit).
4. Press **Play** in Studio to test.
5. **File → Publish to Roblox** creates the game. Set its name, icon and thumbnail on the Creator Hub.

## Turning on purchases (after publishing)

1. On the Creator Hub, open the game → Monetization:
   - create two passes, "2x Coins" and "Auto-Harvest";
   - create one developer product, "Coin Pack".
2. Put their ids into `src/shared/Config.luau` (`passes` and `products`).
3. Rebuild and publish. Until the ids are set, purchases stay switched off.

## Scoring each game (from the Creator Hub analytics)

| Metric | Median Roblox game | Top 1% | Keep the game if |
|---|---:|---:|---|
| Next-day return (D1) | 10% | 22% | ≥ 15% after a small ad test |
| Day-7 return (D7) | 1.6% | 9% | ≥ 4% |
| Session length | n/a | n/a | rising week over week |

Run a $20–100 sponsored-ad test per game. Kill a game that misses the bar; give updates and ad budget to
the ones that clear it.

## Game #2: Village of Lights (Diwali, ~Nov 8)

A server-wide co-op loop: light diyas around the village, and when 90% are lit, fireworks pay everyone.
Five free collectibles range from 1 in 10 to the Mythic **Star of Diwali at 1 in 1,000,000**, with the odds
shown in-game. Rangoli Trails are bought with Sparkles. The icon and thumbnail are in `art/`.
Launch steps: [games/village-of-lights/LAUNCH.md](games/village-of-lights/LAUNCH.md).

## Holiday calendar (dates approximate: verify each year)

| Holiday | Date | Game |
|---|---|---|
| Diwali | ~Nov 8 | Village of Lights |
| Thanksgiving | Nov 26 | Harvest Feast (co-op cooking) |
| Hanukkah | ~Dec 4–12 | Eight Nights (8-day login and nightly mini-game) |
| Christmas | Dec 25 | Gift Factory (workshop tycoon and sleigh runs) |
| Kwanzaa | Dec 26–Jan 1 | Seven Principles (7-day community build) |
| Lunar New Year | ~Feb 6 | Dragon Parade (rhythm) |
| Ramadan → Eid al-Fitr | ~Feb 8 → ~Mar 9 | Lantern Market (decorate, cook iftar, give) |
| Nowruz | ~Mar 20 | Spring Reset (Haft-sin puzzle) |
| Holi | ~Mar 22 | Color War (team map coverage) |

Build around festive traditions (lights, food, colours, kites, gifts), never around religious rituals.

## Next games (each with its own core mechanic, not a reskin)

1. **Mine & Refine:** tycoon. Dig ores, run them through machines, sell the output.
2. **Pet Hatchery:** hatch and level pets with coins earned in-game (no paid eggs), then complete the
   collection.
3. **Obby Rush:** procedurally generated obstacle course with a daily seed and a speedrun leaderboard.
4. **Restaurant Rush:** serve customers, upgrade the kitchen, open new locations.
5. **Survive the Night:** co-op horror lite for teens and adults.
