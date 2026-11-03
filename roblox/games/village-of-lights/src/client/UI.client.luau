--!nonstrict
-- Village of Lights HUD: coins, Sparkles, oil jar, village progress bar, upgrade/rebirth/daily buttons,
-- a Collection panel that shows every item's exact odds, a Trails shop, announcement banners and a tutorial.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local MarketplaceService = game:GetService("MarketplaceService")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local remotes = ReplicatedStorage:WaitForChild("Remotes")
local Config = require(ReplicatedStorage:WaitForChild("Shared").Config)

local gui = Instance.new("ScreenGui")
gui.Name, gui.ResetOnSpawn, gui.IgnoreGuiInset = "HUD", false, false
gui.Parent = player:WaitForChild("PlayerGui")

local GOLD, DARK = Color3.fromRGB(255, 190, 60), Color3.fromRGB(30, 18, 40)

local function corner(inst: Instance, r: number?)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0, r or 10)
	c.Parent = inst
end

local function label(parent: Instance, text: string, pos: UDim2, size: UDim2, color: Color3?): TextLabel
	local l = Instance.new("TextLabel")
	l.Text, l.Position, l.Size = text, pos, size
	l.BackgroundColor3, l.BackgroundTransparency = DARK, 0.25
	l.TextColor3, l.TextScaled, l.Font = color or Color3.new(1, 1, 1), true, Enum.Font.GothamBold
	l.Parent = parent
	corner(l)
	return l
end

local function button(parent: Instance, text: string, pos: UDim2, size: UDim2, color: Color3, onClick: () -> ()): TextButton
	local b = Instance.new("TextButton")
	b.Text, b.Position, b.Size, b.BackgroundColor3 = text, pos, size, color
	b.TextColor3, b.TextScaled, b.Font, b.AutoButtonColor = Color3.new(1, 1, 1), true, Enum.Font.GothamBold, true
	b.Parent = parent
	corner(b)
	b.MouseButton1Click:Connect(onClick)
	return b
end

local function short(n: number): string
	for _, u in { { 1e12, "T" }, { 1e9, "B" }, { 1e6, "M" }, { 1e3, "K" } } do
		if n >= u[1] then return string.format("%.1f%s", n / u[1], u[2]) end
	end
	return tostring(math.floor(n))
end

---------------------------------------------------------------------- top bar
local coins = label(gui, "0", UDim2.new(0.5, -230, 0, 8), UDim2.new(0, 220, 0, 44), GOLD)
local sparkles = label(gui, "0", UDim2.new(0.5, 10, 0, 8), UDim2.new(0, 220, 0, 44), Color3.fromRGB(255, 230, 160))
local oilLbl = label(gui, "Oil 0/3", UDim2.new(0.5, -110, 0, 56), UDim2.new(0, 220, 0, 32))
local barBack = Instance.new("Frame")
barBack.Position, barBack.Size, barBack.BackgroundColor3 = UDim2.new(0.5, -200, 0, 94), UDim2.new(0, 400, 0, 22), DARK
barBack.Parent = gui
corner(barBack, 8)
local bar = Instance.new("Frame")
bar.Size, bar.BackgroundColor3 = UDim2.new(0, 0, 1, 0), GOLD
bar.Parent = barBack
corner(bar, 8)
local barText = Instance.new("TextLabel")
barText.Size, barText.BackgroundTransparency, barText.TextScaled, barText.Font = UDim2.new(1, 0, 1, 0), 1, true, Enum.Font.GothamBold
barText.TextColor3, barText.ZIndex = Color3.new(1, 1, 1), 2
barText.Parent = barBack

---------------------------------------------------------------------- left buttons
local left = Instance.new("Frame")
left.Position, left.Size, left.BackgroundTransparency = UDim2.new(0, 10, 0.25, 0), UDim2.new(0, 240, 0, 420), 1
left.Parent = gui
local list = Instance.new("UIListLayout")
list.Padding = UDim.new(0, 6)
list.Parent = left
local function leftButton(text: string, color: Color3, onClick): TextButton
	return button(left, text, UDim2.new(), UDim2.new(1, 0, 0, 44), color, onClick)
end
local jarBtn = leftButton("Bigger jar", Color3.fromRGB(180, 90, 30), function() remotes.UpgradeJar:InvokeServer() end)
local pressBtn = leftButton("Faster press", Color3.fromRGB(150, 100, 30), function() remotes.UpgradePress:InvokeServer() end)
local wickBtn = leftButton("Brighter wick", Color3.fromRGB(200, 140, 20), function() remotes.UpgradeWick:InvokeServer() end)
local rebirthBtn = leftButton("Rebirth", Color3.fromRGB(140, 60, 180), function() remotes.Rebirth:InvokeServer() end)
local dailyBtn = leftButton("Daily reward", Color3.fromRGB(230, 120, 30), function() remotes.ClaimDaily:InvokeServer() end)

