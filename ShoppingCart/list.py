import tornado.web
from dbMysql import dbMysql
import config
import json
import decimal
from easyOAuth.userinfo import Token

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

class info(tornado.web.RequestHandler):
    
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
    

    def options(self,id=''):
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,PATCH')
        self.set_header('Access-Control-Allow-Headers', 'app-key,authorization,Content-type')
      

    def get(self):  # 查看购物车里的商品
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
        
        #1. 查询用户购物车
        try :
            sqlSelect="SELECT id,pId,pCode,name,OriginalPrice,CurrentPrice,number,offline,available FROM vwShoppingCartList where user='%s'" % (user)
            rows_list=db.query(sqlSelect)
        except :
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        #3. 打包成json object
        rows={
            'User' : user,
            'ShoppingCart' : rows_list
        }              

        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(rows_list,cls=DecimalEncoder,ensure_ascii=False))
        return


    
    def post(self):  # 向购物车填加商品
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
            objRequestBody=json.loads(self.request.body.decode('utf-8'))
        
            if objRequestBody==None :
                raise Exception("参数有误")
            
            pid    = objRequestBody["pid"]
            pcode   = objRequestBody["pcode"]
            number = objRequestBody["number"]

        except :
            # 801 : 数据库连接失败
            self.gotoErrorPage(801)
            return
        
        
        try :
            db=dbMysql(config.dbConfig)
        except :
            # 701 : 数据库连接失败
            self.gotoErrorPage(701)
            return
        
        #1. 插入新地址
        try :
            
            db.begin()
            
            #1.1 插入 tbShoppingCart ;
            
            sqlInsert = (
              "INSERT INTO tbShoppingCart(user,pId,pCode,number,isDelete,createUser,createTime) "
              "VALUES (%s, %s, %s, %s, 'N', %s, now())"
            )
            
            shoppingCartId=db.save(sqlInsert,(user,pid,pcode,number,user))
            
            if shoppingCartId<0 :
                raise Exception('SQL 语句执行失败 !')
            
            db.commit()
            

        except :
            db.rollback()
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        #3. 打包成json object
        rows={
            'user' : user,
            'shoppingCartId' : shoppingCartId
        }        

        self.set_header('Access-Control-Allow-Origin','*')
        self.set_status(201)  # 201 创建对象成功
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(rows,ensure_ascii=False))
        
        return


    def delete(self):  # 删除购物车指定id

        if not self.checkAppKey() :
            # 601 : 未经授权的第三方应用
            self.gotoErrorPage(601)
            return
        
        user=self.tokenToUser()

        if user is None :
            # 602 : 未经登录授权的应用
            self.gotoErrorPage(602)
            return
        
        objRequestBody=json.loads(self.request.body.decode('utf-8'))

        if objRequestBody==None :
            raise Exception("参数有误")

        shoppingCartIds = objRequestBody["ids"]
        
        try :
            db=dbMysql(config.dbConfig)
        except :
            # 701 : 数据库连接失败
            self.gotoErrorPage(701)
            return
        
        #1. 查询产品属性
        try :
            db.begin()
            
            #1. 更新 tbShoppingCart 的isDelete为'Y'；
            sqlSelect="Select id from tbShoppingCart where id in (%s) for update" % (shoppingCartIds)
            db.query(sqlSelect)
            sqlUpdate ="Update tbShoppingCart set isDelete='Y',deleteTime=now(),deleteUser='%s' where id in (%s)" %(user,shoppingCartIds)
            db.update(sqlUpdate)                      

            db.commit()
            
        except :
            db.rollback()
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        #2. 返回
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_status(204)  # 204 操作成功，无返回
        return

    def patch(self):   # 变更购物车中指定商品数量
        if not self.checkAppKey() :
            # 601 : 未经授权的第三方应用
            self.gotoErrorPage(601)
            return
        
        user=self.tokenToUser()

        if user is None :
            # 602 : 未经登录授权的应用
            self.gotoErrorPage(602)
            return

        #number=int(self.get_argument("n",default='0'))
        #shopperCartId=int(self.get_argument("i",default='0'))
        
        objRequestBody=json.loads(self.request.body.decode('utf-8'))

        if objRequestBody==None :
            raise Exception("参数有误")

        shopperCartId = int(objRequestBody["id"])
        number        = int(objRequestBody["number"])
        

        if number<=0 or shopperCartId<=0:
            # 801 : 参数出错
            self.gotoErrorPage(801)
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
            
            #1. 更新 tbUserAddress 的默认地址；
            sqlSelect="Select id from tbShoppingCart where id='%s' for update" % (shopperCartId)
            db.query(sqlSelect)
            sqlUpdate ="Update tbShoppingCart set number=%s where id=%s;"
            db.update(sqlUpdate,(number,shopperCartId))                    
            
            db.commit()

        except :
            db.rollback()
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_status(204)  # 204 操作成功，无返回

        return
 