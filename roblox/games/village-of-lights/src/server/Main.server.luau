--!nonstrict
-- Village of Lights server. Players fill oil jars at the presses and light diyas around the village. Each lit
-- diya pays its lighter while it burns, and lighting can drop a collectible (free, odds shown in-game). When
-- most of the village is lit, fireworks go off and everyone present earns Sparkles for trails.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")
local Lighting = game:GetService("Lighting")

local Framework = ServerScriptService:WaitForChild("Framework")
local Data = require(Framework.Data)
local Economy = require(Framework.Economy)
local DailyReward = require(Framework.DailyReward)
local Monetization = require(Framework.Monetization)
local Analytics = require(Framework.Analytics)
local Config = require(ReplicatedStorage:WaitForChild("Shared").Config)

local data = Data.new(Config.storeName, {
	coins = 0, rebirths = 0, lifetimeCoins = 0, jarTier = 1, pressTier = 1, wickTier = 1,
	sparkles = 0, items = {}, trails = {}, trail = "", diyasLit = 0,
	lastClaimDay = -1, streak = 0, tutorialDone = false,
})
local economy = Economy.new(data, Config)

-- session-only state
local oil = {} :: { [Player]: number }
local litSinceShow = {} :: { [Player]: number }
local bigJar, vip = {} :: { [Player]: boolean }, {} :: { [Player]: boolean }

---------------------------------------------------------------------- remotes
local remotes = Instance.new("Folder")
remotes.Name = "Remotes"
remotes.Parent = ReplicatedStorage
local function fn(name: string): RemoteFunction
	local r = Instance.new("RemoteFunction")
	r.Name = name
	r.Parent = remotes
	return r
end
local function ev(name: string): RemoteEvent
	local r = Instance.new("RemoteEvent")
	r.Name = name
	r.Parent = remotes
	return r
end
local State, Banner, Village = ev("State"), ev("Banner"), ev("Village")

local function jarCapacity(player: Player, p): number
	return Config.jar.capacity[p.jarTier] * (if bigJar[player] then 2 else 1)
end

local function rarityRank(r: string): number
	return ({ Common = 1, Rare = 2, Epic = 3, Legendary = 4, Mythic = 5 })[r] or 0
end

local function collectionBonus(p): number
	local b = 1
	for _, item in Config.items do
		if (p.items[item.id] or 0) > 0 then b += item.bonus end
	end
	return b
end

local function bestItem(p)
	local best = nil
	for _, item in Config.items do
		if (p.items[item.id] or 0) > 0 and (not best or rarityRank(item.rarity) > rarityRank(best.rarity)) then best = item end
	end
	return best
end

local function nextCost(tiers, tier: number): number?
	return tiers.cost[tier + 1]
end

local function state(player: Player)
	local p = data:Get(player)
	if not p then return nil end
	return {
		coins = p.coins, rebirths = p.rebirths, sparkles = p.sparkles, oil = oil[player] or 0,
		capacity = jarCapacity(player, p), multiplier = economy:Multiplier(player),
		jarCost = nextCost(Config.jar, p.jarTier), pressCost = nextCost(Config.press, p.pressTier),
		wickCost = nextCost(Config.wick, p.wickTier), rebirthCost = economy:RebirthCost(player),
		items = p.items, trails = p.trails, trail = p.trail, diyasLit = p.diyasLit,
		canClaim = DailyReward.CanClaim(p), streak = p.streak, tutorialDone = p.tutorialDone,
	}
end
local function push(player: Player) State:FireClient(player, state(player)) end

---------------------------------------------------------------------- the village (built in code)
local diyas = {} :: { BasePart }
local root = Instance.new("Folder")
root.Name = "Village"
root.Parent = workspace

local function part(props): Part
	local p = Instance.new("Part")
	p.Anchored = true
	for k, v in props do (p :: any)[k] = v end
	p.Parent = props.Parent or root
	return p
end

part({ Name = "Ground", Size = Vector3.new(400, 2, 400), Position = Vector3.new(0, -1, 0),
	Color = Color3.fromRGB(150, 110, 70), Material = Enum.Material.Sand })
