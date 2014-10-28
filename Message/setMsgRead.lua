-- 设置未读消息为已读
-- KEYS[1] 用户ID
-- ARGV[1] 消息ID
-- 返回>0的数值表示为已读队列消息数量，返回=0 表示设置失败
local strKey            = 'tbMsg:'..KEYS[1]
local keyUNREAD   = strKey..':UNREAD'
local keyREAD        = strKey..':READ'

local r_lrem=redis.call("LREM",keyUNREAD,1,ARGV[1])
if r_lrem==1 then
   return redis.call("LPUSH",keyREAD,ARGV[1])
end
return r_lrem
