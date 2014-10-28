-- 得到用户的消息内容
-- KEYS[1] 用户ID
-- KEYS[2] 消息队列类型，UNREAD-代表新未读消息  READ-代表已读消息
-- ARGV[1],ARGV[2]对应分页的 limit offset ,rowcount
local offset       = ARGV[1]
local rowcount = ARGV[2]
offset=offset*rowcount

local strKey = 'tbMsg:'..KEYS[1]
local key      = strKey..':UNREAD'

if KEYS[2]=='READ' then
   key=strKey..':READ'
end

local tab = {}

-- local by       = 'by not-exists-key'
local s='by *->level+time get # get *->time get *->from get *->name get *->title get *->level limit '..offset..' '..rowcount

for w in string.gmatch(s, "[a-zA-Z0-9#*->]+") do
    tab[#tab+1]=w
end

local r=redis.call("SORT",key, unpack(tab))

local rows={}
for i=1,#r,6 do 
    local t={}
    t['id']      =  r[i]
    t['time']  = r[i+1]
    t['from']  = r[i+2]
    t['name'] = r[i+3]
    t['title']   = r[i+4]
    t['level']  = r[i+5]
    rows[#rows+1]=t
end

return cmsgpack.pack(rows)


--return cjson.encode(rows)

--[[
return cjson.encode(rows)
-- 不排序
sort tbMsg:xuehai@163.com:UNREAD by not-exists-key get # get *->time limit 0 5
-- 已读需要以时间排序
sort tbMsg:xuehai@163.com:READ get # get *->time get *->msg get *->fromUser

-- 测试数据：
redis-cli -a jct2014redis --eval getList.lua xuehai@163.com UNREAD , 0 100
]]
