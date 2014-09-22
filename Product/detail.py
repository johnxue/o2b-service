from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
    
class info(WebRequestHandler):
    
    def get(self,pcode):
        
        try :
            super().get(self)

            row_BasicInfo={}
            row_HTML={}

            db=self.openDB()
            
            #1.1 查询产品基本信息；
            conditions = {
                'select' : ('name,description,image,imageBanners,starttime,endtime,status,'
                           'supplierCode,supplierName,currentPrice,originalPrice,'
                           'totalTopic,totalFollow,totalSold,limit,totalAmount,code,pid') 
            }
            row_basic = db.getToObjectByPk('vwProductList',conditions,pcode,pk='code')
            
            #1.2. 查询产品详情；
            conditions = {
                'select' : 'description,html',
                'order'  : 'sort'
            }
            rows_html = db.getAllToList('tbProductDetail',conditions,pcode,pk='code')
            
        
            self.closeDB()
        
            #2. 错误处理
            if len(row_basic)==0 :
                raise BaseError(802) # 未找到数据
                
        
            #3. 打包成json object
            rows={
                'basic' : row_basic,
                'html' : rows_html
            }
        
            self.response(rows)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)
