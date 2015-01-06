from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
import json

class list(WebRequestHandler):

    def get(self):  # 查询用户地址
        try :
            super().get(self)
            
            user=self.getTokenToUser()

            #1. 查询用户地址信息
            db=self.openDB()
            
            conditions={
                'select' : 'id,user,contact,tel,mobile,email,province,city,area,street,address,isDefault'
            }
            
            rows_list=db.getAllToList('vwAddressList',conditions,user,pk='user')
            
            self.closeDB()
            if len(rows_list)==0 :
                raise BaseError(802) #802 未找到数据
        
            self.response(rows_list)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)
    
                    
    def post(self):  # 新增用户地址
        
        try :
            super().post(self)
            user=self.getTokenToUser()
            objData=self.getRequestData()
            
            try :
                contact    = objData["c"]
                tel        = objData["t"]
                mobile     = objData["m"]
                email      = objData["e"]
                provinceId = objData["pi"]
                cityId     = objData["ci"]
                areaId     = objData["ai"]
                street     = objData["s"]
                address    = objData["a"]
                zipcode    = objData["z"]
                isDefault  = objData["i"]
            except :
                raise BaseError(801) # 参数错误
        
            db=self.openDB()
            db.begin()
            
            #1.用户地址数据 ;
            addressData={
                'user'       : user,
                'contact'    : contact,
                'tel'        : tel,
                'mobile'     : mobile,
                'email'      : email,
                'provinceId' : provinceId,
                'cityId'     : cityId,
                'areaId'     : areaId,
                'street'     : street,
                'address'    : address,
                'zipcode'    : zipcode,
                'isDefault'  : isDefault,
                'isDelete'   : 'N',
                'createUser' : user,
                'createTime' : '{{now()}}'
            }
            
            addressId=db.insert('tbUserAddress',addressData,commit=False)

            if addressId<0 :
                raise BaseError(702) # SQL 执行错误
            
            #2 如果新地址是默认地址，应修改tbUser表的默认地址栏
            if isDefault.upper()=='Y':
                updateData={
                    'addressId':addressId,
                    'updateTime':'{{now()}}',
                    'updateUser':user
                }
                db.updateByPk('tbUser',updateData,user,pk='user',commit=False)
            
            db.commit()
            self.closeDB()                

            #3. 打包成json object
            row={
                'user' : user,
                'address' : addressId
            }
            
            self.response(row) # 201 创建对象成功
            
        except BaseError as e:
            self.gotoErrorPage(e.code)
    

    def put(self,addressId):  # 修改用户地址，目前此API未使用
        
        try :
            super().put(self)
            
            user=self.tokenToUser()
            objData=self.getRequestData()
          
            try :
                contact    = objData["c"]
                tel        = objData["t"]
                mobile     = objData["m"]
                email      = objData["e"]
                provinceId = objData["pi"]
                cityId     = objData["ci"]
                areaId     = objData["ai"]
                street     = objData["s"]
                address    = objData["a"]
                zipcode    = objData["z"]
            except :
                raise BaseError(801) # 参数错误
        
            db=self.openDB()
            
            #1.用户地址数据 ;
            addressData={
                'user'       : user,
                'contact'    : contact,
                'tel'        : tel,
                'mobile'     : mobile,
                'email'      : email,
                'provinceId' : provinceId,
                'cityId'     : cityId,
                'areaId'     : areaId,
                'street'     : street,
                'address'    : address,
                'zipcode'    : zipcode,
                'updateUser' : user,
                'updateTime' : '{{now()}}'
            }
            
            db.updateByPk('tbUserAddress',updateData,addressId)
            self.closeDB()
            
            self.response() # 204 操作成功，无返回
        except BaseError as e:
            self.gotoErrorPage(e.code)


    def delete(self,addressId):  # 删除指定AddressId的地址
        try :
            super().delete(self)
            user=self.getTokenToUser()
            #1. 查询产品属性
            
            db=self.openDB()
            #1.用户地址数据 ;
            addressData={
                'isDelete'   : 'Y',
                'deleteUser' : user,
                'deleteTime' : '{{now()}}'
            }
            
            db.updateByPk('tbUserAddress',addressData,addressId)
            self.closeDB()
            
            self.response()

        except BaseError as e:
            self.gotoErrorPage(e.code)


    def patch(self,addressId):   # 变更用户默认地址
        try :
            super().patch(self)
            user=self.getTokenToUser()
            
            db=self.openDB()

            # 更新 tbUser 的默认地址；
            updateData={
                'addressId':addressId,
                'updateTime':'{{now()}}',
                'updateUser':user
            }
            
            db.begin()
            # 更改tbUser的addressId
            db.updateByPk('tbUser',updateData,user,pk='user',commit=False)
            
            # 更改tbUserAddress的isDefault字段
            updateData={
                'isDefault': "{{ if(id=%s,'Y','N')}}" % (addressId,),
                'updateTime':'{{now()}}',
                'updateUser':user
            }
            
            db.update('tbUserAddress',updateData,{'user':user},commit=False)
            db.commit()
            
            self.closeDB()

            self.response() # 204 操作成功，无返回
            
        except BaseError as e:
            self.gotoErrorPage(e.code)
