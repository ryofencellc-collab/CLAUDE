--!strict
-- Game passes (permanent perks) and developer products (repeatable purchases), following Roblox's rules:
-- prices shown before purchase, no paid random items, receipts granted exactly once.
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")

local Monetization = {}

export type Products = { [number]: (player: Player, profile: any) -> () }

-- passes: { [passId] = onOwned(player) }, checked on join and after an in-game purchase.
function Monetization.Passes(data, passes: { [number]: (player: Player) -> () })
	local function check(player: Player)
		for id, grant in passes do
			if id <= 0 then continue end -- placeholder ids until the passes exist on Roblox
			local ok, owns = pcall(MarketplaceService.UserOwnsGamePassAsync, MarketplaceService, player.UserId, id)
			if ok and owns then grant(player) end
		end
	end
	data.Loaded:Connect(function(player) check(player) end)
	MarketplaceService.PromptGamePassPurchaseFinished:Connect(function(player, id, bought)
		if bought and passes[id] then passes[id](player) end
	end)
end

-- products: { [productId] = grant(player, profile) }. Receipt ids are remembered in the profile so a retried
-- receipt is never granted twice.
function Monetization.Products(data, products: Products)
	MarketplaceService.ProcessReceipt = function(receipt)
		local player = Players:GetPlayerByUserId(receipt.PlayerId)
		local profile = player and data:Get(player)
		if not profile then
			return Enum.ProductPurchaseDecision.NotProcessedYet
		end
		profile.receipts = profile.receipts or {}
		if profile.receipts[receipt.PurchaseId] then
			return Enum.ProductPurchaseDecision.PurchaseGranted
		end
		local grant = products[receipt.ProductId]
		if not grant then
			return Enum.ProductPurchaseDecision.NotProcessedYet
		end
		local ok, err = pcall(grant, player :: Player, profile)
		if not ok then
			warn(`[Monetization] grant failed: {err}`)
			return Enum.ProductPurchaseDecision.NotProcessedYet
		end
		profile.receipts[receipt.PurchaseId] = true
		return Enum.ProductPurchaseDecision.PurchaseGranted
	end
end

return Monetization
