import tornado.web
import tornado.gen
import config
from Framework.baseException import errorDic,BaseError
import decimal,datetime,json
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
    def options(self,*args,**kwargs):
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,PATCH')
        self.set_header('Access-Control-Allow-Headers', 'app-key,app-secret,authorization,Content-type,X_Requested_With')
    
    
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
        
    def __init(self,userAuth=True):
        self._db_=None
        self.checkAppKey()
        
        self.objUserInfo=None
        
        if userAuth :
            self.objUserInfo=self.getUserToObjct()
        self._now_time_ = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def head(self,*args,**kwargs):
        self.__init()        
        
    def get(self,*args,**kwargs):
        self.__init()
        
    def post(self,*args,**kwargs):
        self.__init()
        
    def delete(self,*args,**kwargs):
        self.__init()
        
    def put(self,*args,**kwargs):
        self.__init()
        
    def patch(self,*args,**kwargs):
        self.__init()        
        
    def gotoErrorPage(self,error_code,error_string='',help=False) :
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
            
        if help is False :
            try :
                del error['help_document']
            except :
                pass
            
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
            objRequestBody=json.loads(self.request.body.decode('utf-8'))
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
        db.open() # open 时 autocommit=True
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