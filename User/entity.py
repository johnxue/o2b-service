from Framework import dbRedis,dbMysql
from Service import Random
import msgpack,ujson

class user(object) :
    
    def __init__(self) :
        self.rds=dbRedis.RedisCache()
        self.rds_conn=self.rds._connection
        
        #self.db =dbMysql.Mysql()
        self.SelectScript='redis.call("SELECT","12")'

    def add(self,data,db,commit=True):
        #1.加入到数据库
        id=db.insert('tbUser',data,commit)
        if id<1 : raise BaseError(703) # SQL执行错误
        
        #2.加入到Redis
        rid=self.rds.save('tbUser',data,data['user'])
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

    def exists(self,username) :
        luaScript=self.SelectScript+'''
            local key = 'tbUser:'..KEYS[1]
            local r=redis.call("EXISTS",key)
            return r
        '''
        ls=self.rds_conn.register_script(luaScript)
        r=ls(keys=[username])
        return r
    

    