from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
import config
from easyOAuth.userinfo import Token

import base64,time
from Crypto.Cipher import AES
from hashlib import md5

class Handler(WebRequestHandler):

    def get(self,callback_url,dataPacket):

        '''
          处理过程：
            1. 查询appId是否合法，即验证appId,appSecret,callback_url的合法性；
            2. 用户登录
            3. 如果用户未对此应用授权，则用户对该应用授权
            4. 反回临时code,即:Authcode
            5. 跳转到callback_url?authcode=$authocde
        '''
        
        try :
            #super().get(self)
            self._db_=None
            
            if  self.getRequestHeader('app-secret')!=config.App_Secret:
                raise BaseError(601) # 未经授权的第三方应用
            
            appId     = self.getRequestHeader('App-Key')
            appSecret = self.getRequestHeader('App-Secret')
        
            #1. 查询appId是否合法，即验证appId,appSecret,callback_url的合法性；
            db = self.openDB()
            
            conditions = {
                'select' : 'app_secret,callback_url'
            }
            row = db.getToObjectByPk('tbApps',conditions,appId,pk='app_key')
            
            if (len(row)==0 or  (row['app_secret']+row['callback_url'])!=(appSecret.strip()+callback_url.strip()) ):
                raise BaseError(601) # 未经授权的第三方应用

        
            #2. 解数据包
            dataPacket   = base64.standard_b64decode(dataPacket).decode()
            uidLength    = int(dataPacket[17:19])
            iv           = dataPacket[:16]
            uid          = dataPacket[-uidLength:]
            encryptedUrl = dataPacket[19:-uidLength]
        
            #3. 查询uid查询password
            conditions = {
                           'select' : 'password'
            }
            row=db.getToObjectByPk('tbUser',conditions,uid,pk='user')            

            self.closeDB()
        
            if len(row)==0:
                raise BaseError(603) # '603' - 用户名或密码错误.
        
            passwd = row['password']
        
            #4. 用passwd对surl进行AES反解码
        
            generator = AES.new(passwd, AES.MODE_CBC, iv)
        
            cryptedStr = encryptedUrl
            crypt      = base64.b64decode(cryptedStr)
            try :
                recovery = generator.decrypt(crypt).decode()
            except :
                recovery = ''
        
            url = recovery.rstrip('\0')
        
            self.set_header('Access-Control-Allow-Origin','*')
            if callback_url != url :
                self.set_header('Authorization', '')
                raise BaseError(603) # '603' - 用户名或密码错误.
                #self.set_header('status', 404)

            authcode = appId+uid+iv+url+str(int(time.time()))
            authcode = md5(authcode.encode()).hexdigest()
            # Access-Control-Expose-Headers 白名单
            self.set_header('Access-Control-Expose-Headers','Authorization')
            self.set_header('Authorization', authcode)
            
            #将一些通用参数带下
            self.response('OK')
            
            #将iAuthorization记录到Redis
            myToken = Token(config.RedisConfig)
            myToken.saveToRedis(authcode,uid)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)
