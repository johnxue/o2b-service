from Framework import dbRedis
import datetime
import msgpack,ujson

class Message :
    
    def __init__(self) :
        self.rds=dbRedis.RedisCache()._connection
        self.redisSelect='redis.call("SELECT","10")'

    def send(self,toUser,messagePack,commit=True):
        '''
        #1.加入到数据库
        id=self.db.insert('tbUser',data,commit)
        if id<0 : raise BaseError(703) # SQL执行错误
        '''
        #校验数据
        if toUser is None or messagePack is None  \
           or toUser=='' or messagePack=='' or messagePack=={} : return 0
        
        # 详见sendMessage.lua
        luaScript = self.redisSelect+'''
            if #ARGV[1]==0 then
               return 0
            end
            
            local tab = {}
            local value=cjson.decode(ARGV[1])
            for k, v in pairs(value) do
              tab[#tab + 1] = k
              tab[#tab + 1] = v
            end
            
            local strKey='tbMsg:'..KEYS[1]
            local id=redis.call("INCR", strKey..':COUNT')
            local keyHM=strKey..':'..id
            redis.call("HMSET", keyHM,unpack(tab))
            
            local keyLS=strKey..':UNREAD'
            redis.call("lpush", keyLS,keyHM)
            
            return 1
        '''
        strNowTime=datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')
        messagePack['time']=strNowTime
        ls=self.rds.register_script(luaScript)
        r=ls(keys=[toUser],args=[ujson.dumps(messagePack)])
        return r
    
    # 探测新消息数量
    def sniffing(self,user):
        # 详见 sniffingMessage.lua
        luaScript = self.redisSelect+'''
            local strKey    = 'tbMsg:'..KEYS[1]
            local keyREAD   = strKey..':READ'
            local keyUNREAD = strKey..':UNREAD'

            local countREAD   = redis.call("LLEN", keyREAD)
            local countUNREAD = redis.call("LLEN", keyUNREAD)
            local tab={}
            tab['unread_count'] = countUNREAD
            tab['read_count']   = countREAD
            
            return cmsgpack.pack(tab)
        '''
        ls        = self.rds.register_script(luaScript)
        listMsgPack = ls(keys=[user])
        countInfo = msgpack.unpackb(listMsgPack,encoding='utf-8')
        return countInfo
    
    # 消息列表
    def getList(self,user,cat='UNREAD',offset=0,rowcount=-1) :
        offset=offset*rowcount
        # 详见getMsgList.lua
        luaScript=self.redisSelect+'''
            local offset   = ARGV[1]
            local rowcount = ARGV[2]
            
            local strKey = 'tbMsg:'..KEYS[1]
            local key    = strKey..':UNREAD'
            
            if KEYS[2]=='READ' then
               key=strKey..':READ'
            end
            
            local tab = {}
            
            local s='by *->level+time get # get *->time get *->from get *->name get *->title get *->level limit '..offset..' '..rowcount
            
            for w in string.gmatch(s, "[a-zA-Z0-9#*->]+") do
                tab[#tab+1]=w
            end
            
            local r=redis.call("SORT",key, unpack(tab))
            
            local rows={}
            for i=1,#r,6 do 
                local t={}
                t['id']    =  r[i]
                t['time']  = r[i+1]
                t['from']  = r[i+2]
                t['name']  = r[i+3]
                t['title'] = r[i+4]
                t['level'] = r[i+5]
                rows[#rows+1]=t
            end
            return cmsgpack.pack(rows)
        '''
        ls          = self.rds.register_script(luaScript)
        listMsgPack = ls(keys=[user,cat.upper()],args=[offset,rowcount])
        listInfo    = msgpack.unpackb(listMsgPack,encoding='utf-8')
        rows= {
            'msg_list_'+cat : listInfo
        }
        return rows
    
    def setRead():
        # 详见setMsgRead.lua
        luaScript=self.redisSelect+'''
            local strKey    = 'tbMsg:'..KEYS[1]
            local keyUNREAD = strKey..':UNREAD'
            local keyREAD   = strKey..':READ'
            
            local r_lrem=redis.call("LREM",keyUNREAD,1,ARGV[1])
            if r_lrem==1 then
               return redis.call("LPUSH",keyREAD,ARGV[1])
            end
            return r_lrem
        '''
        ls=self.rds.register_script(luaScript)
        return ls(keys=[user],args=[msgId])                
    
    def getMsg(self,mid):
        # 应判断用户权限
        # 详见getMsg.lua
        luaScript = self.redisSelect+'''
            local t={}
            
            local r=redis.call("HGETALL",KEYS[1])
            if r==nil then 
               return t
            end
            for i=1,#r,2 do 
                t[r[i]]=r[i+1]
            end
            
            local user=''
            for w in string.gmatch(KEYS[1], "tbMsg:(.*):") do
                user=w
            end
            
            local keyREAD   = 'tbMsg:'..user..':READ'
            local keyUNREAD = 'tbMsg:'..user..':UNREAD'
            
            local r_lrem=redis.call("LREM",keyUNREAD,1,KEYS[1])
            if r_lrem==1 then
               redis.call("LPUSH",keyREAD,KEYS[1])
            end
            return cmsgpack.pack(t)
        '''
        ls=self.rds.register_script(luaScript)
        msgInfo=msgpack.unpackb(ls(keys=[mid]),encoding='utf-8')
        return msgInfo
               
    def remove(self,mids):
        # 详见delMessage.lua
        luaScript=self.redisSelect+'''
            local count=0
            local ids=KEYS[1]..','
            local id,user,strKey,keyUNREAD,keyREAD,keyCount,r,ur,dr
            for w in string.gmatch(ids, "[%w@:._-]+,") do
                id=string.sub(w,1,-2)
            
                user=''
                for wt in string.gmatch(id, "tbMsg:(.*):") do
                    user=wt
                end
                
                strKey    = 'tbMsg:'..user
                keyUNREAD = strKey..':UNREAD'
                keyREAD   = strKey..':READ'
                keyCount  = strKey..':COUNT'
            
                r  = redis.call("LREM",keyREAD,1,id)
                ur = redis.call("LREM",keyUNREAD,1,id)
                dr = redis.call("DEL",id)
             
                if dr == 1 then 
                   redis.call("DECR",keyCount)
                   count=count+1
                end
            end
            return count
        '''
        ls=self.rds.register_script(luaScript)
        return ls(keys=[mids])               
