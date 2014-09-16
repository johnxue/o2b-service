import tornado.web
import config
import redis

class Token(tornado.web.RequestHandler):
    
    def __init__(self,config):
        self.r=redis.Redis(**config)
        self.pr=self.r.pipeline()
        
    def saveToRedis(self,token,uid,timeout=36000) :
        self.pr.set(token,uid)
        self.pr.expire(token,timeout)
        self.pr.execute()
        
    def getUser(self,token) :
        return self.r.get(token)

    def delUser(self,token) :
        return self.r.delete(token)