part({ Name = "Square", Size = Vector3.new(50, 0.4, 50), Position = Vector3.new(0, 0.2, 0),
	Color = Color3.fromRGB(230, 200, 150), Material = Enum.Material.Slate })
-- warm festival night: dim ambient so the diyas carry the scene, but never pitch black
Lighting.OutdoorAmbient = Color3.fromRGB(95, 75, 110)
Lighting.Ambient = Color3.fromRGB(70, 55, 80)
Lighting.Brightness = 2

local spawn = Instance.new("SpawnLocation")
spawn.Anchored, spawn.Size, spawn.Position = true, Vector3.new(10, 1, 10), Vector3.new(0, 0.5, 0)
spawn.Transparency, spawn.CanCollide = 1, true
spawn.Parent = root

-- rangoli on the square: concentric coloured rings
for i, c in { Color3.fromRGB(255, 60, 60), Color3.fromRGB(255, 170, 0), Color3.fromRGB(60, 120, 255), Color3.fromRGB(40, 200, 120) } do
	local ring = part({ Name = `Rangoli{i}`, Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.2, 30 - i * 6, 30 - i * 6),
		CFrame = CFrame.new(0, 0.45 + i * 0.01, 0) * CFrame.Angles(0, 0, math.rad(90)), Color = c, Material = Enum.Material.Neon,
		CanCollide = false })
	ring.Transparency = 0.15
end

local houseColors = { Color3.fromRGB(240, 120, 80), Color3.fromRGB(250, 200, 90), Color3.fromRGB(120, 180, 240),
	Color3.fromRGB(200, 120, 220), Color3.fromRGB(120, 210, 150), Color3.fromRGB(250, 150, 170) }

