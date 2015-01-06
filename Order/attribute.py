from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class info(WebRequestHandler):

    def get(self):
        try :
            super().get(self)
            db=self.openDB()
            
            #1.1 查询付款方式；
            conditions = { 'select':'description,code,comment' , 'order':'sort desc'}
            rows_Payment = db.getAllToList('vwPayment',conditions)              

            #1.2. 查询配送方式；
            conditions = {'select':'description,code,comment' , 'order':'sort desc'}
            rows_Delivery = db.getAllToList('tbDelivery',conditions)             

            #1.3. 获得时间段方式
            conditions = {'select':'description,code'}
            rows_Period = db.getAllToList('vwQueryDate',conditions)               

            #1.4 获得订单状态
            conditions = {'select':'description,code' , 'order':'sort desc'}
            rows_Status = db.getAllToList('tbOrderStatus',conditions)                         
            
            self.closeDB()
            
            #2. 错误处理
            if len(rows_Payment)==0 or len(rows_Delivery)==0 or len(rows_Period)==0 or len(rows_Status)==0 :
                raise BaseError(802) # 无数据
        
            #3. 打包成json object
            rows={
                'payment'  : rows_Payment,
                'delivery' : rows_Delivery,
                'period'   : rows_Period,
                'status'   : rows_Status
            }
            
            self.response(rows)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)
