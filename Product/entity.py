from Framework import dbRedis,dbMysql
from Framework.baseException import errorDic,BaseError
import msgpack,ujson,datetime
import config
from Service import uploadfile



class product(object) :

    def __init__(self) :
        self.table        = 'tbProductList'
        self.view         = 'vwProductList'
        self.rds=dbRedis.RedisCache()._connection
        self.SelectScript = "redis.call('SELECT','%s')" % (config.TableToRedisNo[self.table],)
        self.dropFunctionScript='''
            local function drop(table)
                -- 清除所有产品数据
                local list=redis.call("KEYS",table..":*")
                local i=0
                for k,v in pairs(list) do
                    redis.call("DEL",v)
                    i=i+1
                end
                return i
            end
        '''
        self.addFunctionScript='''
            local function add(table,id,value) 
                local tab = {}
                local key = table..':'..id
                -- local value=cjson.decode(ARGV[1])

                for k,v in pairs(value) do
                    -- 处理 userdata 中的 (nil) 类型
                    if  type(v)=='userdata'  then
                        v=''
                    end
                    tab[#tab + 1] = k
                    tab[#tab + 1] = v
                end

               if redis.call("EXISTS", key) ~= 1 then
                   -- 如果是新增记录，COUNT 计数器+1
                   if id=='id' then 
                      id=redis.call("INCR", table..':AUTOID')
                   end
                   redis.call("INCR", table..':COUNT')
                   -- 将id添加到list列表左侧
                   redis.call("LPUSH", table..":LIST",id)
                   key=table..':'..id
                end

                -- 新增或更改记录
                redis.call("HMSET", key,unpack(tab))

                return 1
            end
        '''
        
    def redisDelete(self,table,id):
        luaScript = self.SelectScript+'''
	    redis.call('SELECT','09')
	    local KEY=KEYS[1]..':'..ARGV[1]
	    local LIST=KEYS[1]..':LIST'
	    local COUNT=KEYS[1]..':COUNT'


	    -- 获得删除key的Value值，并以json串的形式返回
	    local value=redis.call('HGETALL',KEY)
	    if  not value[1] then
	            return 0
	    end

	    local data={}
	    for i=1,#value,2 do
	        data[value[i]] = value[i+1]
	    end

	    -- 从指定排序中删除key
	    local KEY_INDEX=KEYS[1]..':'..data['channel_code']..':'..data['pageIndex']..':'..data['level_code']..':index:ZMEM'
	    local del_index=redis.call('ZREM',KEY_INDEX,KEY)

	    -- 从指定层级中删除
	    local KEY_LEVEL=KEYS[1]..':'..data['channel_code']..':'..data['pageIndex']..':level:ZMEM'

	    if   redis.call('ZINCRBY',KEY_LEVEL,-1,data['level_code'])=='0' then 
	        redis.call('ZREM',KEY_LEVEL,data['level_code'])
	    end
            
            -- 如果某级页面中的层级全部删空，即将页面的级别号从"广告频道页面级数"中清除  tbAdSense:news:PageIndex
            if redis.call('ZCARD',KEY_LEVEL)==0 then
               redis.call('SREM',KEYS[1]..':'..data['channel_code']..':PageIndex',data['pageIndex'])
            end
            
            -- 判断是频道下是否还存在广告，如果没有则从"广告频道"集合中摘除这个频道 tbAdSense:CHANNELS
            if redis.call('SCARD',KEYS[1]..':'..data['channel_code']..':PageIndex')==0 then
               redis.call('SREM',KEYS[1]..':CHANNELS',data['channel_code'])
            end
            
            
	    -- 删除LIST tbAdSense:LIST
	    local del_list=redis.call('LREM',LIST,-1,ARGV[1])

	    -- 删除key
	    local del_key=redis.call('DEL',KEY)

	    -- 计数器-1  tbAdSense:COUNT
	    if redis.call('DECR',COUNT)==0 then 
	       redis.call('DEL',COUNT)
	    end

	    return del_index+del_list+del_key
        '''
        ls=self.rds.register_script(luaScript)
        count=ls(keys=[table],args=[id])
        return count	


    def saveToRedis(self,table,id,data):
        luaScript = self.SelectScript+self.addFunctionScript+'''
            local table = KEYS[1]
            local id    = KEYS[2]
            local value = cjson.decode(ARGV[1])
            return add(table,id,value)
        '''
        ls=self.rds.register_script(luaScript)
        rid=ls(keys=[table,id],args=[ujson.dumps(data)])
        return rid

    def addProductList(self,data,db,commit=True):
        return self.add('tbProductList','vwProductList', data, db, commit)

    def updateProductList(self,code,data,db,commit=True):
        return self.update('tbProductList','vwProductList', code,data, db, commit)
    
    def addProductDetail(self,data,db,commit=True):
        return self.add('tbProductDetail','tbProductDetail', data, db, commit)
    
    def updateProductDetail(self,id,data,db,commit=True):
        return self.update('tbProductDetail','tbProductDetail',id,data, db, commit)    

    def add(self,table,view,data,db,commit=True):
        
        #1. 将临时图像文件移动到正式文件夹中,并更替原有data里的图片文件名为正式文件名
        try :
            # 针对新增产品详细信息中的图片
            imgFiles=data['imgFiles']
        except:
            # 针对新增产品图片
            imgFiles=data['Image']+','+data['imagelarge']+','+data['imageBanners']+','+data['imageSmall']
            
        oHuf=uploadfile.uploadfile()
        # preImagesAndHtml 返回 {'files' : '含正式路径的文件名','content':'含正式URL的内容'}
        if table=='tbProductList' :
            cat='product.*'
            oFileHtml=oHuf.preImagesAndHtml(imgFiles,None,cat,('000000',data['code']))
            #lstImgFiles=oFileHtml['files'].split(',')
            for imgFile in oFileHtml['files'] :
                imgFile=imgFile.split('/').pop()
                if   '-banner.' in imgFile : data['imageBanners']=imgFile
                elif '-large.'  in imgFile : data['imagelarge']=imgFile
                elif '-medium.' in imgFile : data['Image']=imgFile
                elif '-small.'  in imgFile : data['imageSmall']=imgFile
        else :
            cat='product.detail'
            oFileHtml=oHuf.preImagesAndHtml(imgFiles,data['content'],'product.detail',('000000',data['code']))
            # 真对产品详细信息应该用html字段
            data['html']=oFileHtml['content']
            del data['content']
            del data['imgFiles']            

            
        #2.加入到数据库
        id=db.insert(table,data,commit)
        if id<1 : raise BaseError(703) # SQL执行错误
        if table=='tbProductList' :
            data=db.getToObjectByPk(view,{},id=id,pk='pid')
        else :
            # 真对详情数据
            data=db.getToObjectByPk(view,{},id)
            

        #2.加入到Redis
        rid=self.saveToRedis(table,id,data)
        if rid<1 : raise BaseError(823) # redis 执行错误
        
        #data['img_url']=config.imageConfig[cat]['url']
        # 拼图片的URL
        imageList='Image,imagelarge,imageBanners,imageSmall'.split(',')
        for imgFile in imageList :
            try :
                filename=data[imgFile]
                if   '-banner.' in filename : url=config.imageConfig['product.banner']['url']
                elif '-large.'  in filename : url=config.imageConfig['product.large']['url']
                elif '-medium.' in filename : url=config.imageConfig['product.medium']['url']
                elif '-small.'  in filename : url=config.imageConfig['product.small']['url']                
                data[imgFile]=url+'/'+filename
            except:
                pass
            
        return data

    def update(self,table,view,code,data,db,commit=True):
        try:
            image=data['Image']
        except :
            image=''
            
        try:
            imagelarge=data['imagelarge']
        except:
            imagelarge=''
            
        try:
            imageBanners=data['imageBanners']
        except:
            imageBanners=''
            
        try:
            imageSmall=data['imageSmall']
        except:
            imageSmall=''
            
        
        #1. 将临时图像文件移动到正式文件夹中,并更替原有data里的图片文件名为正式文件名
        try :
            # 针对新增产品详细信息中的图片
            imgFiles=data['imgFiles']
        except:
            # 针对新增产品图片
            imgFiles=image+\
                ((','+imagelarge) if imagelarge!='' else '')+\
                ((','+imageBanners) if imageBanners!='' else '')+\
                ((','+imageSmall) if imageSmall!='' else '')

        oHuf=uploadfile.uploadfile()        
        if imgFiles!='' :
            # preImagesAndHtml 返回 {'files' : '含正式路径的文件名','content':'含正式URL的内容'}
            if table=='tbProductList' :
                oFileHtml=oHuf.preImagesAndHtml(imgFiles,None,'product.*',('000000',data['code']))
                #lstImgFiles=oFileHtml['files'].split(',')
                for imgFile in oFileHtml['files'] :
                    imgFile=imgFile.split('/').pop()
                    if   '-banner.' in imgFile : data['imageBanners']=imgFile
                    elif '-large.'  in imgFile : data['imagelarge']=imgFile
                    elif '-medium.' in imgFile : data['Image']=imgFile
                    elif '-small.'  in imgFile : data['imageSmall']=imgFile
            else :
                oFileHtml=oHuf.preImagesAndHtml(imgFiles,data['html'],'product.detail',('000000',data['code']))
                # 真对产品详细信息应该用html字段
                data['html']=oFileHtml['content']
                #del data['content']
                #del data['imgFiles']
        
        try :
            removeImgFiles=data['rImgFiles'].split(',')
        except:
            removeImgFiles=None
        
        # 插入失败后删除成功移动的文件
        if removeImgFiles is not None :
            oHuf.delFiles(removeImgFiles)            
            

        #2.数据更新到数据库
        if table=='tbProductList' :
            rw=db.updateByPk(self.table,data,id=code,pk='code')
        else :
            keys=data.keys()
            delKeysList=['imgFiles','rImgFiles','id']
            for k in delKeysList :
                if k in keys : del data[k]
            rw=db.updateByPk('tbProductDetail',data,code)
        
        if rw<0 : raise BaseError(705) # SQL执行错误
        if table=='tbProductList' :
            data=db.getToObjectByPk(self.view,{},id=code,pk='code')
        else :
            data=db.getToObjectByPk('tbProductDetail',{},code)
            
        #2.数据更新到Redis
        # Redis这里有一个问题，多条详细信息时没有处理
        rw=self.saveToRedis(self.table,code,data)
        
        if table=='tbProductList' :
            # 拼图片的URL
            imageList='Image,imagelarge,imageBanners,imageSmall'.split(',')
            for imgFile in imageList :
                try :
                    filename=data[imgFile]
                    if   '-banner.' in filename : url=config.imageConfig['product.banner']['url']
                    elif '-large.'  in filename : url=config.imageConfig['product.large']['url']
                    elif '-medium.' in filename : url=config.imageConfig['product.medium']['url']
                    elif '-small.'  in filename : url=config.imageConfig['product.small']['url']                
                    data[imgFile]=url+'/'+filename
                except:
                    pass
        
        return data

    def updateProductStatus(self,data,code,db,commit=True):
        if data is None or len(data)==0 :
            return None
            
        #2.数据更新到数据库
        rw=db.updateByPk(self.table,data,id=code,pk='pid')
        if rw<0 : raise BaseError(705) # SQL执行错误
        data=db.getToObjectByPk(self.view,{},id=code,pk='pid')
        #2.数据更新到Redis
        rw=self.saveToRedis(self.table,code,data)
        return data



    def delete(self,ids,db):  #删除数据库表及Redis里的数据
        #1.数据更新到数据库
        rw=db.updateByPk(self.table,{'isDelete':'Y','updateTime':'{{now()}}'},'{{ in (%s)}}'%(ids),pk='pid') 
        if rw<0 : raise BaseError(705) # SQL执行错误

        #2.数据更新到Redis
        self.redisDelete(self.table,ids)
        return rw

    # 数据库中的广告视图与Redis进行同步
    def sync(self,db):
        url_path_large  = config.imageConfig['product.large']['url']
        url_path_banner = config.imageConfig['product.banner']['url']        
        SELECT={
            "select" : "code,id,pid,name,description,totalTopic,totalFollow,totalSold,totalAmount,\
                {{CONCAT('%s/'}},{{imagelarge) as imagelarge}},\
                {{CONCAT('%s/'}},{{imageBanners) as imageBanners}},\
                channel,channel_code,channel_sort,pageindex,level_code,level,subindex,\
                startTime,endTime,statuscode,status,a_status_code,a_status,a_starttime,a_endtime" % (url_path_large,url_path_banner)
        }
        rows=db.getAllToObject('vwAdSenseManage',SELECT)
        data={
            'list': rows
        }
        luaScript=self.SelectScript+self.dropFunctionScript+self.addFunctionScript+'''
           
            local tab = {}
            local value=cjson.decode(ARGV[1])
            local data=''
            for k,v in pairs(value) do
                data = v
            end
            
            -- 删除所有广告数据，这里最好改为，将最新数据增加且变更完成后，删除未做变更的数据
            drop(KEYS[1])
            
            -- 加入新数据
            local c=0
            for k,v in pairs(data) do
               if add(KEYS[1],v['id'],v)>=1 then
                  c=c+1
               end
            end
            return c
        '''
        id=''
        ls=self.rds.register_script(luaScript)
        rows=ls(keys=[self.table],args=[ujson.dumps(data)])        
        return {'count':rows}


    def getAdSense(self,channel,pangeIndex) :
        luaScript='''
            redis.call('SELECT','09')
            local mTable="tbAdSense"
            local mChannel=KEYS[1]
            local mPageIndex=KEYS[2]
            local mNowtime=ARGV[1]
            
            local function dataToJson(value)
                  local data={}
                  for i=1,#value,2 do
                      data[value[i]] = value[i+1]
                  end
                  return data
            end
            
            local s=''
            local v=0
            local tabData={}
            local mData={}
            
            local lsLevels=redis.call("ZRANGE",mTable..":"..mChannel..":"..mPageIndex..":level:ZMEM","0","-1")
            for kl,level in pairs(lsLevels) do
                  local lsDataIndex=redis.call("ZRANGE",mTable..":"..mChannel..":"..mPageIndex..":"..level..":index:ZMEM","0","-1")
                  mData={}
                  for ki,index in pairs(lsDataIndex) do
                        local data=redis.call("HGETALL",index)
                        local jsonData= dataToJson(data)
                        
                        if ( jsonData['a_status_code']=='OK' or  jsonData['a_status_code']=='OPEN' )  and  mNowtime>=jsonData['a_starttime']   and  mNowtime<=jsonData['a_endtime'] then
                                -- 结果集
                                -- code,name,description,imagelarge|imageBanners,starttime,endtime,statusCode,status,totalTopic,totalFollow,totalSold,totalAmount
                                local tmpData={}
                                tmpData[#tmpData+1]=jsonData['code']
                                tmpData[#tmpData+1]=jsonData['name']
                                tmpData[#tmpData+1]=jsonData['description']
                                if string.sub(string.upper(level),1,1)=='T' then 
                                    tmpData[#tmpData+1]=jsonData['imageBanners']
                                else
                                    tmpData[#tmpData+1]=jsonData['imagelarge']
                                end
                                tmpData[#tmpData+1]=jsonData['starttime']
                                tmpData[#tmpData+1]=jsonData['endtime']
                                tmpData[#tmpData+1]=jsonData['statuscode']
                                tmpData[#tmpData+1]=jsonData['status']
                                tmpData[#tmpData+1]=jsonData['totalTopic']
                                tmpData[#tmpData+1]=jsonData['totalFollow']
                                tmpData[#tmpData+1]=jsonData['totalSold']
                                tmpData[#tmpData+1]=jsonData['totalAmount']
                                
                                mData[#mData+1]=tmpData
                         end
                  end
                  tabData[level]=mData
            end
            
            return cmsgpack.pack(tabData)
        '''
        strNowTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ls=self.rds.register_script(luaScript)
        listMsgPack=ls(keys=[channel,pangeIndex],args=[strNowTime])
        rows = msgpack.unpackb(listMsgPack,encoding='utf-8')
        return rows

    def getManageAttribute(self,db) :
        #管理状态；
        conditions = {
            'select' : 'description,code',
            'where'  : 'role="S"',
            'order'  : 'sort'
        }
        rows_List = db.getAllToList('tbProductManageStatus',conditions)
        
        #错误处理
        if len(rows_List)==0:
            raise BaseError(802) # 无数据

        #3. 打包成json object
        rows={
            'status' : rows_List,
        }
        return rows

    # 在产品管理中得到产品列表（多查询模式）
    def getManageAllList(self,param,db):
        
        # 分页控制
        offset       = param['offset']
        rowcount     = param['rowcount']
        offset=offset*rowcount
        
        sortName     = param['sortName']
        sortValue    = param['sortValue']
        searchString = param['searchString']
        p_status     = param['p_status']
        user         = param['user']

        str_Order_by='';
        str_where='';
    
        where={ "{{1}}" : "1" }
        
        if sortName == 'sort':
            str_Order_by='`%s` desc' % (sortValue)
    
        if sortName=='attribute' and sortValue!="ALL" :
            str_where='`statusCode`="%s"' % (sortValue)
            where['statusCode']=sortValue
        
        if sortName=='category' and sortValue!="0000" :
            str_where='`categoryCode`="%s"' % (sortValue)
            where['categoryCode']=sortValue
            
            
        if p_status!='' :
            str_where='`p_status_code`="%s"' % (p_status)
            where['p_status_code']=p_status
            
    
        #sw=''
        if len(searchString)>0 :
            #for word in searchString.split(' ') :
            #    sw+='`name` like "%'+word+'%" or '
            
            #searchString='%'+searchString.replace(' ','%')+'%'
            #str_where=' %s `name` like "%s"' % (sw,searchString)
            str_where="`name` like "+"'%"+searchString+"%'"
            where["name"]="{{ like '%"+searchString+"%'}}"
            
        conditions = {
            'select' : ('pid,code,categoryCode,name,{{CONCAT("'+config.imageConfig['product.small']['url']+'/"}},{{imageSmall) as imageSmall}},'
                        'starttime,endTime,statusCode,status,totalTopic,totalFollow,totalSold,totalAmount,p_status_code,p_status,supplierName,nickname'), 
            'limit'  : '%s,%s' % (offset,rowcount)
        }
        if str_where    : conditions['where']='1 and 1 '+('and '+str_where) if len(str_where)>0 else '' +' and createUserid="%s"' % (user,)
        if str_Order_by : conditions['order']=str_Order_by
        

        #1. 查询圈子的总帖子数
        intCountComment=db.count('vmProductManageList',where)
        if intCountComment==0 : raise BaseError(802) # 没有找到数据            

        #1.1 查询产品；
        rows_list = db.getAllToList('vmProductManageList',conditions)  # 查询结果以List的方式返回  
        
        #2. 错误处理
        if (len(rows_list)==0):
            raise BaseError(802) # 未找到数据
        
        rows = {
            'count' : intCountComment,
            'rows' : rows_list
        }
        return rows
    
