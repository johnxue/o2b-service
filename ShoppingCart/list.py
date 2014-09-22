from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class info(WebRequestHandler):

    def get(self):  # 查看购物车里的商品
        try :
            super().get(self)
            
            ''' <业务代码开始> --------------------------------------------------------------------------'''
            
            user = self.getTokenToUser()    # 从Token中获得用户名

            db   = self.openDB()            # 打开数据库
            
            #1. 查询用户购物车
            conditions = {
                'select' : 'id,pId,pCode,name,OriginalPrice,CurrentPrice,number,offline,available'
            }
            rows_list = db.getAllToList('vwShoppingCartList',conditions,user,pk='user')  # 查询结果以List的方式返回          

            self.closeDB()                # 关闭数据库
            
            if len(rows_list)==0 :        # 没有查到数据抛802异常
                raise BaseError(802)      
        
            #2. 打包成json object
            rows = {
                'User'         : user,
                'ShoppingCart' : rows_list
            } 

            self.response(rows)          # 返回查询结果
            
            ''' <业务代码结束> --------------------------------------------------------------------------'''
            
        except BaseError as e:
            self.gotoErrorPage(e.code)

    
    def post(self):  # 向购物车填加商品
        try :
            super().post(self)
            
            user    = self.getTokenToUser()
            objData = self.getRequestData()
           
            # -- 推荐以下方式对POST数据进行MAP和校验 
            try :
                pid    = objData["pid"]
                pcode  = objData["pcode"]
                number = objData["number"]
            except :
                raise BaseError(801) # 参数错误
        
            db = self.openDB()
            
            
            #1.插入购物车 tbShoppingCart ;
            cartData = {
                'user'       : user,
                'pId'        : pid,
                'pCode'      : pcode,
                'number'     : number,
                'createUser' : user,
                'createTime' : '{{now()}}',
                'isDelete'   : 'N'
            }
            
            cartId = self.insert('tbShoppingCart',cartData)
            
            if cartId < 0 :
                raise BaseError(703) # 插入失败
            
            self.closeDB()
        
            #2. 打包成json object
            rows = {
                'user' : user,
                'shoppingCartId' : shoppingCartId
            }

            self.response(rows) # 201 创建对象成功
            
        except BaseError as e:
            self.gotoErrorPage(e.code)


    def delete(self):  # 删除购物车指定id
        try :
            super().delete(self)
            
            user    = self.getTokenToUser()
            
            objData = self.getRequestData()
            
            cartIds = objData["ids"]

            db      = self.openDB()
            
            updateData = {
                'isDelete':'Y',
                'deleteTime':'{{now()}}',
                'deleteUser':user
            }
            
            db.updateByPk('tbShoppingCart',updateData,'{{ in (%s)}}'%(cartIds))
            self.closeDB()
        
            #2. 返回
            self.response() 
        except BaseError as e:
            self.gotoErrorPage(e.code)


    def patch(self):   # 变更购物车中指定商品数量
        try :
            super().patch(self)
            
            user     = self.getTokenToUser()
            
            objData = self.getRequestData()
            
            try :
                cartId = objData["id"]
                number = objData["number"]
            except :
                raise BaseError(801) # 参数错误
            
            if number <= 0 or cartId <= 0:
                raise BaseError(801) # 参数错误

            db = self.openDB()
            
            updateData = {
                           'number':number,
                           'updateTime':'{now()}',
                           'updateUser':user
                       }
                       
            db.updateByPk('tbShoppingCart',updateData,cartId)            
            
            self.closeDB()
            self.response() # 204 操作成功，无返回
        except BaseError as e:
            self.gotoErrorPage(e.code)