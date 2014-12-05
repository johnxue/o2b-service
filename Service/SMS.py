from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from tornado.httpclient import HTTPClient
import config

def post(self):
    try :
        super().get(self)
        objUser=self.objUserInfo
        user=objUser['user']             
        objData=self.getRequestData()
        
        # 增加产品
        try :
            data={
                'mobile'        : objData['m'],
                'content'       : objData['c'],
                'type'          : objData['t']
            }
            if data['content']=='' or data['mobile']=='' :
                return objData['抛参数错误异常']
        except :
            raise BaseError(801) # 参数错误
        
        SMS=config.SMSConfig
        # 如果是验证码
        if data['type'].lower()=='verification' :
            data['content']=SMS.verification %  (data['content'],)
        
        api_url = SMS.API.url
        args    = SMS.API.arguments
        
        args['mobile']  = data['mobile']
        args['content'] = data['content']
        
        # 拼URL参数
        strArgs='?'
        for (k,v) in args.items():
            strArgs+='&' if s!='?' else  '' +('%s=%s' % (k,v))
            
        api_url+=strArgs
        
        http_client = HTTPClient()
        try:
            response = http_client.fetch(api_url)
            body=response.body
        except httpclient.HTTPError as e:
            raise BaseError(831) # 短信网关通信失败

        self.response(body)
    except BaseError as e:
        self.gotoErrorPage(e.code)



