-- 设置未读消息为已读
-- KEYS[1] 消息ID
-- 返回>0的数值表示删除成功，返回=0 表示删除失败

-- 从消息ID中分离用户ID
local user=''
for w in string.gmatch(KEYS[1], "tbMsg:(.*):") do
    user=w
end

local strKey    = 'tbMsg:'..user
local keyUNREAD = strKey..':UNREAD'
local keyREAD   = strKey..':READ'
local keyCount  = strKey..':COUNT'

-- 一定要先删除消息队列中的ID

local r   = redis.call("LREM",keyREAD,1,KEYS[1])  -- 删除已读队列
local ur = redis.call("LREM",keyUNREAD,1,KEYS[1]) -- 删除未读队列
local dr = redis.call("DEL",KEYS[1])              -- 删除消息体HASH

if dr == 1 then 
   redis.call("DECR",keyCount)                    -- 删除成功,Count-1
end
return r+ur+dr                                    -- 所有删除失败则返回0

--[[
测试用例： 
$ redis-cli -a jct2014redis --eval delMessage.lua tbMsg:xuehai@163.com:11
]]