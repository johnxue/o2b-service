from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
import config

'''
圈子公共服务
1. 得到某圈子的用户权限，如该用户不在此圈中返为None
2. 设置/去除管理员权限
3. 踢除用户
4. 对用户禁言
5. 审核验证用户
'''
class GroupInfo:
    
    # 检查是用户是否是
    def getGroupRole(self,gid,user):
        SELECT={
            'select' : 'role',
            'where' : 'user="%s" and gid=%s' % (user,gid),
            'limit' : '1'
        }
        db=self.openDB()
        user_role=db.getAllToObject('vwGroupUser',SELECT)
        self.closeDB()
        if len(user_role)==0 :
            return None
        return user_role['role']
    