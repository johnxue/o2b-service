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
    

    def options(self):
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,PATCH')
        self.set_header('Access-Control-Allow-Headers', 'app-key,authorization,Content-type')
    
    

    def post(self):  # 创建退货换单
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
            oid         = int(objRequestBody["oid"])          # 订单ID
            orderNo     = int(objRequestBody["orderNo"])      # 订单号
            pcode       = objRequestBody["pcode"]             # 产品编码
            pname       = objRequestBody["pname"]             # 产品名称
            number      = int(objRequestBody["number"])       # 退换货数量
            mode        = objRequestBody["mode"]              # 退货换模式
            description = objRequestBody["description"]       # 问题描述
            imgProblem  = objRequestBody["imgProblem"]        # 问题图片
            swapOrderNo = mode+orderNo                        # 退货货单号   

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
              "INSERT INTO tbReturns (user,oid,orderNo,swapOrderNo,pcode,pname,number,mode,description,imgProblem,createUser,createTime,isDelete) "
              "VALUES (%s,%s,%s,%s, %s, %s, %s, %s, %s, %s, %s, now(),'N')"
            )
            
            orderId=db.save(sqlInsert,(user,oid,orderNo,swapOrderNo,pcode,pname,number,mode,description,imgProblem,user))
            
            if orderId<0 :
                raise Exception('SQL 语句执行失败 !')
            
            #1.2 更改tbOrderList.status=310
            sqlSelect="select id from tbOrderList where id='%s' for update" % (oid)
            db.getToList(sqlSelect)
            # status=310 - 买家申请退换货
            sqlUpdate="Update tbOrderList set status='310'，updateTime=now(),updateUser='%s' where id=%s" % (user,oid)
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
            "user"         : user,
            "orderId"      : oid,
            "orderNo"      : orderNo,
            "swapOrderNo"  : swapOrderNo,
        }

        self.set_header('Access-Control-Allow-Origin','*')
        self.set_status(201)  # 201 创建对象成功
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(rows,cls=DecimalEncoder,ensure_ascii=False))
        
        return

