--!nonstrict
-- Grow & Sell HUD: coins, multiplier, upgrade/expand/rebirth buttons, daily reward and a first-time hint.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local MarketplaceService = game:GetService("MarketplaceService")

local player = Players.LocalPlayer
local remotes = ReplicatedStorage:WaitForChild("Remotes")
local Config = require(ReplicatedStorage:WaitForChild("Shared").Config)

local gui = Instance.new("ScreenGui")
gui.Name = "HUD"
gui.ResetOnSpawn = false
gui.Parent = player:WaitForChild("PlayerGui")

local function label(text: string, pos: UDim2, size: UDim2): TextLabel
	local l = Instance.new("TextLabel")
	l.Text, l.Position, l.Size = text, pos, size
	l.BackgroundTransparency = 0.3
	l.BackgroundColor3 = Color3.fromRGB(20, 20, 20)
	l.TextColor3 = Color3.new(1, 1, 1)
	l.TextScaled = true
	l.Font = Enum.Font.GothamBold
	l.Parent = gui
	return l
end

local function button(text: string, y: number, onClick: () -> ()): TextButton
	local b = Instance.new("TextButton")
	b.Text = text
	b.Position = UDim2.new(0, 10, 0.35, y)
	b.Size = UDim2.new(0, 230, 0, 46)
	b.BackgroundColor3 = Color3.fromRGB(40, 140, 60)
	b.TextColor3 = Color3.new(1, 1, 1)
	b.TextScaled = true
	b.Font = Enum.Font.GothamBold
	b.Parent = gui
	b.MouseButton1Click:Connect(onClick)
	return b
end

local coins = label("Coins: 0", UDim2.new(0.5, -150, 0, 10), UDim2.new(0, 300, 0, 50))
local info = label("", UDim2.new(0.5, -150, 0, 64), UDim2.new(0, 300, 0, 30))
local hint = label("Walk to a crop and press E to harvest!", UDim2.new(0.5, -220, 0.8, 0), UDim2.new(0, 440, 0, 40))

local seedBtn = button("Upgrade seed", 0, function() remotes.UpgradeSeed:InvokeServer() end)
local tileBtn = button("Buy soil tile", 52, function() remotes.BuyTile:InvokeServer() end)
local rebirthBtn = button("Rebirth", 104, function() remotes.Rebirth:InvokeServer() end)
local dailyBtn = button("Claim daily reward", 156, function() remotes.ClaimDaily:InvokeServer() end)
if Config.passes.doubleCoins > 0 then
	button("2x Coins (pass)", 208, function() MarketplaceService:PromptGamePassPurchase(player, Config.passes.doubleCoins) end)
end

local function short(n: number): string
	if n >= 1e9 then return string.format("%.1fB", n / 1e9) end
	if n >= 1e6 then return string.format("%.1fM", n / 1e6) end
	if n >= 1e3 then return string.format("%.1fK", n / 1e3) end
	return tostring(math.floor(n))
end

remotes:WaitForChild("State").OnClientEvent:Connect(function(s)
	if not s then return end
	coins.Text = `Coins: {short(s.coins)}`
	info.Text = `{s.seed} · x{string.format("%.1f", s.multiplier)} · Rebirths {s.rebirths}`
	seedBtn.Text = if s.nextSeed then `{s.nextSeed}: {short(s.nextSeedCost)}` else "Best seed owned"
	tileBtn.Text = if s.tileCost then `New tile: {short(s.tileCost)}` else "Farm is full"
	rebirthBtn.Text = `Rebirth: {short(s.rebirthCost)} (+50%)`
	dailyBtn.Text = if s.canClaim then `Claim daily (day {s.streak + 1})` else `Streak: {s.streak} days`
	dailyBtn.BackgroundColor3 = if s.canClaim then Color3.fromRGB(230, 160, 20) else Color3.fromRGB(90, 90, 90)
	hint.Visible = not s.tutorialDone
end)
