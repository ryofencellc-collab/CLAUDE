--!strict
-- Daily login reward with a streak: claim once per UTC day; missing a day resets the streak to 1.
local DailyReward = {}

local function today(): number
	return math.floor(os.time() / 86400)
end

-- rewards[i] is the reward on streak day i; past the end the last value repeats.
function DailyReward.CanClaim(profile): boolean
	return (profile.lastClaimDay or -1) < today()
end

function DailyReward.Claim(profile, rewards: { number }): (number?, number)
	local d = today()
	if (profile.lastClaimDay or -1) >= d then
		return nil, profile.streak or 0
	end
	profile.streak = if profile.lastClaimDay == d - 1 then (profile.streak or 0) + 1 else 1
	profile.lastClaimDay = d
	local reward = rewards[math.min(profile.streak, #rewards)]
	return reward, profile.streak
end

return DailyReward
