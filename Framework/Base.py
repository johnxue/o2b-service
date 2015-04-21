# _version_ = 0.2.0
# 增加   returnErrorInfo 方法替换旧的 gotoErrorPage方法，新的returnErrorInfo可以返回具体的原始错误信息
# 将异常处理由 @operator_except 来统一捕获

import sys,traceback
import tornado.web
import tornado.gen
import config
from Framework.baseException import errorDic,BaseError
import decimal,datetime,json,ujson
import inspect
from easyOAuth.userinfo import Token
from User import entity


# 屏幕非法链接
class Base404Handler(tornado.web.RequestHandler):
    def head(self,*args,**kwargs):
        self.set_status(404)

    def get(self,*args,**kwargs):
        self.set_status(404)

    def post(self,*args,**kwargs):
        self.set_status(404)
        
    def put(self,*args,**kwargs):
        self.set_status(404)

    def delete(self,*args,**kwargs):
        self.set_status(404)
        
    def patch(self,*args,**kwargs):
        self.set_status(404)
        
    
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

class WebRequestHandler(tornado.web.RequestHandler):

    # Http Options
    def options(self,*args,**kwargs):
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,PATCH')
        self.set_header('Access-Control-Allow-Headers', 'app-key,app-secret,authorization,Content-type,X_Requested_With')
    
    # Http Response
    def response(self,data=None,status=200,angluar=True,callback=None,async=False):

        if status==200 : # 自动识别状态码
            callfun=inspect.stack()[1][3]
            if ('get' in callfun ) or ('put' in callfun and data) : status=200  # GET及PUT有返回时200 
            elif 'post' in callfun                                 : status =201  # POST成功时返回时 - 201
            elif ('put' in callfun or  'delete' in callfun or 'patch' in callfun) and data is None  :
                status = 204                                                      # DELETE,PUT,PATCH无返回时 - 204	
        
        self.set_status(status)
        self.options()
        
        if data is not None :
            if angluar : self.write(")]}',\n")
            strJson=json.dumps(data,cls=DecimalAndDateTimeEncoder,ensure_ascii=False)
            if callback :
                self.set_header("Content-Type", "application/x-javascript")
                #self._write_buffer=[escape.utf8(callback),"(",strJson,")"]
                self.write(callback+"("+strJson+")")
            else :
                self.set_header("Content-Type", "application/json; charset=UTF-8")
                self.write(strJson)
        if (not async) or (data is None) : self.finish()
        
    def getRequestHeader(self,header):
        return self.request.headers.get(header)
        
    def init(self):
        self.__init()
        
    def __init(self,*args,**kwargs):
        self._db_=None
        self.checkAppKey()
        
        self.objUserInfo=None
        try :
            if kwargs['userAuth'] :
                self.objUserInfo=self.getUserToObjct()
        except:
            self.objUserInfo=self.getUserToObjct()
        
        self._now_time_ = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def head(self,*args,**kwargs):
        self.__init()        
        
    def get(self,*args,**kwargs):
        self.__init(*args,**kwargs)
        
    def post(self,*args,**kwargs):
        self.__init()
        
    def delete(self,*args,**kwargs):
        self.__init()
        
    def put(self,*args,**kwargs):
        self.__init()
        
    def patch(self,*args,**kwargs):
        self.__init()        
        
    
    def gotoErrorPage(self,error_code,error_string='',help=False) :
        #    _version_=0.1.0
        #在错误处理中如果数据库连接是打开发，应回滚并关闭,回滚前须提交的数据必须提交
        try :
            if self._db_ is not None :
                self._db_.rollback()
                self.closeDB()
        except:
            pass
        eid=int(error_code)
        try:
            error=errorDic[eid]
        except:
            error=errorDic[900]
        
        # 如果存在自定义的错误消息者，替换原消息体
        if error_string!='' :
            error['message']=error_string

        #info=sys.exc_info()  
        #error['help_document']=info[0]+":"+info[1]  
        info=traceback.print_exc()
        
        if help is False :
            try :
                del error['help_document']
            except :
                pass
            
        self.response(error,error['status'])    


    def returnErrorInfo(self,e,help=False) :
        #在错误处理中如果数据库连接是打开发，应回滚并关闭,回滚前须提交的数据必须提交
        #_version_=0.2.0
        error_code=e.code
        error_string=e.message
        try :
            if self._db_ is not None :
                self._db_.rollback()
                self.closeDB()
        except:
            pass
        eid=int(error_code)
        try:
            error=errorDic[eid]
        except:
            error=errorDic[900]
        
        # 如果存在自定义的错误消息者，替换原消息体
        if error_string :
            error['original message']=error_string
            
        if help is False :
            try :
                del error['help_document']
            except :
                pass
        else :
            traceback.print_exc()  # 将错误信息在控制台输出
            
        self.response(error,error['status'])
        
        
    def checkAppKey(self):
        if self.request.headers.get('app-key')!=config.App_Key :
            raise BaseError(601)

    def getUserToObjct(self):
        token=self.request.headers.get('Authorization')
        hu=entity.user()
        objUerInfo=hu.tokenToGet(token)
        if not objUerInfo : raise BaseError(602) #未登录授权的应用
        return objUerInfo

    def _tokenToUser(self,token):
        if token is not None  :
            myToken=Token(config.RedisConfig)
            try :
                user=myToken.getUser(token).decode('utf-8')
            except:
                raise BaseError(602) #未登录授权的应用
        else :
            raise BaseError(602) 
        return user

        
    def getTokenToUser(self):
        token=self.request.headers.get('Authorization')
        return self._tokenToUser(token)
    '''
        if token is not None  :
            myToken=Token(config.RedisConfig)
            try :
                user=myToken.getUser(token).decode('utf-8')
            except:
                raise BaseError(602) #未登录授权的应用
        else :
            raise BaseError(602) 
        return user
    '''
    

    def getRequestData(self):
        try :
            objRequestBody=ujson.loads(self.request.body.decode('utf-8'))
            #objRequestBody=json.loads(self.request.body.decode('utf-8'))
        except:
            raise BaseError(801) # 参数错误

        if objRequestBody==None :
            raise BaseError(801) # 参数错误
        else :
            return objRequestBody
        
        
    def getRequestArguments(self):
        try :
            data=self.request.arguments
            if data=={} :
                return {}
                
            #objRequestBody=json.loads(self.request.arguments.decode('utf-8'))
            objData={}
            for (k,v) in  data.items():
                objData[k]=v[0].decode('utf-8')
            return objData
        except:
            raise BaseError(801) # 参数错误

        
    def openDB(self):
        db=self.application.db
        self._db_ =db
        db.open() # open 时 autocommit=False
        return db
    
    def closeDB(self):
        if self._db_ is not None :
            self._db_.close()
        self._db_=None
    
    def resetToken(self):
        token=self.request.headers.get('Authorization')
        if token is not None  :
            try :
                myToken=Token(config.RedisConfig)
                user=myToken.getUser(token).decode('utf-8')
                myToken.saveToRedis(token,user)
                time=36000
            except:
                time=0
        else :
            time=0
        return time
    

# 操作异常处理
def operator_except(func):  
    #得到操作状态
    def gen_status(self,*args, **kwargs):  
        #result = None, None  
        try:
            self.init()
            self.db=self.openDB()
            #result = func(self,*args, **kwargs)
            func(self,*args, **kwargs)
            self.closeDB()
        except BaseError as e:
            # help=True 将显示错误信息
            self.returnErrorInfo(e,help=True)                
        #return result 
  
    return gen_status      

# 操作异常处理
def operator_argumentExcept(func):  
    #得到操作状态
    def gen_status(self,*args, **kwargs):  
        result = None, None  
        try:
            result = func(self,*args, **kwargs)
            func(self,*args, **kwargs)
        except :
            raise BaseError(801) # 参数错误
        return result 
    return gen_status      
