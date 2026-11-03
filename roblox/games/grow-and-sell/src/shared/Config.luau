--!strict
-- Every tunable number for Grow & Sell lives here, so a new version of the game is mostly a new Config.
return {
	storeName = "GrowAndSell_v1",
	tiles = 6, -- soil tiles per plot at the start
	maxTiles = 24,
	tileCost = function(owned: number) return math.floor(50 * 1.6 ^ (owned - 6)) end,
	-- seed tiers: grow time (seconds), base harvest value, cost to unlock
	seeds = {
		{ name = "Carrot", grow = 5, value = 5, cost = 0, color = Color3.fromRGB(255, 140, 0) },
		{ name = "Tomato", grow = 8, value = 14, cost = 150, color = Color3.fromRGB(220, 40, 40) },
		{ name = "Corn", grow = 12, value = 40, cost = 1200, color = Color3.fromRGB(250, 220, 60) },
		{ name = "Pumpkin", grow = 18, value = 130, cost = 9000, color = Color3.fromRGB(240, 120, 20) },
		{ name = "Melon", grow = 25, value = 420, cost = 60000, color = Color3.fromRGB(60, 190, 80) },
		{ name = "Golden Apple", grow = 35, value = 1500, cost = 450000, color = Color3.fromRGB(255, 215, 0) },
	},
	rebirthBase = 1_000_000,
	rebirthGrowth = 3,
	rebirthBonus = 0.5, -- +50% income per rebirth
	daily = { 100, 200, 400, 800, 1500, 2500, 5000 },
	-- set these to the real ids after creating the pass and products on Roblox (0 = not live yet)
	passes = { doubleCoins = 0, autoHarvest = 0 },
	products = { coinPack = 0 },
	coinPackSeconds = 600, -- a coin pack is worth 10 minutes of the player's current best income
}
