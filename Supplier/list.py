from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from Supplier import entity


class Handler(WebRequestHandler):
    def get(self):
        try :
            super().get(self)
            objUser=self.objUserInfo
            user=objUser['user']
            
            s=entity.supplier()
            db=self.openDB()
            rowData=s.getSupplierCodeList(db)
            self.closeDB()
            self.response(rowData)
        except BaseError as e:
            self.gotoErrorPage(e.code)        