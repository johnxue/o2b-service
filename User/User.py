import Framework.dbRedis

class userinfo :
    
    def __init__(db,rdb) :
        self.db=db
        self.rdb=rdb

    def add(self,data,commit=True):
        
        #1.加入到数据库
        id=self.db.insert('tbUser',data,commit)
        if id<0 : raise BaseError(703) # SQL执行错误
        
        #2.加入到Redis
        key='tbUser:'+data['user']
        del data['user']
        self.rdb.save(key,data)
        return id
    
    def update(self,data,ids,isCommit=True,isLock=True):
        #1.数据更新到数据库
        rw=db.updateByPk('tbUser',data,'{{ in (%s)}}'%(ids),pk='user',commit=isCommit,lock=islock)      
        if id<0 : raise BaseError(705) # SQL执行错误

        #2.数据更新到Redis
        key='tbUser:'
        self.rdb.update(key,data,ids,pk='user')
        return rw
    
    def delete(self,data,ids,isCommit=True,isLock=True):
        #1.数据更新到数据库
        rw=db.updateByPk('tbUser',
                         {'isDelete':'Y','updateTime':'{{now()}}'},
                         '{{ in (%s)}}'%(ids),pk='user',commit=isCommit,lock=islock)      
        if id<0 : raise BaseError(705) # SQL执行错误

        #2.数据更新到Redis
        key='tbUser:'
        self.rdb.delete(key,data,ids,pk='user')
        return rw
    
    def get(self,user) :
        return self.rdb.find('tbUser:'+user)
    
    def 
    