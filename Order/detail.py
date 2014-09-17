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
            return json.JSONEncoder.default(self, o)
        #return super(DecimalEncoder, self).default(o)    
    
class info(tornado.web.RequestHandler):
    
    def gotoErrorPage(self,error_code) :
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,PATCH')
        self.set_header('Access-Control-Allow-Headers', 'app-key,authorization,Content-type')
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
    
    # 查询指定条件的订单（总单）    
    def getOrderList(self,db,where_conditions):
        try :
            sqlSelect=("SELECT id,orderNo,orderDate,contact,total,amount,payment,status,address,zipcode,tel,mobile,email "
                       "FROM vwOrderList %s")%(where_conditions)
            rows_list=db.query(sqlSelect)
        except :
            rows_list="ERROR"
        return rows_list
    
    # 查询指定条件的订单详单（详单）    
    def getOrderDetailList(self,db,where_conditions):
        #1. 查询用户订单
        try :
            sqlSelect=("SELECT oid,image,pcode,pname,number,currentPrice as Price ,amount "
                       " FROM vwOrderDetail %s" % (where_conditions) )
            detail_list=db.query(sqlSelect)            
        except :
            detail_list="ERROR"
        return detail_list 
    

    def get(self,oid):  # 查询用户订单
        if not self.checkAppKey() :
            # 601 : 未经授权的第三方应用
            self.gotoErrorPage(601)
            return
        
        user=self.tokenToUser()

        if user is None :
            # 602 : 未经登录授权的应用
            self.gotoErrorPage(602)
            return
        
        
        # 初始化数据
        row_list=detail_list=None  # 订单及订单详情

        try :
            db=dbMysql(config.dbConfig)
        except :
            # 701 : 数据库连接失败
            self.gotoErrorPage(701)
            return

        #1. 查询用户订单
        where_conditions=" where user='%s' and id=%s" % (user,oid)
        rows_list=self.getOrderList(db, where_conditions)
        if rows_list=='ERROR' :
            # 702 : SQL查询失败
            db.close()
            self.gotoErrorPage(702)
            return            
        
        
        # 根据oid查询详单
        if rows_list is not None:
            #1. 根据订单ID查询用户详单
            where_conditions="where oid =%s" % (oid)
            detail_list=self.getOrderDetailList(db,where_conditions)
            if detail_list=='ERROR' :
                # 702 : SQL查询失败
                db.close()
                self.gotoErrorPage(702)
                return
        
        db.close() 
        
        #3. 打包成json object
        if rows_list is None or len(rows_list)==0 :
            self.set_header('Access-Control-Allow-Origin','*')
            self.set_status(404)  # 404 没有找到
            return
        
        row=rows_list[0]
        order_list={
            "oid":row[0],
            "orderNo":row[1],
            "orderDate":row[2],
            "total":row[4],
            "amount":row[5],
            "payment":row[6],
            "status":row[7]
        }
        
        address_list={
            "contact"  : row[3],
            "address"  : row[8],
            "zipcode"  : row[9],
            "tel"      : row[10],
            "mobile"   : row[11],
            "email"    : row[12]
        }
        
        rows={
          'User'         : user,
          'AddressInfo'  : address_list,
          'OrderInfo'    : order_list,
          'OrderDetail'  : detail_list
        }
            
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(rows,cls=DecimalAndDateTimeEncoder,ensure_ascii=False))
        return

    def delete(self):  # 取消未发货订单
        # 卖家发货前可以取消订单，并退款，卖家发货后只能申请退换货
        
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
        
        # 取消订单的前提条件，订单状态必须为1XX，即订单处于买家未支付、买家已支付、等待卖家发货状态
        
        try :
            db.begin()
            
            #1. 更新 tbOrderList 的status为'Y'；
            sqlSelect="Select id from tbOrderList where id in (%s) and left(status,1)='1' for update" % (oids)
            ids_list=db.query(sqlSelect)
            if ids_list is None or len(ids_list)==0 :
                #没有找到返回404
                db.commit()
                db.close()
                self.set_header('Access-Control-Allow-Origin','*')
                self.set_status(404)
                return
            
            # 如果 状态码-110 即等待买家付款状态，直接关闭交易
            # 如果 状态码120,130 即买家已付款状态，进入退款状态
            sqlUpdate ="Update tbOrderList set status=if(status='110','920','430'),updateTime=now(),updateUser='%s' where id in (%s) and left(status,1)='1'" %(user,oids)
            db.update(sqlUpdate)
            
            db.commit()
        except :
            db.rollback()
            db.close()
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        db.close()
        
        #2. 返回
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_status(204)  # 204 操作成功，无返回
        return


 
