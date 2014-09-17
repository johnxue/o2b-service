import tornado.web
import base64,time
from dbMysql import dbMysql
from Crypto.Cipher import AES
from hashlib import md5
import config
from easyOAuth.userinfo import Token

class Handler(tornado.web.RequestHandler):

    def gotoErrorPage(self,error_code) :
        self.set_header('Access-Control-Allow-Origin','*')
        self.redirect('/o2b/v1.0.0/error/%d'% error_code )
        
    def options(self,userid,abc):
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Headers', 'app-key,app-secret')
    
    def get(self,callback_url,dataPacket):
        #self.write("Hello, world * "+callback_url+'['+dataPacket)

        '''
          处理过程：
            1. 查询appId是否合法，即验证appId,appSecret,callback_url的合法性；
            2. 用户登录
            3. 如果用户未对此应用授权，则用户对该应用授权
            4. 反回临时code,即:Authcode
            5. 跳转到callback_url?authcode=$authocde
        '''
        
        if ((self.request.headers.get('app-key')!=config.App_Key) or (self.request.headers.get('app-secret')!=config.App_Secret)):
            # 601 : 未经授权的第三方应用
            self.gotoErrorPage(601)
            return
        
        appId    = self.request.headers.get('App-Key')
        appSecret= self.request.headers.get('App-Secret')
        
        try :
            db=dbMysql(config.dbConfig)
        except :
            # 701 : 数据库连接失败
            self.gotoErrorPage(701)
            return
        
        
        #1. 查询appId是否合法，即验证appId,appSecret,callback_url的合法性；
        try :
            sqlSelect='select app_secret,callback_url from tbApps where app_key="%s"' % appId
            row=db.getToObject(sqlSelect)
        except :
             # 702 : SQL查询失败
            db.close()
            self.gotoErrorPage(702)
            return
        
        if (row is None) or ( (row['app_secret']+row['callback_url'])!=(appSecret.strip()+callback_url.strip()) ):
            # '601' - 未被授权的应用
            db.close()
            self.gotoErrorPage(601)
            return
        
        #3. 解数据包
        dataPacket=base64.standard_b64decode(dataPacket).decode()
        uidLength=int(dataPacket[17:19])
        iv=dataPacket[:16]
        uid=dataPacket[-uidLength:]
        encryptedUrl=dataPacket[19:-uidLength]
        
        #4. 查询uid查询password
        try :
            sqlSelect='select password from tbUser where user="%s"' % uid
            row=db.getToObject(sqlSelect)
        except :
             # 702 : SQL查询失败
            db.close()
            self.gotoErrorPage(702)
            return
        
        db.close()
        
        if (row is None):
            # '602' - 用户名或密码错误.
            self.gotoErrorPage(602)
            return
        
        passwd=row['password']
        
        #5. 用passwd对surl进行AES反解码
        
        generator = AES.new(passwd, AES.MODE_CBC, iv)
        
        cryptedStr=encryptedUrl
        crypt=base64.b64decode(cryptedStr)
        try :
            recovery = generator.decrypt(crypt).decode()
        except :
            recovery=''
        
        url=recovery.rstrip('\0')
        
        self.set_header('Access-Control-Allow-Origin','*')
        if callback_url!=url :
            self.set_header('Authorization', '')
            self.set_header('status', 404)
            return 

        authcode=appId+uid+iv+url+str(int(time.time()))
        authcode=md5(authcode.encode()).hexdigest()
        # Access-Control-Expose-Headers 白名单
        self.set_header('Access-Control-Expose-Headers','Authorization')
        #self.set_header('Authorization', 'Basic '+authcode)
        self.set_header('Authorization', authcode)
        #将一些通用参数带下
        self.write('OK')
        #将iAuthorization记录到Redis
        myToken=Token(config.redisConfig)
        myToken.saveToRedis(authcode,uid)
        
        #r=redis.Redis(host='localhost',port=6379,db=12,password='jct2014redis')
        #pr=r.pipeline()
        #pr.set(authcode,uid)
        #pr.expire(authcode,1800)
        #pr.execute()


