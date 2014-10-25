from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from Service import uploadfile

class info(WebRequestHandler):
    def get(self):
        try :
            super().get(self)
            
            offset   = int(self.get_argument("o",default='0'))
            rowcount = int(self.get_argument("r",default='1000'))
        
            db = self.openDB()
            
            #1.1 查询产品属性；
            conditions={
                'select' : 'id,title,author,source,summary,createTime,topLevel,CTR,status_code,status',
                'where'  : 'status_code="OK"',
                'limit'  : '%s,%s' % (offset,rowcount)
            }
            rows_list = db.getAllToList('vwNews',conditions)

            self.closeDB()
            
            if len(rows_list)==0:
                raise BaseError(802) # 未找到数据
            
            #3. 打包成json object
            rows = {'news' : rows_list }
            self.response(rows)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)


    # 新增新闻  
    def post(self):
        try:
            super().post(self)
            user=self.getTokenToUser()
            objData=self.getRequestData()
            
            try:
                title=objData['title']
                author = objData['author']
                summary = objData['summary']
                source = objData['source']
                content=objData['content']
                imgFiles=objData['imgFiles']
                try :
                    status =objData['status']
                except :
                    status ='NO'
                    
                try :
                    iscomment =objData['iscomment']
                except :
                    iscomment ='Y'                
                    
            except :
                raise BaseError(801) # 参数错误
            
            
            # 将临时图像文件移动到正式文件夹中,并更替Content里的图片链接为正式连接
            oHuf=uploadfile.uploadfile()
            # preImagesAndHtml 返回 {'files' : '含正式路径的文件名','content':'含正式URL的内容'}
            oFileHtml=oHuf.preImagesAndHtml(imgFiles,content,'news') 
                   
            db=self.openDB()
            db.begin()
            
            #1.1 插入新闻
            insertData={
                'createUser' : user,
                'title'      : title,
                'summary'    : summary,
                'author'     : author,
                'source'     : source,
                'htmlContent': oFileHtml['content'],
                'viewCount'  : 0,
                'replyCount' : 0,
                'createTime' : '{{now()}}',
                'isDelete'   : 'N',
                'topLevel'   : 0,
                'CTR'        : 0,
                'status'     : status,
                'iscomment'  : iscomment
            }
            newsId=db.insert('tbNews',insertData)
            db.close()
            if newsId<0 : 
                # 插入失败后删除成功移动的文件
                oHuf.delFiles(oFileHtml['files'])
                raise BaseError(703) # SQL执行错误            

            rows={
                'id' : newsId
            }
        
            self.response(rows)
            
        except BaseError as e:
            self.gotoErrorPage(e.code) 