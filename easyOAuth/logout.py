import tornado.web
from dbMysql import dbMysql
import config
import json
from easyOAuth.userinfo import Token

# 
class Handler(tornado.web.RequestHandler):
    
    def gotoErrorPage(self,error_code) :
        self.set_header('Access-Control-Allow-Origin','*')
        self.redirect('/o2b/v1.0.0/error/%d'% error_code )
        
    def checkAppKey(self):
        if self.request.headers.get('app-key')!=config.App_Key :
            r = False
        else :
            r = True
        return r
        
        
    def tokenToUser(self):
        token=self.request.headers.get('Authorization')
        if token is not None  :
            myToken=Token(config.redisConfig)
            try :
                user=myToken.getUser(token).decode('utf-8')
            except:
                user=None
        else :
            user=None
        return user
    
    def delUserToken(self):
        token=self.request.headers.get('Authorization')
        if token is not None  :
            try :
                myToken=Token(config.redisConfig)
                s=myToken.delUser(token) # 成功删除应返回成功受影响的记录数
            except:
                s=0
        else :
            s=None
        return s
    

    def options(self,id=''):
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,PATCH')
        self.set_header('Access-Control-Allow-Headers', 'app-key,authorization,Content-type')
      

    def delete(self):  # 用户logout

        if not self.checkAppKey() :
            # 601 : 未经授权的第三方应用
            self.gotoErrorPage(601)
            return
        
        token=self.request.headers.get('Authorization')
        user=self.tokenToUser()
        if user is None :
            # 602 : 未经登录授权的应用
            self.gotoErrorPage(602)
            return        

        r=self.delUserToken()
        
        if r>0:
            strLogs='User:%s Token:%s [ Redisk 删除成功,r.delte()=%d ]' % (user,token,r)
        else :
            strLogs='User:%s Token:%s [ Redisk 删除失败,r.delete()=%d ]' % (user,token,r)

        try :
            db=dbMysql(config.dbConfig)
        except :
            # 701 : 数据库连接失败
            self.gotoErrorPage(701)
            return
        
        #1. 查询产品属性
        try :

            db.begin()
            
            #2.1 更新 tbUser 表的用户最后一次登出时间 
            sqlSelect="Select user from tbUser where user='%s' for update" % (user)
            db.query(sqlSelect)
            
            sqlUpdate ="Update tbUser set lastLogout=now() where user='%s'" % (user)
            db.update(sqlUpdate)                    
            
            #2.2 插入 tbLogs 日志库；
            sqlInsert = (
              "INSERT INTO tbLogs(user,level,content,createTime) "
              "VALUES (%s, %s, %s, now())"
            )
            
            strLogs+=' Logout 操作完成.'
            addressId=db.save(sqlInsert,(user,'USE',strLogs))
            
            db.commit()
            
        except :
            db.rollback()
            # 702 : SQL执行失败
            self.gotoErrorPage(702)
            return
        
        #3. 返回
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Expose-Headers','Authorization')
        self.set_header('Authorization', '')     
        # 下面需要观察，有无Header的返回
        self.set_status(204)  # 204 操作成功，无返回
        return

 