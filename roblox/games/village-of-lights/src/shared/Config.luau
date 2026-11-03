--!strict
-- Village of Lights (Diwali): every tunable number. Rare items are free drops from lighting diyas, with the
-- odds shown in-game; nothing paid changes the odds.
return {
	storeName = "VillageOfLights_v1",

	-- village
	houses = 8,
	diyasPerHouse = 6,
	villageRadius = 70,
	burnSeconds = 120, -- a lit diya burns this long, then needs relighting
	incomePerLitDiya = 1, -- coins per second to whoever lit it, before multipliers
	lightReward = 5, -- coins for each diya lit, before multipliers
	presses = 4,
	dayLengthSeconds = 720, -- one full day/night cycle

	-- fireworks: when this share of the village is lit, everyone present gets Sparkles
	fireworksAt = 0.9,
	fireworksCooldown = 300,
	sparklesBase = 10,
	sparklesPerDiyaLit = 1, -- extra Sparkles per diya the player lit since the last show

	-- upgrades (coins): tier n costs cost[n]; tier 1 is free
	jar = { capacity = { 3, 6, 10, 16, 25, 40, 60 }, cost = { 0, 120, 900, 6000, 40000, 250000, 1500000 } },
	press = { oil = { 1, 2, 3, 5, 8, 12, 20 }, cost = { 0, 200, 1500, 10000, 70000, 450000, 3000000 } },
	wick = { mult = { 1, 1.5, 2.2, 3.2, 4.6, 6.5, 9 }, cost = { 0, 300, 2500, 18000, 120000, 800000, 5000000 } },

	rebirthBase = 2_000_000,
	rebirthGrowth = 3,
	rebirthBonus = 0.5,

	-- free drops when lighting a diya, rolled per diya lit. bonus = permanent income multiplier for owning one.
	items = {
		{ id = "marigold", name = "Marigold Garland", rarity = "Common", odds = 10, bonus = 0.05, color = Color3.fromRGB(255, 170, 0) },
		{ id = "peacock", name = "Peacock Feather", rarity = "Rare", odds = 250, bonus = 0.15, color = Color3.fromRGB(0, 160, 170) },
		{ id = "goldendiya", name = "Golden Diya", rarity = "Epic", odds = 5000, bonus = 0.5, color = Color3.fromRGB(255, 210, 60) },
		{ id = "lotus", name = "Lotus of Light", rarity = "Legendary", odds = 100000, bonus = 1.5, color = Color3.fromRGB(255, 120, 200) },
		{ id = "star", name = "Star of Diwali", rarity = "Mythic", odds = 1000000, bonus = 5, color = Color3.fromRGB(200, 160, 255) },
	},
	announceFrom = "Epic", -- Epic and rarer finds are announced to the whole server

	-- cosmetic trails bought with Sparkles
	trails = {
		{ id = "saffron", name = "Saffron", cost = 50, colors = { Color3.fromRGB(255, 153, 51), Color3.fromRGB(255, 220, 120) } },
		{ id = "rose", name = "Rose", cost = 150, colors = { Color3.fromRGB(255, 80, 140), Color3.fromRGB(255, 200, 220) } },
		{ id = "peacock", name = "Peacock", cost = 400, colors = { Color3.fromRGB(0, 140, 160), Color3.fromRGB(40, 220, 120) } },
		{ id = "gold", name = "Gold", cost = 1000, colors = { Color3.fromRGB(255, 200, 40), Color3.fromRGB(255, 255, 200) } },
		{ id = "rangoli", name = "Rangoli Rainbow", cost = 3000, colors = { Color3.fromRGB(255, 60, 60), Color3.fromRGB(60, 120, 255) } },
	},

	-- 7-day login streak, named for the five days of Diwali and two days after
	daily = { 150, 300, 600, 1200, 2500, 4000, 8000 },
	dailyNames = { "Dhanteras", "Choti Diwali", "Diwali", "Govardhan Puja", "Bhai Dooj", "Day 6", "Day 7" },

	-- set to real ids after creating them on the Creator Hub (0 = switched off)
	passes = { doubleCoins = 0, bigJar = 0, vip = 0 },
	products = { coinPack = 0 },
	coinPackSeconds = 600,
	vipSpeed = 24, -- default Roblox walk speed is 16
}
