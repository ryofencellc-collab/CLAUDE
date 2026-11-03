--!nonstrict
-- Grow & Sell server: builds each player's plot, runs planting and harvesting, upgrades, rebirth,
-- daily reward and purchases. All state is on the server; the client only sends requests.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Framework = ServerScriptService:WaitForChild("Framework")
local Data = require(Framework.Data)
local Economy = require(Framework.Economy)
local DailyReward = require(Framework.DailyReward)
local Monetization = require(Framework.Monetization)
local Analytics = require(Framework.Analytics)
local Config = require(ReplicatedStorage:WaitForChild("Shared").Config)

local data = Data.new(Config.storeName, {
	coins = 0, rebirths = 0, lifetimeCoins = 0, seedTier = 1, tiles = Config.tiles,
	lastClaimDay = -1, streak = 0, tutorialDone = false,
})
local economy = Economy.new(data, Config)
local autoHarvest = {} :: { [Player]: boolean }

-- remotes
local remotes = Instance.new("Folder")
remotes.Name = "Remotes"
remotes.Parent = ReplicatedStorage
local function remote(name: string): RemoteFunction
	local r = Instance.new("RemoteFunction")
	r.Name = name
	r.Parent = remotes
	return r
end
local stateChanged = Instance.new("RemoteEvent")
stateChanged.Name = "State"
stateChanged.Parent = remotes

local function state(player: Player)
	local p = data:Get(player)
	if not p then return nil end
	local nextSeed = Config.seeds[p.seedTier + 1]
	return {
		coins = p.coins, rebirths = p.rebirths, seed = Config.seeds[p.seedTier].name,
		nextSeed = nextSeed and nextSeed.name, nextSeedCost = nextSeed and nextSeed.cost,
		tiles = p.tiles, tileCost = p.tiles < Config.maxTiles and Config.tileCost(p.tiles) or nil,
		rebirthCost = economy:RebirthCost(player), multiplier = economy:Multiplier(player),
		canClaim = DailyReward.CanClaim(p), streak = p.streak, tutorialDone = p.tutorialDone,
	}
end
local function push(player: Player) stateChanged:FireClient(player, state(player)) end

-- plots: one row per player slot, built from parts so the game needs no hand-made assets
local plots = {} :: { [Player]: { model: Model, tiles: { BasePart }, slot: number } }
local SLOT_SPACING = 60

local function freeSlot(): number
	local used = {}
	for _, plot in plots do used[plot.slot] = true end
	local i = 0
	while used[i] do i += 1 end
	return i
end

local function growTile(player: Player, tile: BasePart)
	local p = data:Get(player)
	if not p or tile:GetAttribute("Growing") then return end
	local seed = Config.seeds[p.seedTier]
	tile:SetAttribute("Growing", true)
	local crop = Instance.new("Part")
	crop.Name = "Crop"
	crop.Anchored, crop.CanCollide = true, false
	crop.Shape = Enum.PartType.Ball
	crop.Color = seed.color
	crop.Size = Vector3.new(1, 1, 1)
	crop.Position = tile.Position + Vector3.new(0, 1.5, 0)
	crop.Parent = tile
	local steps = 10
	for i = 1, steps do
		task.wait(seed.grow / steps)
		if not crop.Parent then return end
		local s = 1 + 2 * i / steps
		crop.Size = Vector3.new(s, s, s)
	end
	tile:SetAttribute("Ready", true)
	tile:SetAttribute("Value", seed.value)
	local prompt = tile:FindFirstChildOfClass("ProximityPrompt")
	if prompt then prompt.Enabled = true end
	if autoHarvest[player] then
		task.wait(0.5)
		tile:SetAttribute("Harvest", true) -- picked up by the harvest handler below
	end
end

local function harvest(player: Player, tile: BasePart)
	if not tile:GetAttribute("Ready") then return end
	local p = data:Get(player)
	if not p then return end
	local gained = economy:Add(player, tile:GetAttribute("Value") :: number)
	Analytics.Earn(player, gained, p.coins, "Harvest")
	tile:SetAttribute("Ready", false)
	tile:SetAttribute("Growing", false)
	local prompt = tile:FindFirstChildOfClass("ProximityPrompt")
	if prompt then prompt.Enabled = false end
	local crop = tile:FindFirstChild("Crop")
	if crop then crop:Destroy() end
	if not p.tutorialDone then
		p.tutorialDone = true
		Analytics.Funnel(player, "Onboarding", 3, "FirstHarvest")
	end
	push(player)
	task.spawn(growTile, player, tile) -- replant automatically so the loop never stalls
end