---------------------------------------------------------------------- panels
local function panel(title: string): Frame
	local f = Instance.new("Frame")
	f.Position, f.Size, f.BackgroundColor3, f.Visible = UDim2.new(0.5, -220, 0.5, -200), UDim2.new(0, 440, 0, 400), DARK, false
	f.Parent = gui
	corner(f, 14)
	label(f, title, UDim2.new(0, 10, 0, 8), UDim2.new(1, -70, 0, 40), GOLD).BackgroundTransparency = 1
	button(f, "X", UDim2.new(1, -50, 0, 8), UDim2.new(0, 40, 0, 40), Color3.fromRGB(170, 40, 40), function() f.Visible = false end)
	local body = Instance.new("Frame")
	body.Name, body.Position, body.Size, body.BackgroundTransparency = "Body", UDim2.new(0, 10, 0, 56), UDim2.new(1, -20, 1, -66), 1
	body.Parent = f
	local l = Instance.new("UIListLayout")
	l.Padding = UDim.new(0, 6)
	l.Parent = body
	return f
end

local collection = panel("Collection (free drops from lighting diyas)")
local itemRows = {}
for _, item in Config.items do
	local row = label(collection.Body, "", UDim2.new(), UDim2.new(1, 0, 0, 52), item.color)
	itemRows[item.id] = row
end
label(collection.Body, "Exact odds per diya lit. Nothing you can buy changes them.", UDim2.new(), UDim2.new(1, 0, 0, 30)).TextColor3 =
	Color3.fromRGB(200, 200, 200)

local trailsPanel = panel("Rangoli Trails (Sparkles)")
local trailButtons = {}
for _, t in Config.trails do
	trailButtons[t.id] = button(trailsPanel.Body, t.name, UDim2.new(), UDim2.new(1, 0, 0, 52), t.colors[1], function()
		remotes.BuyTrail:InvokeServer(t.id)
	end)
end

leftButton("Collection", Color3.fromRGB(60, 120, 200), function() collection.Visible = not collection.Visible end)
leftButton("Trails", Color3.fromRGB(220, 70, 140), function() trailsPanel.Visible = not trailsPanel.Visible end)
if Config.passes.doubleCoins > 0 then
	leftButton("2x Coins", Color3.fromRGB(40, 160, 60), function() MarketplaceService:PromptGamePassPurchase(player, Config.passes.doubleCoins) end)
end
if Config.passes.bigJar > 0 then
	leftButton("Double Jar", Color3.fromRGB(40, 140, 120), function() MarketplaceService:PromptGamePassPurchase(player, Config.passes.bigJar) end)
end

---------------------------------------------------------------------- banners and tutorial
local banner = label(gui, "", UDim2.new(0.5, -300, 0.18, 0), UDim2.new(0, 600, 0, 54))
banner.Visible = false
local bannerToken = 0
remotes:WaitForChild("Banner").OnClientEvent:Connect(function(text: string, color: Color3)
	bannerToken += 1
	local mine = bannerToken
	banner.Text, banner.TextColor3, banner.Visible = text, color or Color3.new(1, 1, 1), true
	banner.Size = UDim2.new(0, 540, 0, 48)
	TweenService:Create(banner, TweenInfo.new(0.25, Enum.EasingStyle.Back), { Size = UDim2.new(0, 600, 0, 54) }):Play()
	task.delay(4, function() if bannerToken == mine then banner.Visible = false end end)
end)

local tutorial = label(gui, "Fill your oil jar at a glowing press, then light the diyas in front of the houses!",
	UDim2.new(0.5, -300, 0.82, 0), UDim2.new(0, 600, 0, 46), GOLD)

---------------------------------------------------------------------- state
remotes:WaitForChild("Village").OnClientEvent:Connect(function(share: number)
	bar.Size = UDim2.new(math.clamp(share / Config.fireworksAt, 0, 1), 0, 1, 0)
	barText.Text = `Village lit {math.floor(share * 100)}% · fireworks at {math.floor(Config.fireworksAt * 100)}%`
end)

remotes:WaitForChild("State").OnClientEvent:Connect(function(s)
	if not s then return end
	coins.Text = `Coins {short(s.coins)}  x{string.format("%.1f", s.multiplier)}`
	sparkles.Text = `Sparkles {short(s.sparkles)}`
	oilLbl.Text = `Oil {s.oil}/{s.capacity}`
	jarBtn.Text = if s.jarCost then `Bigger jar: {short(s.jarCost)}` else "Jar maxed"
	pressBtn.Text = if s.pressCost then `Faster press: {short(s.pressCost)}` else "Press maxed"
	wickBtn.Text = if s.wickCost then `Brighter wick: {short(s.wickCost)}` else "Wick maxed"
	rebirthBtn.Text = `Rebirth: {short(s.rebirthCost)} (+50%)`
	local day = Config.dailyNames[math.min(s.streak + 1, #Config.dailyNames)]
	dailyBtn.Text = if s.canClaim then `Claim: {day}` else `Streak {s.streak} days`
	dailyBtn.BackgroundColor3 = if s.canClaim then Color3.fromRGB(230, 120, 30) else Color3.fromRGB(80, 80, 80)
	for _, item in Config.items do
		local n = s.items[item.id] or 0
		itemRows[item.id].Text = `{item.rarity}: {item.name}  1 in {short(item.odds)}  ·  owned {n}  ·  +{math.floor(item.bonus * 100)}% income`
	end
	for _, t in Config.trails do
		local b = trailButtons[t.id]
		b.Text = if s.trail == t.id then `{t.name} (equipped)` elseif s.trails[t.id] then `Equip {t.name}` else `{t.name}: {t.cost} Sparkles`
	end
	tutorial.Visible = not s.tutorialDone
end)
