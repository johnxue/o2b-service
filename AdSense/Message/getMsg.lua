-- 根据消息ID得到消息具体内容 
-- KEYS[1] 消息ID

redis.call("SELECT",'10')

-- 得到消息体
local r=redis.call("HGETALL",KEYS[1])
if r==nil then 
   return t
end

local t={}
for i=1,#r,2 do 
    t[r[i]]=r[i+1]
end

-- 得到用户id
local user=''
for w in string.gmatch(KEYS[1], "tbMsg:(.*):") do
    user=w
end

-- 得到用户的消息队列
local keyREAD   = 'tbMsg:'..user..':READ'
local keyUNREAD = 'tbMsg:'..user..':UNREAD'

-- 从未读队列中删除消息id
local r_lrem=redis.call("LREM",keyUNREAD,1,KEYS[1])
if r_lrem==1 then
   -- 将从未读队列中删除的消息id压入已读消息队列
   redis.call("LPUSH",keyREAD,KEYS[1])
end

-- 返回消息体
return cmsgpack.pack(t)