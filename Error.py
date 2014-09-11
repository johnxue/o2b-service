import tornado.web
import json

class Handler(tornado.web.RequestHandler):
    def get(self,eid):
        errorDic={
            900 : {
                "code": "900",
                "status": 500,
                "message": "未被定义的错误类型",
                "help_document": "/oauth/v1.0.0/help/900"
            },
            601: {
                "code": "601",
                "status":401,
                "message": "未经过JctOAuth授权的第三方应用",
                "help_document": "/oauth/v1.0.0/help/601"
            },
            602: {
                "code": "602",
                "status":401,
                "message": "未登录授权的应用",
                "help_document": "/oauth/v1.0.0/help/602"
            },
            603: {
                "code": "603",
                "status":404,
                "message": "无法识别的用户名或密码",
                "help_document": "/oauth/v1.0.0/help/603"
            },                  
            701: {
                  "code": "701",
                  "status":500,
                  "message": "数据库连接失败",
                  "help_document": "/oauth/v1.0.0/help/701"
            },
            702: {
                  "code": "702",
                  "status":500,
                  "message":"SQL语句执行失败",
                  "help_document":"/oauth/v1.0.0/help/702"
            },
            801: {
                  "code": "801",
                  "status":400,
                  "message":"参数列表错误",
                  "help_document":"/o2b/v1.0.0/help/801"
            },
            802: {
                "code": "802",
                "status":404,
                "message":"没有找到数据",
                "help_document":"/o2b/v1.0.0/help/801"
            }
            
        }
        
        eid=int(eid)
        if eid<=0 :
            eid=900
        
        try:
            error=errorDic[eid]
        except:
            error=errorDic[900]
        
        #self.set_header('status', eid)
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Content-type','application/json;charset=utf-8');
        #self.set_header('apikey','YOUR_API_KEY_HERE')
        self.set_status(error['status'])
        self.write(json.dumps(error,ensure_ascii=False))
        
                   
