import tornado.web
import config
import redis

class Token(tornado.web.RequestHandler):
    
    def __init__(self,config):
        # 未处理redis初始化失败异常
        self.r=redis.Redis(**config)
        self.pr=r.pipeline()
        
    def saveToRedis(self,token,uid,timeout=1800) :
        self.pr.set(token,uid)
        self.pr.expire(token,timeout)
        self.execute()
        
    def getUser(self,token) :
        return self.r.get(token)

    def delUser(self,token) :
        return self.r.delete(token)
