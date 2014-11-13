from Framework import dbRedis,dbMysql
import msgpack,ujson

class user(object) :
    
    def __init__(self) :
        self.rcon=dbRedis.RedisCache()._connection
        #self.db =dbMysql.Mysql()
        self.SelectScript='redis.call("SELECT","12")'

    def add(self,data,commit=True):
        #1.加入到数据库
        db =dbMysql.Mysql()
        id=db.insert('tbUser',data,commit)
        db.close()
        if id<1 : raise BaseError(703) # SQL执行错误
        
        #2.加入到Redis
        rid=self.rds.save('tbUser',data,id=data['user'])
        if rid['result']<1 : raise BaseError(823) # redis 执行错误
        return id
    
    def update(self,data,user,isCommit=True,isLock=True):
        #1.数据更新到数据库
        db =dbMysql.Mysql()
        rw=db.updateByPk('tbUser',data,user,pk='user',commit=isCommit,lock=islock)    
        db.close()
        
        if id<0 : raise BaseError(705) # SQL执行错误

        #2.数据更新到Redis
        self.rds.save('tbUser',data,id=user)
        return rw
    
    def delete(self,data,id,isCommit=True,isLock=True):
        #1.数据更新到数据库
        db =dbMysql.Mysql()
        rw=db.updateByPk('tbUser',
                         {'isDelete':'Y','updateTime':'{{now()}}'},
                         user,pk='user',commit=isCommit,lock=islock) 
        db.close()
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
        ls=self.rcon.register_script(luaScript)
        info=ls(keys=[token])
        if info is None :
            info=None
        else : 
            info=msgpack.unpackb(info,encoding='utf-8')
        return info