from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class info(WebRequestHandler):
    
    # 查询指定条件的订单（总单） - 注意：此方法与list模块中定义的同名方法返回的字段不同    
    def getOrderList(self,db,where_conditions):
        conditions={
            'select' : 'id,orderNo,orderDate,contact,total,amount,payment,status,address,zipcode,tel,mobile,email',
            'where' : where_conditions
        }
        rows_list = db.getAllToList('vwOrderList',conditions)
        return rows_list
    
    # 查询指定条件的订单详单（详单） -  注意：此方法与list模块中定义的同名方法返回的字段不同
    def getOrderDetailList(self,db,where_conditions):
        #1. 查询用户订单
        conditions={
            'select' : 'oid,image,pcode,pname,number,price,amount',
            'where' : where_conditions
        }
        detail_list = db.getAllToList('vwOrderDetail',conditions)        
        return detail_list     


    def get(self,oid):  # 查询用户订单
        try :
            super().get(self)
            user=self.getTokenToUser()
        
            db=self.openDB()
    
            #1. 查询用户订单
            where_conditions="user='%s' and id=%s" % (user,oid)
            rows_list=self.getOrderList(db, where_conditions)
            
            if len(rows_list)==0 :
                BaseError(802) # 没有找到数据             
            
            # 根据oid查询详单
            #1. 根据订单ID查询用户详单
            where_conditions="oid =%s" % (oid)
            detail_list=self.getOrderDetailList(db,where_conditions)

            self.closeDB() 
                
            #3. 打包成json object
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
            
            self.response(rows)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)

    def delete(self,oid):  # 取消未发货订单
        # 卖家发货前可以取消订单，并退款，卖家发货后只能申请退换货
        try :
            super().delete(self)
            user=self.getTokenToUser()

            # 取消订单的前提条件，订单状态必须为1XX，即订单处于买家未支付、买家已支付、等待卖家发货状态
            db=self.openDB()
            
            #1. 更新 tbOrderList 的status为'Y'；
            select={
                "select" : "id",
                "where"  : "id=%s and left(status,1)='1'" % (oid)
            }
            ids_list=db.getAllToList('tbOrderList',select)
            if len(ids_list)==0 :
                BaseError(802) # 没有找到数据             
 
            
            # 如果 状态码-110 即等待买家付款状态，直接关闭交易  (920 - 交易关闭)
            # 如果 状态码120,130 即买家已付款状态，进入退款状态 (430 - 等待退款)
            update={
                'status' : "{{if(status='110','920','430')}}",
                'updateTime' : '{{now()}}',
                'updateUser' : user
            }
            db.updateByPk('tbOrderList',update,oid)
            
            self.closeDB()
            self.response()
                    
        except BaseError as e:
            self.gotoErrorPage(e.code)
