--!strict
-- Thin wrapper over Roblox AnalyticsService: onboarding funnel, economy flows and progression, so every
-- factory game reports the same metrics (D1 retention and session length come from Roblox automatically).
local AnalyticsService = game:GetService("AnalyticsService")

local Analytics = {}

function Analytics.Funnel(player: Player, funnel: string, step: number, name: string)
	pcall(AnalyticsService.LogOnboardingFunnelStepEvent, AnalyticsService, player, step, name)
end

function Analytics.Earn(player: Player, amount: number, balance: number, source: string)
	pcall(AnalyticsService.LogEconomyEvent, AnalyticsService, player, Enum.AnalyticsEconomyFlowType.Source,
		"Coins", amount, balance, Enum.AnalyticsEconomyTransactionType.Gameplay.Name, source)
end

function Analytics.Spend(player: Player, amount: number, balance: number, sink: string)
	pcall(AnalyticsService.LogEconomyEvent, AnalyticsService, player, Enum.AnalyticsEconomyFlowType.Sink,
		"Coins", amount, balance, Enum.AnalyticsEconomyTransactionType.Shop.Name, sink)
end

function Analytics.Progress(player: Player, path: string, level: number)
	pcall(AnalyticsService.LogProgressionCompleteEvent, AnalyticsService, player, path, level)
end

return Analytics
