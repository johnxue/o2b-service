from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from tornado.httpclient import HTTPClient,HTTPError

import config

class Handler(WebRequestHandler):

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
                }
                if data['content']=='' or data['mobile']=='' :
                    return objData['抛参数错误异常']
            except :
                raise BaseError(801) # 参数错误
            
            try:
                data['type']=objData['t']
            except:
                data['type']=''
                
            SMS=config.SMSConfig
            
            api_url = SMS['api']['url']
            
            # 如果是验证码,将调用已备案接口
            
            if data['type'].lower()=='verification' :
                data['content']=SMS['verification'] %  (data['content'],)
                args    = SMS['api']['arguments_Record']
            else :
                # 否则，调用未备案接口
                args    = SMS['api']['arguments']
            
            args['mobile']  = data['mobile']
            args['content'] = data['content']
            
            # 拼URL参数
            strArgs='?'
            for (k,v) in args.items():
                strArgs+=('&' if strArgs!='?' else  '') +('%s=%s' % (k,v))
                
            api_url+=strArgs
            
            http_client = HTTPClient()
            try:
                response = http_client.fetch(api_url)
                body=response.body
                if b'stat=100' not in body :
                    raise BaseError(832) # 短信网关通信失败,错误消息在body中
            except HTTPError as e:
                raise BaseError(831) # 短信网关通信失败
    
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code,'SMS API返回：'+body.decode('gbk') if e.code==832 else '')
           
