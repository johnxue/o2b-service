import tornado.web
from dbMysql import dbMysql
import config
import json
from easyOAuth.userinfo import Token

# 关注    
class hFollow(tornado.web.RequestHandler):
    
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
    
        
    def options(self,pcode):
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,PATCH')
        self.set_header('Access-Control-Allow-Headers', 'app-key,authorization')
        
        
    # 加关注
    def post(self,code):
        if not self.checkAppKey() :
            # 601 : 未经授权的第三方应用
            self.gotoErrorPage(601)
            return
        
        user=self.tokenToUser()

        if user is None :
            # 602 : 未经登录授权的应用
            self.gotoErrorPage(602)
            return

        
        try :
            db=dbMysql(config.dbConfig)
        except :
            # 701 : 数据库连接失败
            self.gotoErrorPage(701)
            return
        
        #1. 查询产品属性
        try :
            
            db.begin()
            
            #1.1 插入到关注库 tbProductFollower；
            
            sqlInsert = (
              "INSERT INTO tbProductFollower(user, pcode,followtime) "
              "VALUES (%s, %s,null)"
            )            
            if db.save(sqlInsert,(user,code))<0 :
                raise Exception('SQL 语句执行失败 !')
            
            #1.2 更改tbUser.totalFollow+1
            sqlSelect="select totalFollow from tbUser where user='%s' for update" % (user)
            db.query(sqlSelect)
            
            sqlUpdate="Update tbUser set totalFollow=totalFollow+1 where user='%s'" % (user)
            db.update(sqlUpdate)
            
            #1.3 更改tbProdcutList.totalFollow+1
            sqlSelect="Select totalFollow from tbProductList where code='%s' for update" % (code)
            db.query(sqlSelect)
            sqlUpdate="Update tbProductList set totalFollow=totalFollow+1 where code='%s'" % (code)
            db.update(sqlUpdate)            
            #if db.update(sqlUpdate) is None :
            #    raise Exception('SQL 语句执行失败 !')

            db.commit()
            
            # 返回最后的关注数
            sqlSelect="select code,totalFollow from tbProductList where code='%s'" % (code)
            row_object=db.getToObject(sqlSelect)

        except :
            db.rollback()
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        #3. 打包成json object

        self.set_header('Access-Control-Allow-Origin','*')
        self.set_status(201)  # 201 创建对象成功
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(row_object,ensure_ascii=False))
        
        return
    
    # 取消关注
    def delete(self,code):

        if not self.checkAppKey() :
            # 601 : 未经授权的第三方应用
            self.gotoErrorPage(601)
            return
        
        user=self.tokenToUser()

        if user is None :
            # 602 : 未经登录授权的应用
            self.gotoErrorPage(602)
            return
        
        try :
            db=dbMysql(config.dbConfig)
        except :
            # 701 : 数据库连接失败
            self.gotoErrorPage(701)
            return
        
        #1. 查询产品属性
        try :
            db.begin()
            
            #1.1 从关注库删除 tbProductFollower；
            sqlDelete = "Delete From tbProductFollower Where user=%s and pcode=%s"
            db.delete(sqlDelete,(user,code))
            
            #1.2 更改tbUser.totalFollow-1
            sqlSelect="select totalFollow from tbUser where user='%s' for update" % (user)
            db.query(sqlSelect)
            
            sqlUpdate="Update tbUser set totalFollow=totalFollow-1 where user='%s' and totalFollow>0" % (user)
            db.update(sqlUpdate)
            
            #1.3 更改tbProdcutList.totalFollow-1
            sqlSelect="Select totalFollow from tbProductList where code='%s' for update" % (code)
            db.query(sqlSelect)
            sqlUpdate="Update tbProductList set totalFollow=totalFollow-1 where code='%s' and totalFollow>0" % (code)
            db.update(sqlUpdate)            
            #if db.update(sqlUpdate) is None :
            #    raise Exception('SQL 语句执行失败 !')

            db.commit()
            
            # 返回最后的关注数
            sqlSelect="select code,totalFollow from tbProductList where code='%s'" % (code)
            row_object=db.getToObject(sqlSelect)

        except :
            db.rollback()
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        #3. 打包成json object
        self.set_header('Access-Control-Allow-Origin','*')
        #self.set_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE')
        self.set_status(202)  # 201 操作成功
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(row_object,ensure_ascii=False))
        return
    
    # 查询用户是否关注了某产品
    def get(self,code):

        if not self.checkAppKey() :
            # 601 : 未经授权的第三方应用
            self.gotoErrorPage(601)
            return
        
        user=self.tokenToUser()

        if user is None :
            # 602 : 未经登录授权的应用
            self.gotoErrorPage(602)
            return

        
        try :
            db=dbMysql(config.dbConfig)
        except :
            # 701 : 数据库连接失败
            self.gotoErrorPage(701)
            return
        
        #1. 查询产品属性
        try :
            
            # 返回最后的关注数
            sqlSelect="select code,totalFollow from tbProductList where code=%s"
            pl_object=db.getToObject(sqlSelect,(code,))            
            
            #1.1 查询 tbProductFollower 表；
            sqlSelect= "Select user,pcode From tbProductFollower Where user=%s and pcode=%s"
            pf_List=db.getToList(sqlSelect,(user,code))
            
            
            if pf_List is not None :
                pl_object[user]='YES'
            else :
                pl_object={}
                pl_object[user]='NO'

        except :
            db.rollback()
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        #3. 打包成json object
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(pl_object,ensure_ascii=False))
        return    
