import tornado.web
from dbMysql import dbMysql
import config
import json
import decimal,datetime
from easyOAuth.userinfo import Token

class DecimalAndDateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, decimal.Decimal):
            return float(o)
        else :
            return json.JSONEncoder.default(self, obj)
        #return super(DecimalEncoder, self).default(o)    
    
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

class DataTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

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
      

    def get(self):  # 查询用户订单
        if not self.checkAppKey() :
            # 601 : 未经授权的第三方应用
            self.gotoErrorPage(601)
            return
        
        user=self.tokenToUser()

        if user is None :
            # 602 : 未经登录授权的应用
            self.gotoErrorPage(602)
            return
        
        # 分页
        offset=int(self.get_argument("o",default=0))
        rowcount=int(self.get_argument("r",default=1000))
        offset=offset*rowcount
        
        # 查询条件 
        s=self.get_argument("s",default='')
        v=self.get_argument("v",default='')
        

        
        try :
            db=dbMysql(config.dbConfig)
        except :
            # 701 : 数据库连接失败
            self.gotoErrorPage(701)
            return
        
        
        # 时间段查询
        while_date=''
        if s=='period' :
            if v!='' or v!='ALL':
                period=v
                sqlSelect='SELECT while_date FROM tbQueryDate where code=%s'
                row_list=db.getToObject(sqlSelect,(period,))
                if row_list is not None :
                    while_date=row_list['while_date']
        
        # 模糊查询
        
        sqlWhile=''
        
        if (len(while_date)>0):
            sqlWhile=' and ' + while_date
        
        
        #1. 查询用户订单
        try :
            sqlSelect=("SELECT id,orderNo,orderDate,contact,total,amount,payment,status "
                       "FROM vwOrderList where user='%s' %s limit %s,%s" % (user,sqlWhile,offset,rowcount) )
            rows_list=db.query(sqlSelect)
        except :
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        #3. 打包成json object
        rows={
            'User' : user,
            'OrderList' : rows_list
        }              

        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(rows,cls=DecimalAndDateTimeEncoder,ensure_ascii=False))
        return


    
    def post(self):  # 创建订单
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
            
            # 订单信息
            aId       = int(objRequestBody["aId"])       # 寄送地址ID
            payment   = objRequestBody["payment"]        # 付款方式ID
            shipping  = objRequestBody["shipping"]       # 运送方式ID
            total     = int(objRequestBody["total"])     # 货物总数量
            freight   = float(objRequestBody["freight"]) # 运费
            amount    = float(objRequestBody["amount"])  # 总金额
            comment   = objRequestBody["comment"]        # 备注
            orderList = objRequestBody["orders"]         # 详单
            
        except :
            # 801 : 参数错误
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
            
            #1.1 插入 tbOrder;
            
            sqlInsert = (
              "INSERT INTO tbOrderList (user,addressID,payment,shipping,freight,total,amount,createUser,comment,createTime,isDelete) "
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,now(),'N')"
            )
            
            orderId=db.save(sqlInsert,(user,aId,payment,shipping,freight,total,amount,user,comment))
            
            if orderId<0 :
                raise Exception('SQL 语句执行失败 !')
            
            for i,item in enumerate(orderList):
                pid=item["pid"]
                pcode=item["pcode"]
                name=item["name"]
                price=item["price"]
                oPrice=item["oPrice"]
                number=item["number"]
                sqlInsert = (
                    "INSERT INTO tbOrderDetail (oid,pid,pcode,pname,CurrentPrice,OriginalPrice,number,amount,createTime,createUser,isDelete) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, CurrentPrice*number,now(),%s ,'N')"
                )
                odId=db.save(sqlInsert,(orderId,pid,pcode,name,price,oPrice,number,user))
                if odId<0 :
                    raise Exception('SQL 语句执行失败 !')
                
                
            #1.2 更改tbOrderList.orderNo
            sqlSelect="select createTime from tbOrderList where id='%s' for update" % (orderId)
            orderDate=db.getToList(sqlSelect)
            sqlUpdate="Update tbOrderList set orderNo=CONCAT(DATE_FORMAT(createTime,'%s'),LPAD(id,8,'0')) where id=%s" % ('%Y%m%d',orderId)
            db.update(sqlUpdate)            

            db.commit()
        except :
            db.rollback()
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        # 生成订单号
        orderNo=orderDate[0].strftime("%Y%m%d")+"%08d"%orderId
        
        #3. 打包成json object
        rows={
            "user"    : user,
            "orderId" : orderId,
            "amount"  : amount,
            "payment" : freight,
            "orderNo" : orderNo
        }

        self.set_header('Access-Control-Allow-Origin','*')
        self.set_status(201)  # 201 创建对象成功
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(rows,cls=DecimalEncoder,ensure_ascii=False))
        
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
 
 
'''            
                           - id
                     pid          - 产品id
                     pcode        - 产品编码
                     name         - 产品名称
                     Price        - 当前价格
                     number       - 数量
'''
 