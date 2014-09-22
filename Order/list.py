from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class info(WebRequestHandler):
    # 查询指定条件的订单（总单）    
    def getOrderList(self,db,where_conditions):
        conditions={
            'select' : 'id,orderNo,orderDate,contact,total,amount,payment,status,statuscode',
            'where' : where_conditions
        }
        rows_list = db.getAllToList('vwOrderList',conditions)
        return rows_list
    
    # 查询指定条件的订单详单（详单）    
    def getOrderDetailList(self,db,where_conditions):
        #1. 查询用户订单
        conditions={
            'select' : 'oid,image,pcode,pname,number,price,amount',
            'where' : where_conditions
        }
        detail_list = db.getAllToList('vwOrderDetail',conditions)        
        return detail_list 
    

    def get(self):  # 查询用户订单
        try :
            super().get(self)
            user=self.getTokenToUser()        
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
    
            db=self.openDB()

            # 模糊查询 - 开始
            if len(searchString)>0 :
                sw=''
                for word in searchString.split(' ') :
                    sw+='concat(orderNo,pname) like "%'+word+'%" or '
                searchString='%'+searchString.replace(' ','%')+'%'
                where_conditions=' %s concat(orderNo,pname) like "%s"' % (sw,searchString)
                
                detail_list=self.getOrderDetailList(db, where_conditions)
                if len(detail_list)==0 :
                    raise BaseError(802) # 没有找到数据                    
                
                    
                # 生成订单号集合到 ids
                ids=''
                if len(detail_list)>0 :
                    for  row in detail_list :
                        if ids.find(str(row[0]))<0:
                            ids+=str(row[0])+','
                    ids+='-1'            
                
            # 模糊查询 - 结束
            
            # 按时间段查询
            where_date=where_status=where_search=''
            if s=='period' :
                if v!='' or v!='ALL':
                    period=v
                    
                    conditions={
                                'select' : 'where_date'
                            }
                    rows_list = db.getToObjectByPk('tbQueryDate',conditions,period,pk='code')                      
                    
                    if len(row_list)>0 :
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
            where_conditions=" user='%s' %s limit %s, %s" % (user,sqlWhere,offset,rowcount)
            rows_list=self.getOrderList(db, where_conditions)
            
            if len(rows_list)==0 :
                raise BaseError(802) # 没有找到数据                    
                
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
                where_conditions=" oid in (%s)" % (ids)
                detail_list=self.getOrderDetailList(db,where_conditions)
                if len(detail_list)==0 :
                    raise BaseError(802) # 没有找到数据                    
            
            self.closeDB()
            
            if len(detail_list)>0:   
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
            
            self.response(rows)
                       
        except BaseError as e:
            self.gotoErrorPage(e.code)

        
    def post(self):  # 创建订单
        try :
            super().post(self)
            user=self.getTokenToUser()
        
            objRequestBody=self.getRequestData()
            
            try :
            
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
                raise BaseError(801) # 参数错误
                
            db=self.openDB()
            db.begin()
            
            #1.1 插入 tbOrder;
            insertData={
                'user'       : user,
                'addressID'  : aId,
                'payment'    : payment,
                'shipping'   : shipping,
                'freight'    : freight,
                'total'      : total,
                'amount'     : amount,
                'comment'    : comment,
                'createUser' : user,
                'createTime' : '{{now()}}',
                'isDelete'   : 'N',
                'status'     : '110'  # status- 110 等待买家付款 
            }
            
            orderId=db.insert('tbOrderList',insertData)            
            
            #sqlInsert = (
            #  "INSERT INTO tbOrderList (user,addressID,payment,shipping,freight,total,amount,createUser,comment,createTime,isDelete,status) "
            #  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,now(),'N','110')"
            #)
            #
            #orderId=db.save(sqlInsert,(user,aId,payment,shipping,freight,total,amount,user,comment))
            
            if orderId<0 :
                raise BaseError(702) # SQL执行错误                    
            
            for i,item in enumerate(orderList):
                pid=item["pid"]
                pcode=item["pcode"]
                name=item["name"]
                price=item["price"]
                oPrice=item["oPrice"]
                number=item["number"]
                
                insertData={
                    'oid'           : orderId,
                    'pid'           : pid,
                    'pcode'         : pcode,
                    'pname'         : name,
                    'CurrentPrice'  : price,
                    'OriginalPrice' : oPrice,
                    'number'        : number,
                    'amount'        : price*number,
                    'createUser'    : user,
                    'createTime'    : '{{now()}}',
                    'isDelete'      : 'N'
                }
                odId=db.insert('tbOrderDetail',insertData)                      
                
                #sqlInsert = (
                #    "INSERT INTO tbOrderDetail (oid,pid,pcode,pname,CurrentPrice,OriginalPrice,number,amount,createTime,createUser,isDelete) "
                #    "VALUES (%s, %s, %s, %s, %s, %s, %s, CurrentPrice*number,now(),%s ,'N')"
                #)
                #odId=db.save(sqlInsert,(orderId,pid,pcode,name,price,oPrice,number,user))
                
                if odId<0 :
                    raise BaseError(801) # SQL执行错误                    
                    
                #1.2 更改tbOrderList.orderNo
                updateData={
                    "orderNo" : "{{CONCAT(DATE_FORMAT(createTime,'%s'),LPAD(id,8,'0'))}}" % ('%Y%m%d')
                }
                
                db.updateByPk('tbOrderList',updateData,orderId,commit=False)
                
                #sqlSelect="select createTime from tbOrderList where id='%s' for update" % (orderId)
                #orderDate=db.getToList(sqlSelect)
                
                #sqlUpdate="Update tbOrderList set orderNo=CONCAT(DATE_FORMAT(createTime,'%s'),LPAD(id,8,'0')) where id=%s" % ('%Y%m%d',orderId)
                #db.update(sqlUpdate)            
    
                db.commit()
                
                row= db.getToObjectByPk('tbOrderList',{'select':'orderNo'},orderId)
                self.closeDB()
                    
                # 生成订单号
                
                #orderNo=orderDate[0].strftime("%Y%m%d")+"%08d"%orderId
                
                #3. 打包成json object
                rows={
                    "user"    : user,
                    "orderId" : orderId,
                    "amount"  : amount,
                    "payment" : freight,
                    "orderNo" : row['orderNo']
                }
                
                self.response(rows)
                           
        except BaseError as e:
            self.gotoErrorPage(e.code)
       

    '''删除指定oids订单，输入为订单组,如果订单中有状态不为9的订单，则该订单不会被岀除'''
    def delete(self):  
        try :
            super().delete(self)
            user=self.getTokenToUser()
            
            objRequestBody=self.getRequestData()
            oids = objRequestBody["ids"]
            
            db=self.openDB()
            
            # 删除的前提条件，订单状态必须为9XX，即订单处于交易成功、交易关闭、已退款状态
            ids_list=db.getAllToList('tbOrderList',{'select':'id','where':'id in (%s) and left(status,1)="9"'%(oids)})
            
            # 生成订单号集合到 ids
            ids=''
            if len(ids_list)>0 :
                for  row in ids_list :
                    if ids.find(str(row[0]))<0:
                        ids+=str(row[0])+','
                ids+='-1'
            else : 
                raise BaseError(802) # 未查询到数据
            
            
            updateData = {'isDelete':'Y','deleteTime':'{{now()}}','deleteUser':user}
            
            db.begin()

            #1. 更新 tbOrderList 的isDelete为'Y'；
            db.updateByPk('tbOrderList',updateData,'{{in (%s)}}' %(ids),commit=False)            
            #2. 更新 tbOrderDetail 的isDelete为'Y'；
            db.updateByPk('tbOrderDetail',updateData,'{{ in (%s)}}'%(ids),pk='oid',commit=False)                
            
            db.commit()
            self.closeDB()
            self.response()
                       
        except BaseError as e:
            self.gotoErrorPage(e.code)