local function addTile(player: Player, plot, index: number)
	local col, row = (index - 1) % 6, math.floor((index - 1) / 6)
	local tile = Instance.new("Part")
	tile.Name = `Tile{index}`
	tile.Anchored = true
	tile.Size = Vector3.new(6, 1, 6)
	tile.Color = Color3.fromRGB(110, 70, 40)
	tile.Material = Enum.Material.Ground
	tile.Position = plot.model:GetPivot().Position + Vector3.new(-18 + col * 7, 0.5, -10 + row * 7)
	tile.Parent = plot.model
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Harvest"
	prompt.HoldDuration = 0
	prompt.MaxActivationDistance = 12
	prompt.Enabled = false -- shown once the crop is ready
	prompt.Parent = tile
	prompt.Triggered:Connect(function(who) if who == player then harvest(player, tile) end end)
	tile:GetAttributeChangedSignal("Harvest"):Connect(function()
		if tile:GetAttribute("Harvest") then
			tile:SetAttribute("Harvest", false)
			harvest(player, tile)
		end
	end)
	table.insert(plot.tiles, tile)
	task.spawn(growTile, player, tile)
end

local function buildPlot(player: Player, profile)
	local slot = freeSlot()
	local model = Instance.new("Model")
	model.Name = `{player.Name}'s Farm`
	local base = Instance.new("Part")
	base.Name = "Base"
	base.Anchored = true
	base.Size = Vector3.new(50, 1, 40)
	base.Color = Color3.fromRGB(80, 160, 60)
	base.Material = Enum.Material.Grass
	base.Position = Vector3.new(slot * SLOT_SPACING, 0, 0)
	base.Parent = model
	model.PrimaryPart = base
	model.Parent = workspace
	local plot = { model = model, tiles = {}, slot = slot }
	plots[player] = plot
	for i = 1, profile.tiles do addTile(player, plot, i) end
	player.CharacterAdded:Connect(function(char)
		task.wait(0.2)
		char:PivotTo(CFrame.new(base.Position + Vector3.new(0, 5, 18)))
	end)
	if player.Character then player.Character:PivotTo(CFrame.new(base.Position + Vector3.new(0, 5, 18))) end
end

data.Loaded:Connect(function(player: Player, profile)
	Analytics.Funnel(player, "Onboarding", 1, "Joined")
	buildPlot(player, profile)
	Analytics.Funnel(player, "Onboarding", 2, "PlotBuilt")
	push(player)
end)
Players.PlayerRemoving:Connect(function(player)
	local plot = plots[player]
	if plot then plot.model:Destroy() end
	plots[player], autoHarvest[player] = nil, nil
	economy.passMultiplier[player] = nil
end)

-- requests from the client
remote("UpgradeSeed").OnServerInvoke = function(player)
	local p = data:Get(player)
	local nextSeed = p and Config.seeds[p.seedTier + 1]
	if not nextSeed or not economy:Spend(player, nextSeed.cost) then return false end
	p.seedTier += 1
	Analytics.Spend(player, nextSeed.cost, p.coins, "Seed")
	Analytics.Progress(player, "SeedTier", p.seedTier)
	push(player)
	return true
end

remote("BuyTile").OnServerInvoke = function(player)
	local p = data:Get(player)
	if not p or p.tiles >= Config.maxTiles then return false end
	local cost = Config.tileCost(p.tiles)
	if not economy:Spend(player, cost) then return false end
	p.tiles += 1
	Analytics.Spend(player, cost, p.coins, "Tile")
	addTile(player, plots[player], p.tiles)
	push(player)
	return true
end

remote("Rebirth").OnServerInvoke = function(player)
	local ok = economy:Rebirth(player, function(p)
		p.seedTier, p.tiles = 1, Config.tiles
	end)
	if ok then
		local plot = plots[player]
		if plot then
			for _, t in plot.tiles do t:Destroy() end
			plot.tiles = {}
			for i = 1, Config.tiles do addTile(player, plot, i) end
		end
		local p = data:Get(player)
		Analytics.Progress(player, "Rebirth", p and p.rebirths or 0)
		push(player)
	end
	return ok
end

remote("ClaimDaily").OnServerInvoke = function(player)
	local p = data:Get(player)
	if not p then return nil end
	local reward, streak = DailyReward.Claim(p, Config.daily)
	if reward then
		economy:Add(player, reward)
		Analytics.Earn(player, reward, p.coins, "Daily")
	end
	push(player)
	return reward, streak
end

-- purchases (ids are 0 until created on Roblox, which keeps them inactive)
Monetization.Passes(data, {
	[Config.passes.doubleCoins] = function(player) economy.passMultiplier[player] = 2; push(player) end,
	[Config.passes.autoHarvest] = function(player) autoHarvest[player] = true end,
})
Monetization.Products(data, {
	[Config.products.coinPack] = function(player, profile)
		local best = Config.seeds[profile.seedTier]
		local perSecond = best.value / best.grow * profile.tiles
		economy:Add(player, perSecond * Config.coinPackSeconds)
		push(player)
	end,
})
