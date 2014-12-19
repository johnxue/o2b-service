from Framework import dbRedis,dbMysql
from Service import Random
import msgpack,ujson

class user(object) :
    
    def __init__(self) :
        self.rds=dbRedis.RedisCache()
        self.rds_conn=self.rds._connection
        
        #self.db =dbMysql.Mysql()
        self.SelectScript='redis.call("SELECT","12")'

    def saveToRedis(self,table,data,id='id') :
        luaScript = '''
            local tab = {}
            local id=KEYS[2]
            local table=KEYS[1]
            local key = table..':'..id
            --local id  = 1  -- 如果是修改记录，则返回的值为1
            
            local value=cjson.decode(ARGV[1])
            
            for k,v in pairs(value) do
                if  type(v)=='userdata'  then
                    v=''
                end
                tab[#tab + 1] = k
                tab[#tab + 1] = v
                if k=='nickname' then
                   local nickname=v
                end
            end
            
            redis.call("SELECT", KEYS[3])
            if redis.call("EXISTS", key) ~= 1 then
               -- 如果是新增记录，COUNT 计数器+1
               if KEYS[2]=='id' then 
                  id=redis.call("INCR", table..':AUTOID')
               end
               redis.call("INCR", table..':COUNT')
               -- 将id添加到list列表左侧
               redis.call("LPUSH", table..":LIST",id)
               key=table..':'..id
            end
            
            -- 新增或更改记录
            redis.call("HMSET", key,unpack(tab))
            redis.call("SADD",table..':NICKNAME_SADD',nickname)
            return id
        '''
        
        ls=self.rds._connection.register_script(luaScript)
        r=ls(keys=[table,id,config.TableToRedisNo[table]],args=[ujson.dumps(data)])
        return r

    def add(self,data,db,commit=True):
        #1.加入到数据库
        id=db.insert('tbUser',data,commit)
        if id<1 : raise BaseError(703) # SQL执行错误
        
        #2.加入到Redis
        rid=self.saveToRedis('tbUser',data,data['user'])
        if rid['result'] is None : raise BaseError(823) # redis 执行错误
        return id
    
    def update(self,data,user,db,isCommit=True,isLock=True):
        #1.数据更新到数据库
        rw=db.updateByPk('tbUser',data,user,pk='user',commit=isCommit,lock=islock)    
        
        if id<0 : raise BaseError(705) # SQL执行错误

        #2.数据更新到Redis
        self.rds.save('tbUser',data,id=user)
        return rw
    
    def delete(self,data,id,db,isCommit=True,isLock=True):
        #1.数据更新到数据库
        rw=db.updateByPk('tbUser',
                         {'isDelete':'Y','updateTime':'{{now()}}'},
                         user,pk='user',commit=isCommit,lock=islock) 
        if id<0 : raise BaseError(705) # SQL执行错误

        #2.数据更新到Redis
        self.rds.delete('tbUser',data,id=user)
        return rw
    
    def get(self,user) :
        userinfo=self.rds.get('tbUser',user)
        return userinfo['result']
    
    def tokenToGet(self,token) :
        luaScript=self.SelectScript+'''
            local user=redis.call("GET",KEYS[1])
            if not user then 
               return nil
            end
            
            local key = 'tbUser:'..user
            local r=redis.call("HGETALL",key)
            local t={}
            for i=1,#r,2 do 
                t[r[i]]=r[i+1]
            end
            return cmsgpack.pack(t)
        '''
        ls=self.rds_conn.register_script(luaScript)
        info=ls(keys=[token])
        if info is None :
            info=None
        else : 
            info=msgpack.unpackb(info,encoding='utf-8')
        return info

    def existsUsername(self,username) :
        luaScript=self.SelectScript+'''
            local key = 'tbUser:'..KEYS[1]
            local r=redis.call("EXISTS",key)
            return r
        '''
        ls=self.rds_conn.register_script(luaScript)
        r=ls(keys=[username])
        return r
    

    def existsNickname(self,nickname) :
        luaScript=self.SelectScript+'''
            local nickname = KEYS[1]
            local r=redis.call("SISMEMBER",'tbUser:NICKNAME_SADD',nickname)
            return r
        '''
        ls=self.rds_conn.register_script(luaScript)
        r=ls(keys=[nickname])
        return r
    