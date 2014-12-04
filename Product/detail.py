from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from Product import entity
import config
    
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
            url_path_medium = config.imageConfig['product.medium']['url']
            url_path_large  = config.imageConfig['product.large']['url']
            url_path_banner = config.imageConfig['product.banner']['url']
            url_path_small  = config.imageConfig['product.small']['url']
            conditions = {
                'select' : ("name,description,"
                            "{{CONCAT('%s/'}},{{image) as image}},"
                            "{{CONCAT('%s/'}},{{imagelarge) as imagelarge}},"
                            "{{CONCAT('%s/'}},{{imageBanners) as imageBanners}},"
                            "{{CONCAT('%s/'}},{{imageSmall) as imageSmall}},"
                            "starttime,endtime,statusCode,status,"
                           "supplierCode,supplierName,currentPrice,originalPrice,"
                           "totalTopic,totalFollow,totalSold,limit,totalAmount,code,pid,"
                           "batchNo,specification,categoryCode,category" % (url_path_medium,url_path_large,url_path_banner,url_path_small)
                           ) 
            }
            row_basic = db.getToObjectByPk('vwProductList',conditions,pcode,pk='code')
            
            #1.2. 查询产品详情；
            conditions = {
                'select' : 'id,description,html,sort',
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
                'html' : {
                    'struct':conditions['select'],
                    'list'  : rows_html
                }
            }
        
            self.response(rows)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)
    
    # 新增详细信息
    def post(self,pid):
        try :
            super().get(self)
            objUser=self.objUserInfo
            user=objUser['user']             
            objData=self.getRequestData()
                
            # 增加产品
            try :
                data={
                    'code'        : objData['code'],
                    'pid'         : pid,
                    'description' : objData['desc'],
                    'content'     : objData['html'],
                    'imgFiles'    : objData['imgFiles'],
                }
            except :
                raise BaseError(801) # 参数错误
            
            try:
                data['sort'] = objData['sort']
            except:
                data['sort']='1'
            
            data['createTime']='{{now()}}'
            data['createUserId']=user            
            
            p=entity.product()
            db=self.openDB()
            row=p.addProductDetail(data,db)
            self.closeDB()
            #row={
            #    objData['code'] : id
            #}            
            self.response(row)
        except BaseError as e:
            self.gotoErrorPage(e.code)
        
    # 变更产品内容
    def put(self,pid):
        try :
            super().get(self)
            objUser=self.objUserInfo
            user=objUser['user']            
            objData=self.getRequestData()
            if objData is None :
                raise BaseError(801) # 参数错误
                
            lstData={
                'id'          : 'id',
                'code'        : 'code',
                'description' : 'desc',
                'html'        : 'html',
                'imgFiles'    : 'imgFiles',
                'rImgFiles'   : 'rImgFiles',
                'sort'        : 'sort'
            }
            
            data={}
            
            for (k,v) in lstData.items():
                try:
                    if objData[v] is not None :
                        data[k]=objData[v]
                except:
                    pass
            
            try :
                id = data['id']
            except:
                raise BaseError(801) # 参数错误                
                
                
            data['updateTime']='{{now()}}'
            data['updateUserId']=user
            
            p=entity.product()
            db=self.openDB()
            returnData=p.updateProductDetail(id,data,db)
            self.closeDB()
            self.response(returnData)
        except BaseError as e:
            self.gotoErrorPage(e.code)
    
    # 下线产品再发（等待审核）/审核未通过/暂停/停止状态设置
    def patch(self,pcode):
        try :
            super().get(self)
            objUser=self.objUserInfo
            user=objUser['user']                  
            objData=self.getRequestData()
            data={
                'updateTime':'{{now()}}'
            }
            
            try:
                data['batchNo']=objData['bn']
                data['p_status']='WAIT'
            except:
                try :
                    data['p_status']=objData['st'].upper()
                    data['comments']=objData['cm']
                except :
                    raise BaseError(801) # 参数错误
            
            p=entity.product()
            db=self.openDB()
            p.updateProductStatus(data,pcode,db)
            self.closeDB()
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
    # 删除产品
    def delete(self,pcode):
        try :
            super().get(self)
            objUser=self.objUserInfo
            user=objUser['user']
            
            p=entity.product()
            db=self.openDB()
            p.delete(pcode,db)
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
        
