from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class Handler(WebRequestHandler):
    '''
    def formate(self,str):
        list=str.split('.')
        s=''
        for x in range(len(list)):
            list[x]='%d' % (int(list[x]))
        return '.'.join(list)
    '''

    def get(self):  # 查看API
        try :
            super().get(self)

            db   = self.openDB()            # 打开数据库
            # 分页
            node=self.get_argument("n",default='')
            fatherNode=self.get_argument("f",default='')
            
            fields=('id,node,fatherNode,URI,name,description,httpMethod,inputParameter,'
                    'inputData,outputStatus,outData,comment')
            
            conditions = {
                'select' : fields,
                'where'  : 'fatherNode="" or fatherNode is Null',
                'order'  : 'fatherNode,node'
            }            
            
            if len(fatherNode)>0 and node=='' :
                conditions['where']='fatherNode=%s' % (fatherNode)
            if len(node)>0 and len(fatherNode)>0 :
                conditions['where']='node="%s" and fatherNode="%s"' % (node,fatherNode)
                
            #1. 查询API
            rows_list = db.getAllToList('tbAPILibs',conditions)  # 查询结果以List的方式返回          
            self.closeDB()                # 关闭数据库
            if len(rows_list)==0 :        # 没有查到数据抛802异常
                raise BaseError(802)
            '''
            for x in range(len(rows_list)):
                l=list(rows_list[x])
                str=l[1]
                l[1]=self.formate(str)
                str=l[2]
                l[2]=self.formate(str)
                rows_list[x]=tuple(l)
            '''
        
            self.response(rows_list)          # 返回查询结果
        except BaseError as e:
            self.gotoErrorPage(e.code)

