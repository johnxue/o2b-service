from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
    
class info(WebRequestHandler):
    
    def get(self,pcode):
        
        try :
            #super().get(self)
            self._db_=None
            self.checkAppKey()            

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
    
    # 新增详细信息
    def post(self):
        try :
            super().get(self)
            objUser=self.objUserInfo
            user=objUser['user']             
            objData=self.getRequestData()
                
            # 增加产品
            try :
                data={
                    'code'        : objData['c'],
                    'pid'         : objData['pid'],
                    'description' : objData['description'],
                    'html'        : objData['html'],
                }
            except :
                raise BaseError(801) # 参数错误
            
            data['createTime']='{{now()}}'
            data['createUserId']=user            
            
            p=entity.product()
            db=self.openDB()
            id=p.addProductDetail(data,db)
            self.closeDB()
            row={
                objData['c'] : id
            }            
            self.response(row)
        except BaseError as e:
            self.gotoErrorPage(e.code)
        
    # 变更产品内容
    def put(self,pcode):
        try :
            super().get(self)
            objUser=self.objUserInfo
            user=objUser['user']            
            objData=self.getRequestData()
            if objData is None :
                raise BaseError(801) # 参数错误
                
            lstData={
                'Image'         : 'img',
                'imagelarge'    : 'imgl',
                'imageBanners'  : 'imgb',
                'imageSmall'    : 'imgs',
                'supplierCode'  : 'sc',
                'categoryCode'  : 'cat',
                'statusCode'    : 'st',
                'startTime'     : 'stm',
                'endTime'       : 'etm',
                'currentPrice'  : 'cp',
                'originalPrice' : 'op',
                'totalAmount'   : 'ta',
                'totalTopic'    : 'tt',
                'totalFollow'   : 'tf',
                'totalSold'     : 'ts',
                'limit'         : 'lmt',
            }
            
            for (k,v) in lstData.items():
                try:
                    data[k]=objData[v]
                except:
                    pass
            
            data['updateTime']='{{now}}'
            data['updateUserId']=user
            
            ads=entity.adsense()
            db=self.openDB()
            aid=ads.update(data,id,db)
            self.closeDB()
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)
    
    # 修改/设置广告参数   
    def patch(self,pcode):
        try :
            super().get(self)
            objUser=self.objUserInfo
            user=objUser['user']                  
            objData=self.getRequestData()
            data={
                'updateTime':'{{now()}}'
            }
            
            try :
                data['status']=objData['st'].upper()
                data['comments']=objData['cm']
            except :
                raise BaseError(801) # 参数错误
            
            ads=entity.adsense()
            db=self.openDB()
            aid=ads.update(data,pcode,db)
            self.closeDB()
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
    # 删除广告
    def delete(self,pcode):
        try :
            super().get(self)
            objUser=self.objUserInfo
            user=objUser['user']
            
            ads=entity.adsense()
            db=self.openDB()
            aid=ads.delete(pcode,db)
            self.closeDB()
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)       
            
            
    # 同步mysql与redis    
    def redisSync(self):
        ads=entity.adsense()
        db=self.openDB()
        list=ads.sync(db)
        self.closeDB()
        return list
        
