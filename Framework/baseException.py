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
                      "message": "无法获得连接",
                      "help_document": "/oauth/v1.0.0/help/702"
        },        
        703: {
              "code": "703",
              "status":500,
              "message":"SQL 语句执行失败(I)",
              "help_document":"/oauth/v1.0.0/help/703"
        },
        704: {
              "code": "704",
              "status":500,
              "message":"SQL 语句执行失败(D)",
              "help_document":"/oauth/v1.0.0/help/704"
        },
        705: {
              "code": "705",
              "status":500,
              "message":"SQL 语句执行失败(U)",
              "help_document":"/oauth/v1.0.0/help/705"
        },
        706: {
              "code": "706",
              "status":500,
              "message":"SQL 语句执行失败(S)",
              "help_document":"/oauth/v1.0.0/help/706"
        },
        707: {
              "code": "707",
              "status":500,
              "message":"SQL 语句执行失败(C)",
              "help_document":"/oauth/v1.0.0/help/707"
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


class BaseError(Exception) :
    def __init__(self,code) :
        self.code=code
    
    def __str__(self) :
        return repl(self.code)


