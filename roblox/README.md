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

## Next games (each with its own core mechanic, not a reskin)

1. **Mine & Refine:** tycoon. Dig ores, run them through machines, sell the output.
2. **Pet Hatchery:** hatch and level pets with coins earned in-game (no paid eggs), then complete the
   collection.
3. **Obby Rush:** procedurally generated obstacle course with a daily seed and a speedrun leaderboard.
4. **Restaurant Rush:** serve customers, upgrade the kitchen, open new locations.
5. **Survive the Night:** co-op horror lite for teens and adults.
