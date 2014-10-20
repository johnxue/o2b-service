from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
#from Service import RichEditor
import re,json,os,datetime
from Framework.Base  import BaseError
import logging
import config


'''
查圈子的所有话题
# 关注
'''
class Handler(WebRequestHandler):
    # 用户查询圈子的某一个话题具体内容
    def get(self,tid=None):
        try :
            '''
            objData=self.getRequestArguments()
            try :
                # RichEditor 初始化时会调get方法
                if objData['action']=='config' :
                    re=RichEditor.RichEditorIO()
                    rspData=re.get(objData)
                    try:
                        CallBack=objData['callback']
                    except:
                        CallBack=None                    
                    self.response(rspData,angluar=False,callback=CallBack)
                    return
            except :
                pass
                   
            '''
            
            super().get(self)
            
            # 分页
            offset=int(self.get_argument("o",default=0))
            rowcount=int(self.get_argument("r",default=1000))
            offset=offset*rowcount
            user=self.getTokenToUser()
                
            db=self.openDB()
            
            #1. 查询圈子的帖子
            Select={
                'select' : 'tid,gid,user,nickname,header,topic,contents,createTime,viewCount,replyCount,isTop,isEssence,status_code,status',
                'where'  : "id=%s" % (tid,)
            }
            objTopicsContent = db.getToObjctByPk('vwGroupTopics',Select,tid)
            db.close()
            
            if len(objTopicsContent)==0 : raise BaseError(802) # 没有找到数据
            
            self.response(objTopicsContent)
        except BaseError as e:
            self.gotoErrorPage(e.code)
        

