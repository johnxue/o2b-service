from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
import config

'''

用户查询我的圈子（我的圈子=我创建的圈子+我加入的圈子）

'''

# 关注    
class Handler(WebRequestHandler):
    def get(self):
        try :
            super().get(self)
                   
            # 分页
            offset=int(self.get_argument("o",default=0))
            rowcount=int(self.get_argument("r",default=1000))
            offset=offset*rowcount
            user=self.getTokenToUser()
                
            db=self.openDB()
            
            #1. 查询用户加入的所有圈子，返回圈子gid
            conditions={
                'select' : "gid,name,cat,owner,role,membership,totalTopic,{{CONCAT('%s/'}},{{header) as header}},status_code,status" % (config.imageConfig['groupheader']['url']),
                'where'  : "user='%s'" % (user),
                'limit' : '%s,%s' % (offset,rowcount)
            }
            group_List = db.getAllToList('vwMyGroups',conditions)
            self.closeDB()
            
            #2. 错误处理
            if len(group_List)==0 :
                raise BaseError(802) # 没有找到数据                    
                
            #3. 打包成json object
            rows = {'MyJoinGroups' : group_List }
            self.response(rows)
        except BaseError as e:
            self.gotoErrorPage(e.code)
