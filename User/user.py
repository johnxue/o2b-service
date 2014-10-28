from Framework import dbRedis

class userinfo :
    
    def __init__(self,db) :
        self.db=db
        self.rds=dbRedis.RedisCache()


    def add(self,data,commit=True):
        
        #1.加入到数据库
        id=self.db.insert('tbUser',data,commit)
        if id<0 : raise BaseError(703) # SQL执行错误
        
        #2.加入到Redis
        self.rds.save('tbUser',data,id=data['user'])
        return id
    
    def update(self,data,user,isCommit=True,isLock=True):
        #1.数据更新到数据库
        rw=self.db.updateByPk('tbUser',data,user,pk='user',commit=isCommit,lock=islock)      
        if id<0 : raise BaseError(705) # SQL执行错误

        #2.数据更新到Redis
        self.rds.save('tbUser',data,id=user)
        return rw
    
    def delete(self,data,id,isCommit=True,isLock=True):
        #1.数据更新到数据库
        rw=self.db.updateByPk('tbUser',
                         {'isDelete':'Y','updateTime':'{{now()}}'},
                         user,pk='user',commit=isCommit,lock=islock)      
        if id<0 : raise BaseError(705) # SQL执行错误

        #2.数据更新到Redis
        self.rds.delete('tbUser',data,id=user)
        return rw
    
    def get(self,user) :
        userinfo=self.rds.get('tbUser',user)
        return userinfo['result']
    
