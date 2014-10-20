from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
import config
import Service.uploadfile
from Service.uploadfile import uploadfile

'''
/group
1. 圈子
1.1 查询所有圈子                 
1.1.1 查询所有圈子信息
1.1.1.1 列出所有圈子(基础信息)         get /group?s=all&o=起始页&r=每页行数
1.1.1.2 列出最新加入的圈子(基础信息)    get /group?s=new&o=起始页&r=每页行数
1.1.1.3 按分类列出圈子(基础信息)       get /group?s=category&o=起始页&r=每页行数
1.1.1.4 列出热门圈子(基础信息)         get /group?s=hot&o=起始页&r=每页行数
1.1.1.5 模糊查询圈子(基础信息)         get /group?s=hot&o=起始页&r=每页行数
1.1.1.6 查询圈子详细信息(详细信息)      get /group/$id/info

/group
1.2 创建圈子   post /group

/group/id
1.3 管理圈子
1.3.1 设置/取消圈子管理者（权限：创建者）       put /group/$id/user   {'guid'=$guid,'role'="S|U"}
1.3.2 修改圈子信息（权限：创建者|管理者）       
1.3.2.1 修改圈子内容权限/用户加入权限/公告信息  put  /group/$gid       {'guid'=$guid,'role'="S|U"}
1.3.2.2 上传圈子头像（权限：创建者|管理者）     post /group/header
1.3.3 圈子用户管理
1.3.3.1 列出所有圈子用户（权限：创建者|管理者） get   /group/$gid/user
1.3.3.2 设置/取消用户禁言（只能看不能说）      patch /group/$gid/user  {'guid'=$guid,'st'="NO|OK"}
1.3.3.3 踢出用户                           patch /group/$gid/user  {'guid'=$guid,'st'="KO|OK"}
1.3.3.4 将用户拉入/取消黑名单                patch /group/$gid/user  {'guid'=$guid,'role'="H|U"}
1.3.4 批准/驳回用户加入圈子的申请             patch /group/$gid/user  {'st'='OK|NP','role'='U'}

/user/group
2. 用户
2.1 列出我的圈子（基础信息，按我自建的圈子+我管理的圈子+我加入的圈子（最近访问频率）排序）
2.2 加入圈子
2.3 退出圈子

/group/topics
3. 帖子
3.1 用户发帖
3.2 用户回帖


4. 管理帖子

/group/message
4. 消息



3. 主题
1. 查询圈子的详细信息
'''

class Handler(WebRequestHandler):
 
    '''
      查询圈子详细信息
      1. 圈主详细信息
      2. 圈子详细信息
    '''
    def get(self,gid): 
        try :
            super().get(self)
            
            user=self.getTokenToUser()
                
            db=self.openDB()
            #1. 圈子信息
            conditions={
                'select' : "gid,name,createTime,notice,cat,membership,totalTopic,status_code,status,isVerifyJoin,isPrivate,{{CONCAT('%s/'}},{{header) as header}}" % (config.imageConfig['groupheader']['url'])
            }                        
            groupInfo=db.getToObjectByPk('vwGroupList',conditions,gid,pk='gid')
            
            if len(groupInfo)==0 : raise BaseError(802) # 没有找到数据
            
            #2. 圈子管理者信息
            conditions={
                'select' : "id,user,role_code,role,nickname,{{CONCAT('%s/'}},{{img_header) as header}}" % (config.imageConfig['userheader']['url']),
                'where' : "role_code in ('O','S') and gid=%s" % (gid,) 
            }                        
            userInfo=db.getAllToList('vwGroupUser',conditions)
            self.closeDB()
            
            
            if len(userInfo)==0 : raise BaseError(802) # 没有找到数据
            
            groupDetailInfo={
                'Group' : groupInfo,
                'Administrator' : userInfo
            }

            self.response(groupDetailInfo)
        except BaseError as e:
            self.gotoErrorPage(e.code)


