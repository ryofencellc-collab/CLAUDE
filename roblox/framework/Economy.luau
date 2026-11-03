--!strict
-- Coins and rebirths: leaderstats, multipliers (rebirths, 2x pass), and the rebirth cost curve.
local Economy = {}
Economy.__index = Economy

function Economy.new(data, config: { rebirthBase: number, rebirthGrowth: number, rebirthBonus: number })
	local self = setmetatable({}, Economy)
	self.data = data
	self.config = config
	self.passMultiplier = {} :: { [Player]: number }
	data.Loaded:Connect(function(player: Player, profile)
		local stats = Instance.new("Folder")
		stats.Name = "leaderstats"
		local coins = Instance.new("IntValue")
		coins.Name = "Coins"
		coins.Value = profile.coins
		coins.Parent = stats
		local reb = Instance.new("IntValue")
		reb.Name = "Rebirths"
		reb.Value = profile.rebirths
		reb.Parent = stats
		stats.Parent = player
	end)
	return self
end

function Economy:_sync(player: Player, profile)
	local stats = player:FindFirstChild("leaderstats")
	if stats then
		(stats :: any).Coins.Value = math.floor(profile.coins);
		(stats :: any).Rebirths.Value = profile.rebirths
	end
end

function Economy:Multiplier(player: Player): number
	local profile = self.data:Get(player)
	if not profile then return 1 end
	return (1 + self.config.rebirthBonus * profile.rebirths) * (self.passMultiplier[player] or 1)
end

-- amount is the base reward; multipliers apply here so every source of income gets them.
function Economy:Add(player: Player, amount: number): number
	local profile = self.data:Get(player)
	if not profile then return 0 end
	local gained = math.floor(amount * self:Multiplier(player))
	profile.coins += gained
	profile.lifetimeCoins = (profile.lifetimeCoins or 0) + gained
	self:_sync(player, profile)
	return gained
end

function Economy:Spend(player: Player, cost: number): boolean
	local profile = self.data:Get(player)
	if not profile or profile.coins < cost then return false end
	profile.coins -= cost
	self:_sync(player, profile)
	return true
end

function Economy:RebirthCost(player: Player): number
	local profile = self.data:Get(player)
	local n = if profile then profile.rebirths else 0
	return math.floor(self.config.rebirthBase * self.config.rebirthGrowth ^ n)
end

-- Resets coins and the game's own progress fields (reset callback); rebirth count raises every future multiplier.
function Economy:Rebirth(player: Player, reset: (profile: any) -> ()): boolean
	local profile = self.data:Get(player)
	if not profile then return false end
	local cost = self:RebirthCost(player)
	if profile.coins < cost then return false end
	profile.coins = 0
	profile.rebirths += 1
	reset(profile)
	self:_sync(player, profile)
	return true
end

return Economy
