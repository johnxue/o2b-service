from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from Service import uploadfile


class info(WebRequestHandler):
    def get(self,id):
        try :
            super().get(self)

            db = self.openDB()            

            #1. 查询新闻详情；
            conditions = {
                'select' : 'id,title,author,source,htmlContent,createTime,CTR' 
            }
            row = db.getToObjectByPk('tbNews',conditions,id)

            self.closeDB()
            
            #2. 错误处理
            if len(row)==0 :
                raise BaseError(802) # 未找到数据

            self.response(row)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
    # 设置新闻的状态         
    def patch(self,id):
        try :
            super().patch(self)
            db = self.openDB()
            
            objData=self.getRequestData()
            user=self.getTokenToUser()
            
            try:
                st=objData['st']
            except :
                raise BaseError(801) # 参数例表错误
                
            #1. 查询新闻详情；
            updateData = {
                'status' :st ,
                'updateTime' : '{{now()}}',
                'updateUser' : user
            }
            
            db=self.openDB()
            rw=db.updateByPk('tbNews',updateData,id)
            self.closeDB()
            
            if rw<0 : raise BaseError(803) # 修改数据失败

            self.response()
            
        except BaseError as e:
            self.gotoErrorPage(e.code)            
            
    # 删除新闻         
    def delete(self,id):
        try :
            super().delete(self)
            db = self.openDB()
            
            user=self.getTokenToUser()
                
            #1. 查询新闻详情；
            updateData = {
                'status' :'UD' , #此状态应该根据用户的权限来判读 UD|AD
                'updateTime' : '{{now()}}',
                'updateUser' : user,
                'isDelete'   : 'Y'
            }
            
            db=self.openDB()
            #rw=db.update('tbNews',updateData,{'id':id,'user':user})
            rw=db.updateByPk('tbNews',updateData,id)
            self.closeDB()
            if rw<0 : raise BaseError(803) # 修改数据失败

            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)     

    # 修改新闻  
    def put(self,id):
        try:
            super().post(self)
            user=self.getTokenToUser()
            objData=self.getRequestData()
            
            try:
                try:
                    title          = objData['title']
                except : 
                    title= None
                try:
                    author         = objData['author']
                except : 
                    author=None
                try: 
                    summary        = objData['summary']
                except : 
                    summary=None
                try:
                    source         = objData['source']
                except :
                    source=None
                try:
                    content        = objData['content']
                except :
                    content=None
                try:
                    iscomment      = objData['iscomment']
                except :
                    iscomment = None
                try:
                    imgFiles       = objData['imgFiles']
                except :
                    imgFiles=None
                try:
                    removeImgFiles = objData['rImgFiles']
                except :
                    removeImgFiles=None
                try:
                    status         = objData['status']
                except :
                    status =None                   
            except :
                raise BaseError(801) # 参数错误
            
            oFileHtml={
                'content':content,
                'files':None
            }            
            
            # 将临时图像文件移动到正式文件夹中,并更替Content里的图片链接为正式连接
            oHuf=uploadfile.uploadfile()
            # preImagesAndHtml 返回 {'files' : '含正式路径的文件名','content':'含正式URL的内容'}
            oFileHtml=oHuf.preImagesAndHtml(imgFiles,content,'news') 
                   
            db=self.openDB()
            db.begin()
            
            #1.1 插入新闻
            updateData={
                'updateUser' : user,
                'updateTime' : '{{now()}}',
                'isDelete'   : 'N',
            }
            
            # 如果内容为None即不修改
            if title     is not None : updateData['title']     = title
            if author    is not None : updateData['author']    = author
            if summary   is not None : updateData['summary']   = summary
            if source    is not None : updateData['source']    = source
            if iscomment is not None : updateData['iscomment'] = iscomment
            if status    is not None : updateData['status']    = status
            if content   is not None : updateData['htmlContent'] = oFileHtml['content']

            rw=db.updateByPk('tbNews',updateData,id)
            db.close()
            if rw<0 : 
                # 插入失败后删除成功移动的文件
                oHuf.delFiles(oFileHtml['files'])
                raise BaseError(703) # SQL执行错误
            
            if removeImgFiles is not None :
                # 删除更改后移除的图形文件
                oHuf.delFiles(removeImgFiles)             
    
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code) 