for h = 1, Config.houses do
	local a = (h / Config.houses) * math.pi * 2
	local pos = Vector3.new(math.cos(a) * Config.villageRadius, 0, math.sin(a) * Config.villageRadius)
	local face = CFrame.lookAt(pos, Vector3.zero)
	local house = Instance.new("Model")
	house.Name = `House{h}`
	house.Parent = root
	part({ Name = "Walls", Size = Vector3.new(22, 14, 16), CFrame = face + Vector3.new(0, 7, 0),
		Color = houseColors[(h - 1) % #houseColors + 1], Material = Enum.Material.Plaster, Parent = house })
	part({ Name = "Roof", Size = Vector3.new(24, 2, 18), CFrame = face + Vector3.new(0, 15, 0),
		Color = Color3.fromRGB(150, 60, 40), Material = Enum.Material.Brick, Parent = house })
	for d = 1, Config.diyasPerHouse do
		local offset = (d - (Config.diyasPerHouse + 1) / 2) * 3.4
		local spot = face * CFrame.new(offset, 0.6, -9.5)
		local diya = part({ Name = `Diya{h}_{d}`, Size = Vector3.new(1.4, 0.6, 1.4), CFrame = spot,
			Color = Color3.fromRGB(170, 90, 40), Material = Enum.Material.Slate, Parent = house })
		local flame = part({ Name = "Flame", Size = Vector3.new(0.4, 0.8, 0.4), CFrame = spot + Vector3.new(0, 0.7, 0),
			Color = Color3.fromRGB(255, 170, 40), Material = Enum.Material.Neon, Transparency = 1, CanCollide = false,
			Parent = diya })
		local light = Instance.new("PointLight")
		light.Color, light.Range, light.Brightness, light.Enabled = Color3.fromRGB(255, 170, 60), 12, 2, false
		light.Parent = flame
		local prompt = Instance.new("ProximityPrompt")
		prompt.ActionText, prompt.ObjectText = "Light diya", "1 oil"
		prompt.HoldDuration, prompt.MaxActivationDistance = 0.3, 10
		prompt.Parent = diya
		diya:SetAttribute("Lit", false)
		table.insert(diyas, diya)
	end
end

for i = 1, Config.presses do
	local a = (i / Config.presses + 1 / (Config.presses * 2)) * math.pi * 2
	local pos = Vector3.new(math.cos(a) * 34, 2, math.sin(a) * 34)
	local press = part({ Name = `OilPress{i}`, Shape = Enum.PartType.Cylinder, Size = Vector3.new(4, 5, 5),
		CFrame = CFrame.new(pos) * CFrame.Angles(0, 0, math.rad(90)), Color = Color3.fromRGB(120, 80, 30), Material = Enum.Material.Wood })
	local glow = Instance.new("PointLight")
	glow.Color, glow.Range, glow.Brightness = Color3.fromRGB(255, 220, 120), 10, 1
	glow.Parent = press
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText, prompt.ObjectText = "Fill oil jar", "Oil press"
	prompt.HoldDuration, prompt.MaxActivationDistance = 0.5, 10
	prompt.Parent = press
	prompt.Triggered:Connect(function(player)
		local p = data:Get(player)
		if not p then return end
		local cap = jarCapacity(player, p)
		oil[player] = math.min(cap, (oil[player] or 0) + Config.press.oil[p.pressTier])
		push(player)
	end)
end

---------------------------------------------------------------------- lighting, income, drops
local function setLit(diya: BasePart, lit: boolean, owner: Player?)
	diya:SetAttribute("Lit", lit)
	diya:SetAttribute("Owner", if owner then owner.UserId else 0)
	diya:SetAttribute("LitUntil", if lit then os.clock() + Config.burnSeconds else 0)
	local flame = diya:FindFirstChild("Flame") :: BasePart
	flame.Transparency = if lit then 0 else 1
	flame:FindFirstChildOfClass("PointLight").Enabled = lit
	diya:FindFirstChildOfClass("ProximityPrompt").Enabled = not lit
end

local function litShare(): number
	local n = 0
	for _, d in diyas do if d:GetAttribute("Lit") then n += 1 end end
	return n / #diyas
end

local rng = Random.new()
local function rollDrop(player: Player, p)
	-- rarest first, so one roll can only award the single best item it hits
	for i = #Config.items, 1, -1 do
		local item = Config.items[i]
		if rng:NextInteger(1, item.odds) == 1 then
			local first = (p.items[item.id] or 0) == 0
			p.items[item.id] = (p.items[item.id] or 0) + 1
			economy.bonus[player] = collectionBonus(p)
			Analytics.Progress(player, `Item_{item.id}`, p.items[item.id])
			if rarityRank(item.rarity) >= rarityRank(Config.announceFrom) then
				Banner:FireAllClients(`{player.DisplayName} found a {item.rarity} {item.name}! (1 in {item.odds})`, item.color)
			else
				Banner:FireClient(player, `You found a {item.name}!{if first then " New!" else ""}`, item.color)
			end
			return
		end
	end
end

local function light(player: Player, diya: BasePart)
	local p = data:Get(player)
	if not p or diya:GetAttribute("Lit") or (oil[player] or 0) < 1 then return end
	oil[player] -= 1
	setLit(diya, true, player)
	p.diyasLit += 1
	litSinceShow[player] = (litSinceShow[player] or 0) + 1
	local gained = economy:Add(player, Config.lightReward * Config.wick.mult[p.wickTier])
	Analytics.Earn(player, gained, p.coins, "Light")
	if not p.tutorialDone then
		p.tutorialDone = true
		Analytics.Funnel(player, "Onboarding", 3, "FirstDiya")
	end
	rollDrop(player, p)
	push(player)
end

for _, diya in diyas do
	diya:FindFirstChildOfClass("ProximityPrompt").Triggered:Connect(function(player) light(player, diya) end)
end

-- every second: pay owners of burning diyas, burn out old ones, check the fireworks goal, move the sun
local lastShow = -math.huge
local function fireworks()
	lastShow = os.clock()
	local show = Instance.new("Folder")
	show.Name = "Fireworks"
	show.Parent = workspace
	for i = 1, 12 do
		local a = rng:NextNumber(0, math.pi * 2)
		local burst = part({ Name = "Burst", Size = Vector3.new(1, 1, 1), Transparency = 1, CanCollide = false,
			Position = Vector3.new(math.cos(a) * rng:NextNumber(10, 60), rng:NextNumber(50, 90), math.sin(a) * rng:NextNumber(10, 60)),
			Parent = show })
		local pe = Instance.new("ParticleEmitter")
		local c = Config.items[(i - 1) % #Config.items + 1].color
		pe.Color = ColorSequence.new(c)
		pe.LightEmission, pe.Rate, pe.Speed, pe.Lifetime = 1, 0, NumberRange.new(20, 35), NumberRange.new(1.2, 2)
		pe.SpreadAngle = Vector2.new(180, 180)
		pe.Size = NumberSequence.new(1.2)
		pe.Parent = burst
		task.delay(i * 0.35, function() pe:Emit(200) end)
	end
	task.delay(10, function() show:Destroy() end)
	for _, player in Players:GetPlayers() do
		local p = data:Get(player)
		if p then
			local s = Config.sparklesBase + Config.sparklesPerDiyaLit * (litSinceShow[player] or 0)
			p.sparkles += s
			litSinceShow[player] = 0
			Banner:FireClient(player, `Fireworks! The village is lit. +{s} Sparkles`, Color3.fromRGB(255, 220, 120))
			push(player)
		end
	end
end

local clock = 0
task.spawn(function()
	while true do
		task.wait(1)
		local now = os.clock()
		local pay = {} :: { [number]: number }
		for _, d in diyas do
			if d:GetAttribute("Lit") then
				if now >= (d:GetAttribute("LitUntil") :: number) then
					setLit(d, false, nil)
				else
					local owner = d:GetAttribute("Owner") :: number
					pay[owner] = (pay[owner] or 0) + 1
				end
			end
		end
		for userId, n in pay do
			local player = Players:GetPlayerByUserId(userId)
			local p = player and data:Get(player)
			if p then economy:Add(player, n * Config.incomePerLitDiya * Config.wick.mult[p.wickTier]) end
		end
		local share = litShare()
		if share >= Config.fireworksAt and now - lastShow >= Config.fireworksCooldown then fireworks() end
		clock = (clock + 24 / Config.dayLengthSeconds) % 24
		Lighting.ClockTime = clock
		Village:FireAllClients(share)
		if math.floor(now) % 5 == 0 then
			for _, player in Players:GetPlayers() do push(player) end
		end
	end
end)

---------------------------------------------------------------------- players
local function applyTrail(player: Player)
	local p = data:Get(player)
	local char = player.Character
	local hrp = char and char:FindFirstChild("HumanoidRootPart")
	if not p or not hrp then return end
	local old = hrp:FindFirstChild("RangoliTrail")
	if old then old:Destroy() end
	for _, t in Config.trails do
		if t.id == p.trail then
			local a0, a1 = Instance.new("Attachment"), Instance.new("Attachment")
			a0.Name, a1.Name = "TrailTop", "TrailBottom"
			a0.Position, a1.Position = Vector3.new(0, 1, 0), Vector3.new(0, -1, 0)
			a0.Parent, a1.Parent = hrp, hrp
			local trail = Instance.new("Trail")
			trail.Name = "RangoliTrail"
			trail.Attachment0, trail.Attachment1 = a0, a1
			trail.Color = ColorSequence.new(t.colors[1], t.colors[2])
			trail.LightEmission, trail.Lifetime = 1, 0.8
			trail.Parent = hrp
		end
	end
end

local function applyTitle(player: Player)
	local p = data:Get(player)
	local char = player.Character
	local head = char and char:FindFirstChild("Head")
	if not p or not head then return end
	local old = head:FindFirstChild("Title")
	if old then old:Destroy() end
	local best = bestItem(p)
	local hasRare = best ~= nil and rarityRank(best.rarity) >= 2
	if not hasRare and not vip[player] then return end
	local bb = Instance.new("BillboardGui")
	bb.Name, bb.Size, bb.StudsOffset, bb.AlwaysOnTop = "Title", UDim2.new(0, 220, 0, 40), Vector3.new(0, 2.5, 0), false
	local t = Instance.new("TextLabel")
	t.Size, t.BackgroundTransparency, t.TextScaled, t.Font = UDim2.new(1, 0, 1, 0), 1, true, Enum.Font.GothamBlack
	t.Text = if hasRare then best.name else "VIP"
	t.TextColor3 = if hasRare then best.color else Color3.fromRGB(255, 215, 0)
	t.TextStrokeTransparency = 0.3
	t.Parent = bb
	bb.Parent = head
end

local function onCharacter(player: Player, char: Model)
	local hum = char:WaitForChild("Humanoid") :: Humanoid
	if vip[player] then hum.WalkSpeed = Config.vipSpeed end
	task.wait(0.5)
	applyTrail(player)
	applyTitle(player)
end

data.Loaded:Connect(function(player: Player, profile)
	Analytics.Funnel(player, "Onboarding", 1, "Joined")
	oil[player], litSinceShow[player] = 0, 0
	economy.bonus[player] = collectionBonus(profile)
	player.CharacterAdded:Connect(function(char) onCharacter(player, char) end)
	if player.Character then task.spawn(onCharacter, player, player.Character) end
	Analytics.Funnel(player, "Onboarding", 2, "Loaded")
	push(player)
end)

Players.PlayerRemoving:Connect(function(player)
	oil[player], litSinceShow[player], bigJar[player], vip[player] = nil, nil, nil, nil
	economy.passMultiplier[player], economy.bonus[player] = nil, nil
end)

---------------------------------------------------------------------- requests
local function upgrade(name: string, field: string, tiers)
	fn(name).OnServerInvoke = function(player)
		local p = data:Get(player)
		if not p then return false end
		local cost = tiers.cost[p[field] + 1]
		if not cost or not economy:Spend(player, cost) then return false end
		p[field] += 1
		Analytics.Spend(player, cost, p.coins, name)
		Analytics.Progress(player, name, p[field])
		push(player)
		return true
	end
end
upgrade("UpgradeJar", "jarTier", Config.jar)
upgrade("UpgradePress", "pressTier", Config.press)
upgrade("UpgradeWick", "wickTier", Config.wick)

fn("Rebirth").OnServerInvoke = function(player)
	local ok = economy:Rebirth(player, function(p)
		p.jarTier, p.pressTier, p.wickTier = 1, 1, 1 -- items, Sparkles and trails are kept
	end)
	if ok then
		oil[player] = 0
		local p = data:Get(player)
		Analytics.Progress(player, "Rebirth", p and p.rebirths or 0)
		Banner:FireClient(player, "Rebirth! +50% income forever", Color3.fromRGB(255, 215, 0))
		push(player)
	end
	return ok
end

fn("ClaimDaily").OnServerInvoke = function(player)
	local p = data:Get(player)
	if not p then return nil end
	local reward, streak = DailyReward.Claim(p, Config.daily)
	if reward then
		economy:Add(player, reward)
		Analytics.Earn(player, reward, p.coins, "Daily")
		Banner:FireClient(player, `{Config.dailyNames[math.min(streak, #Config.dailyNames)]} reward: +{reward} coins`, Color3.fromRGB(255, 180, 40))
	end
	push(player)
	return reward, streak
end

fn("BuyTrail").OnServerInvoke = function(player, id)
	local p = data:Get(player)
	if not p or type(id) ~= "string" then return false end
	for _, t in Config.trails do
		if t.id == id then
			if not p.trails[id] then
				if p.sparkles < t.cost then return false end
				p.sparkles -= t.cost
				p.trails[id] = true
			end
			p.trail = id
			applyTrail(player)
			push(player)
			return true
		end
	end
	return false
end

---------------------------------------------------------------------- purchases (switched off while ids are 0)
Monetization.Passes(data, {
	[Config.passes.doubleCoins] = function(player) economy.passMultiplier[player] = 2; push(player) end,
	[Config.passes.bigJar] = function(player) bigJar[player] = true; push(player) end,
	[Config.passes.vip] = function(player)
		vip[player] = true
		local hum = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
		if hum then hum.WalkSpeed = Config.vipSpeed end
		applyTitle(player)
	end,
})
Monetization.Products(data, {
	[Config.products.coinPack] = function(player, profile)
		local perSecond = Config.incomePerLitDiya * Config.wick.mult[profile.wickTier] * Config.jar.capacity[profile.jarTier]
		economy:Add(player, math.max(500, perSecond * Config.coinPackSeconds))
		push(player)
	end,
})
