--!strict
-- Player save data: one DataStore key per player, cached for the session, autosaved, saved on leave and shutdown.
local DataStoreService = game:GetService("DataStoreService")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local Data = {}
Data.__index = Data

local AUTOSAVE_SECONDS = 120
local RETRIES = 3

export type Profile = { [string]: any }

local function deepCopy(t: { [any]: any }): { [any]: any }
	local out = {}
	for k, v in t do
		out[k] = if type(v) == "table" then deepCopy(v) else v
	end
	return out
end

local function retry<T>(fn: () -> T): (boolean, T?)
	for attempt = 1, RETRIES do
		local ok, result = pcall(fn)
		if ok then
			return true, result
		end
		warn(`[Data] attempt {attempt} failed: {result}`)
		task.wait(2 ^ attempt)
	end
	return false, nil
end

-- defaults: the starting profile; missing keys in old saves are filled from it, so new fields are safe to add.
function Data.new(storeName: string, defaults: Profile)
	local self = setmetatable({}, Data)
	self.store = if RunService:IsStudio() and not game:GetService("ServerStorage"):GetAttribute("UseRealData")
		then nil -- Studio play-tests keep data in memory unless the attribute is set
		else DataStoreService:GetDataStore(storeName)
	self.defaults = defaults
	self.profiles = {} :: { [Player]: Profile }
	self.loaded = Instance.new("BindableEvent")
	self.Loaded = self.loaded.Event

	-- deferred so the game script can connect to Loaded before the first profile fires
	Players.PlayerAdded:Connect(function(p) task.defer(self._load, self, p) end)
	for _, p in Players:GetPlayers() do task.defer(self._load, self, p) end
	Players.PlayerRemoving:Connect(function(p) self:_save(p, true) end)
	game:BindToClose(function()
		for _, p in Players:GetPlayers() do task.spawn(self._save, self, p, true) end
		task.wait(3)
	end)
	task.spawn(function()
		while true do
			task.wait(AUTOSAVE_SECONDS)
			for p in self.profiles do task.spawn(self._save, self, p, false) end
		end
	end)
	return self
end

function Data:_load(player: Player)
	local saved = nil
	if self.store then
		local ok, value = retry(function() return self.store:GetAsync(`p_{player.UserId}`) end)
		if not ok then
			player:Kick("Could not load your save. Please rejoin.") -- never overwrite a save we failed to read
			return
		end
		saved = value
	end
	local profile = deepCopy(self.defaults)
	if type(saved) == "table" then
		for k, v in saved do profile[k] = v end
	end
	self.profiles[player] = profile
	self.loaded:Fire(player, profile)
end

function Data:_save(player: Player, release: boolean)
	local profile = self.profiles[player]
	if not profile then return end
	if self.store then
		retry(function() return self.store:SetAsync(`p_{player.UserId}`, profile) end)
	end
	if release then self.profiles[player] = nil end
end

function Data:Get(player: Player): Profile?
	return self.profiles[player]
end

return Data
