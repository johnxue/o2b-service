import tornado.web
from dbMysql import dbMysql
import config
import json
from easyOAuth.userinfo import Token

# 
class list(tornado.web.RequestHandler):
    
    def gotoErrorPage(self,error_code) :
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,PATCH')
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
      

    def get(self):  # 查询用户地址
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
        
        #1. 查询用户地址信息
        try :
            sqlSelect="SELECT id,user,contact,tel,mobile,email,province,city,area,street,address,isDefault FROM vwAddressList where user='%s'" % (user)
            rows_list=db.query(sqlSelect)
        except :
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        #3. 打包成json object

        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(rows_list,ensure_ascii=False))
        
        return


    
    def post(self):  # 新增用户地址
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
            
            contact    = objRequestBody["c"]
            tel        = objRequestBody["t"]
            mobile     = objRequestBody["m"]
            email      = objRequestBody["e"]
            provinceId = objRequestBody["pi"]
            cityId     = objRequestBody["ci"]
            areaId     = objRequestBody["ai"]
            street     = objRequestBody["s"]
            address    = objRequestBody["a"]
            zipcode    = objRequestBody["z"]
            isDefault  = objRequestBody["i"]
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
            
            #1.1 插入 tbUserAddress；
            
            sqlInsert = (
              "INSERT INTO tbUserAddress(user,contact,tel,mobile,email,provinceId,cityId,areaId,street,address,zipcode,isDefault,isDelete,createUser,createTime) "
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'N',%s,now())"
            )
            
            addressId=db.save(sqlInsert,(user,contact,tel,mobile,email,provinceId,cityId,areaId,street,address,zipcode,isDefault,user))
            
            if addressId<0 :
                raise Exception('SQL 语句执行失败 !')
            
            #1.2 如果新地址是默认地址，应修改tbUser表的默认地址栏
            if isDefault.upper()=='Y':
                sqlSelect="Select user from tbUser where user='%s' for update" % (user)
                db.query(sqlSelect)                
                sqlUpdate ="Update tbUser set addressId=%s where user='%s'"
                db.update(sqlUpdate)                
            
            db.commit()
            

        except :
            db.rollback()
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        #3. 打包成json object
        rows={
            'user' : user,
            'address' : addressId
        }        

        self.set_header('Access-Control-Allow-Origin','*')
        self.set_status(201)  # 201 创建对象成功
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(rows,ensure_ascii=False))
        
        return


    
    def put(self,addressId):  # 修改用户地址
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

            aid        = addressId
            contact    = objRequestBody["c"]
            tel        = objRequestBody["t"]
            mobile     = objRequestBody["m"]
            email      = objRequestBody["e"]
            provinceId = objRequestBody["pi"]
            cityId     = objRequestBody["ci"]
            areaId     = objRequestBody["ai"]
            street     = objRequestBody["s"]
            address    = objRequestBody["a"]
            zipcode    = objRequestBody["z"]
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
        
        #1. 查询产品属性
        try :
            db.begin()
            
            sqlSelect="Select user from tbUserAddress where id='%s' for update" % (aid)
            db.query(sqlSelect)
            
            sqlUpdate ='''Update tbUserAddress set contact=%s ,tel=%s ,mobile=%s ,email=%s ,provinceId=%s,
                                 cityId=%s ,areaId=%s ,street=%s ,address=%s ,zipcode=%s
                          where id=%s"
                        '''
            db.update(sqlUpdate,((contact,tel,mobile,email,provinceId,cityId,areaId,street,address,zipcode,aid)))                    
            
            db.commit()
        except :
            db.rollback()
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        

        self.set_header('Access-Control-Allow-Origin','*')
        self.set_status(204)  # 204 操作成功，无返回
        return



    
    def delete(self,addressId):  # 删除指定AddressId的地址

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
            
            #1.1 从用户地址库删除 tbUserAddress；
            #sqlDelete = "Delete From tbUserAddress Where id=%s" % (addressId)
            #db.delete(sqlDelete)
            
            #1. 更新 tbUserAddress 的isDelete为'Y'；
            sqlSelect="Select id from tbUserAddress where id='%s' for update" % (addressId)
            db.query(sqlSelect)
            sqlUpdate ="Update tbUserAddress set isDelete='Y',deleteTime=now(),deleteUser=%s where id=%s;"
            db.update(sqlUpdate,(user,addressId))                      

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

    def patch(self,addressId):   # 变更用户默认地址
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
            
            #1. 更新 tbUserAddress 的默认地址；
            sqlSelect="Select user from tbUserAddress where user='%s' for update" % (user)
            db.query(sqlSelect)
            sqlUpdate ="Update tbUserAddress set isDefault=if(id=%s,'Y','N') where user=%s;"
            db.update(sqlUpdate,(addressId,user))                    

            #2. 更新 tbUser 的默认地址；
            sqlSelect="Select user from tbUser where user='%s' for update" % (user)
            db.query(sqlSelect)
            sqlUpdate ="Update tbUser set addressId=%s where user=%s;"
            db.update(sqlUpdate,(addressId,user))                    
            
            db.commit()

        except :
            db.rollback()
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        #3. 打包成json object
        rows={
            'user' : user,
            'defaultAddressId' : addressId
        }        

        self.set_header('Access-Control-Allow-Origin','*')
        self.set_status(204)  # 204 操作成功，无返回

        return
 