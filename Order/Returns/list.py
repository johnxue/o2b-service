from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class info(WebRequestHandler):
    
    def get(self):  # 查询用户退换货信息
        
        try :
            super().get(self)
            
            user=self.getTokenToUser()        
        
            # 分页
            offset=int(self.get_argument("o",default=0))
            rowcount=int(self.get_argument("r",default=1000))
            offset=offset*rowcount
            
            db=self.openDB()
            
            #1. 查询退换货单；
            conditions={
                'select' : ('id,swapOrderNo,orderNo,oid,pcode,pname,number,mode,description,'
                            'createTime,updateTime,status,comment'),
                'where' : 'user="%s"' % (user),
                'limit' : '%s,%s' % (offset,rowcount)
            }
            rows_list=db.getAllToList('vwReturns',conditions)

            self.closeDB()
            
            #2. 错误处理
            if len(rows_list)==0 :
                raise BaseError(802) # 没有找到数据                    
                
            #3. 打包成json object
            rows = {'swapOrder' : rows_list }
            self.response(rows)
             
        except BaseError as e:
            self.gotoErrorPage(e.code)


    def post(self):  # 创建退货换单
        try :
            super().post(self)
            user=self.getTokenToUser()        
        
            objRequestBody=self.getRequestData()
            
            try :
                # 订单信息
                oid         = int(objRequestBody["oid"])          # 订单ID
                orderNo     = objRequestBody["orderNo"]           # 订单号
                pcode       = objRequestBody["pcode"]             # 产品编码
                pname       = objRequestBody["pname"]             # 产品名称
                number      = int(objRequestBody["number"])       # 退换货数量
                mode        = objRequestBody["mode"]              # 退货换模式
                description = objRequestBody["description"]       # 问题描述
                imgProblem  = objRequestBody["imgProblem"]        # 问题图片
                swapOrderNo = mode+orderNo                        # 退货货单号   
            except :
                raise BaseError(801) # 参数错误
                
            db=self.openDB()
            db.begin()
            
            #1.1 插入 tbOrder;
           
            insertData={
                'user': user,
                'oid': oid,
                'orderNo':orderNo,
                'swapOrderNo':swapOrderNo,
                'pcode':pcode,
                'pname':pname,
                'number':number,
                'mode': mode,
                'description':description,
                'imgProblem': imgProblem,
                'createUser': user,
                'createTime': '{{now()}}',
                'isDelete': 'N',
                'status': '310'                # status- 310 买家申请退换货
            }
            
            soId=db.insert('tbReturns',insertData,commit=False)
            
            if soId<0 : raise BaseError(702) # SQL操作失败
            
            #1.2 更改tbOrderList.status=310
            updateData={
                'status':'310', 
                'updateTime':'{{now()}}',
                'updateUser':user
            }
            db.updateByPk('tbOrderList',updateData,oid,commit=False)            

            db.commit()
            self.closeDB()
        
            # 生成订单号
            #orderNo=orderDate[0].strftime("%Y%m%d")+"%08d"%orderId
        
            #3. 打包成json object
            rows={
                "user"         : user,
                "orderId"      : oid,
                "orderNo"      : orderNo,
                "swapOrderNo"  : swapOrderNo,
            }

            self.response(rows)
                        
        except BaseError as e:
            self.gotoErrorPage(e.code)
