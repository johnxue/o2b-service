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
    
    # 查询指定条件的订单（总单）    
    def getOrderList(self,db,where_conditions):
        try :
            sqlSelect=("SELECT id,orderNo,orderDate,contact,total,amount,payment,status "
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
        searchString=self.get_argument("q",default='')
        
        # 初始化数据
        ids=''  # 订单号集合
        row_list=detail_list=None  # 订单及订单详情

        try :
            db=dbMysql(config.dbConfig)
        except :
            # 701 : 数据库连接失败
            self.gotoErrorPage(701)
            return


        # 模糊查询
        if len(searchString)>0 :
            sw=''
            for word in searchString.split(' ') :
                sw+='concat(orderNo,pname) like "%'+word+'%" or '
            searchString='%'+searchString.replace(' ','%')+'%'
            where_conditions='where %s concat(orderNo,pname) like "%s"' % (sw,searchString)
            
            detail_list=self.getOrderDetailList(db, where_conditions)
            if detail_list is None  :
                # 702 : SQL查询失败
                self.gotoErrorPage(702)
                return
            
            if len(detail_list)==0:
                self.set_header('Access-Control-Allow-Origin','*')
                self.set_status(404)
                return
                
            # 生成订单号集合到 ids
            ids=''
            if len(detail_list)>0 :
                for  row in detail_list :
                    if ids.find(str(row[0]))<0:
                        ids+=str(row[0])+','
                ids+='-1'            
            

        # 按时间段查询
        where_date=where_status=where_search=''
        if s=='period' :
            if v!='' or v!='ALL':
                period=v
                sqlSelect='SELECT where_date FROM tbQueryDate where code=%s'
                row_list=db.getToObject(sqlSelect,(period,))
                if row_list is not None :
                    where_date=row_list['where_date']
        # 按订单状态查询
        elif s=='status' :
            where_status="statuscode = '%s'" % (v)
        # 模糊查询
        elif len(searchString)>0 and len(detail_list)>0 :
            where_search="id in (%s) " % (ids)
        
        sqlWhere=''
        if (len(where_date)>0):
            sqlWhere+=' and ' + where_date
        
        if (len(where_status)>0):
            sqlWhere+=' and '+where_status
            
        if (len(where_search)>0):
            sqlWhere+=' and '+where_search
        
        #1. 查询用户订单
        where_conditions=" where user='%s' %s limit %s, %s" % (user,sqlWhere,offset,rowcount)
        rows_list=self.getOrderList(db, where_conditions)
        if rows_list=='ERROR' :
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return            
        
        #3. 打包成json object
        rows={
            'User' : user,
            'OrderList' : rows_list
        }
        
        # 生成订单号集合到 ids
        if len(ids)<=0 and len(rows_list)>0 :
            for  row in rows_list :
                ids+=str(row[0])+','
            ids+='-1'
        
        # 根据ids查询详单
        obj_OD_Imgs={}
        if len(ids)>0 and (detail_list is None):
            #1. 根据订单ID查询用户详单
            where_conditions="where oid in (%s)" % (ids)
            detail_list=self.getOrderDetailList(db,where_conditions)
            if detail_list=='ERROR' :
                # 702 : SQL查询失败
                self.gotoErrorPage(702)
                return                        
        
        db.close
            
        if detail_list is not None:   
            # 根据订单号汇总各详单中的图片文件到od
            for  row in detail_list :
                try : 
                    #obj_OD_Imgs[row[0]]+=','+row[1]
                    obj_OD_Imgs[row[0]].append(row[1])
                except :
                    #obj_OD_Imgs[row[0]]=row[1]
                    obj_OD_Imgs[row[0]]=[]
                    obj_OD_Imgs[row[0]].append(row[1])
        
        # 拼接订单 
        if len(rows_list)>0 :
            for  i in range(len(rows_list)) :
                try :
                    rows_list[i]=(rows_list[i],obj_OD_Imgs[rows_list[i][0]])
                except :
                    pass
            
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
              "INSERT INTO tbOrderList (user,addressID,payment,shipping,freight,total,amount,createUser,comment,createTime,isDelete,status) "
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,now(),'N','110')"
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


    def delete(self):  # 删除指定oids订单，输入为订单组

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
        
        oids = objRequestBody["ids"]
        
        try :
            db=dbMysql(config.dbConfig)
        except :
            # 701 : 数据库连接失败
            self.gotoErrorPage(701)
            return
        
        # 删除的前提条件，订单状态必须为9XX，即订单处于交易成功、交易关闭、已退款状态
        
        #1. 查询产品属性
        try :
            db.begin()
            
            #1. 更新 tbOrderList 的isDelete为'Y'；
            sqlSelect="Select id from tbOrderList where id in (%s) and left(status,1)='9' for update" % (oids)
            ids_list=db.query(sqlSelect)
            if ids_list is None or len(ids_list)==0 :
                #没有找到返回404
                db.commit()
                db.close()
                self.set_header('Access-Control-Allow-Origin','*')
                self.set_status(404)
                return
            
            sqlUpdate ="Update tbOrderList set isDelete='Y',deleteTime=now(),deleteUser='%s' where id in (%s) and left(status,1)='9'" %(user,oids)
            db.update(sqlUpdate)
            
            # 生成订单号集合到 ids
            ids=''
            if len(ids_list)>0 :
                for  row in ids_list :
                    if ids.find(str(row[0]))<0:
                        ids+=str(row[0])+','
                ids+='-1'

            #2. 更新 tbOrderDetail 的isDelete为'Y'；
            sqlSelect="Select id from tbOrderDetail where oid in (%s) for update" % (ids)
            db.query(sqlSelect)
            sqlUpdate ="Update tbOrderDetail set isDelete='Y',deleteTime=now(),deleteUser='%s' where oid in (%s)" %(user,ids)
            db.update(sqlUpdate)            
        
            db.commit()
            db.close()
        except :
            db.rollback()
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        #2. 返回
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_status(204)  # 204 操作成功，无返回
        return