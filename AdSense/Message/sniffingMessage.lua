-- 得到用户的未读消息数量
-- KEYS[1] 用户ID
local strKey    = 'tbMsg:'..KEYS[1]
local keyREAD   = strKey..':READ'
local keyUNREAD = strKey..':UNREAD'

local countREAD   = redis.call("LLEN", keyREAD)
local countUNREAD = redis.call("LLEN", keyUNREAD)
local tab={}
tab['unread_count'] = countUNREAD
tab['read_count']   = countREAD
            
return cmsgpack.pack(tab)

--[[ 实验：
redis-cli -a jct2014redis --eval sniffingMessage.lua xuehai@163.com

]]
