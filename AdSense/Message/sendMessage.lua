-- 给指定用户发消息
-- KEYS[1] 接收消息用户ID
-- ARGV[1] 消息内容
-- 消息体内容： '{"from":"来自用户","name":"用户昵称","msg":"消息内容","time":"时间串"}'

-- ARGV[2] 消息级别  U-用户级 S-系统级 H-紧急、重要的

if #ARGV[1]==0 then
   return 0
end

local tab = {}
local value=cjson.decode(ARGV[1])
for k, v in pairs(value) do
  tab[#tab + 1] = k
  tab[#tab + 1] = v
end

-- 添加到消息库
local strKey='tbMsg:'..KEYS[1]
local id=redis.call("INCR", strKey..':COUNT')
local keyHM=strKey..':'..id
redis.call("HMSET", keyHM,unpack(tab))

-- 添加到消息队列
local keyLS=strKey..':UNREAD'
redis.call("rpush", keyLS,keyHM)

return 1

-- 测试数据：
-- redis-cli -a jct2014redis --eval sendmsg.lua xuehai@163.com , '{"from":"test@163.com","name":"test","msg":"I like Linux","time":"2014.10.28 11:44:00"}'
