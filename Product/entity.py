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
        self.add('tbProductList','vwProductList', data, db, commit)
    
    def addProductDetail(self,data,db,commit=True):
        self.add('tbProductDetail','vwProductDetail', data, db, commit)

    def add(self,table,view,data,db,commit=True):
        
        #1. 将临时图像文件移动到正式文件夹中,并更替原有data里的图片文件名为正式文件名
        imgFiles=data['Image']+','+data['imagelarge']+','+data['imageBanners']+','+data['imageSmall']
        oHuf=uploadfile.uploadfile()
        # preImagesAndHtml 返回 {'files' : '含正式路径的文件名','content':'含正式URL的内容'}
        oFileHtml=oHuf.preImagesAndHtml(imgFiles,None,'product.*',('000000',data['code']))
        
        #lstImgFiles=oFileHtml['files'].split(',')
        for imgFile in oFileHtml['files'] :
            imgFile=imgFile.split('/').pop()
            if   '-banner-' in imgFile : data['imageBanners']=imgFile
            elif '-large-'  in imgFile : data['imagelarge']=imgFile
            elif '-medium-' in imgFile : data['Image']=imgFile
            elif '-small-'  in imgFile : data['imageSmall']=imgFile
        
        #2.加入到数据库
        pid=db.insert(table,data,commit)
        if pid<1 : raise BaseError(703) # SQL执行错误
        data=db.getToObjectByPk(view,{},id=pid,pk='pid')

        #2.加入到Redis
        rid=self.saveToRedis(table,pid,data)
        if rid<1 : raise BaseError(823) # redis 执行错误
        return aid

    def update(self,data,code,db):
        
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
        imgFiles=image+','+imagelarge+','+imageBanners+','+imageSmall
        if imgFiles!=',,,' :
            oHuf=uploadfile.uploadfile()
            # preImagesAndHtml 返回 {'files' : '含正式路径的文件名','content':'含正式URL的内容'}
            oFileHtml=oHuf.preImagesAndHtml(imgFiles,None,'product')         
        
            lstImgFiles=oFileHtml['files'].split(',')
            for imgFile in lstImgFiles :
                if   '-banner.' in imgFile : data['imageBanners']=imgFile
                elif '-large.'  in imgFile : data['imagelarge']=imgFile
                elif '-medium.' in imgFile : data['Image']=imgFile
                elif '-small.'  in imgFile : data['imageSmall']=imgFile        
        
        
        #2.数据更新到数据库
        rw=db.updateByPk(self.table,data,id=code)
        if rw<0 : raise BaseError(705) # SQL执行错误
        data=db.getToObjectByPk(self.view,{},id=code)
        #2.数据更新到Redis
        rw=self.saveToRedis(self.table,code,data)
        return rw

    def delete(self,code,db):  #删除数据库表及Redis里的数据
        #1.数据更新到数据库
        rw=db.updateByPk(self.table,{'isDelete':'Y','updateTime':'{{now()}}'},id=code) 
        if rw<0 : raise BaseError(705) # SQL执行错误

        #2.数据更新到Redis
        self.redisDelete(self.table,code)
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

    def getAttribute(self,db) :
        #db =dbMysql.Mysql()
        #1.1 频道；
        conditions = {
            'select' : 'description,code,maxPly',
            'order'  : 'sort'
        }
        rows_Channel = db.getAllToList('tbChannel',conditions)
        
        #1.2. 广告模式；
        conditions = {
            'select' : 'description,code',
            'order'  : 'sort'
        }        

        rows_Mode = db.getAllToList('tbAdSenseMode',conditions)            

        #1.3. 广告状态；
        rows_Status = db.getAllToList('tbAdSenseStatus',conditions)

        #1.4. 广告布局；
        rows_Layout = db.getAllToList('tbAdSenseLayout',conditions)
        #db.close()

        #2. 错误处理
        if len(rows_Channel)==0 or len(rows_Mode)==0 or len(rows_Layout)==0 or len(rows_Status)==0:
            raise BaseError(802) # 无数据

        #3. 打包成json object
        rows={
            'Channel' : rows_Channel,
            'Mode'    : rows_Mode,
            'Status'  : rows_Status,
            'Layout'  : rows_Layout
        }
        return rows

    # 在广告管理中得到广告列表（多查询模式）
    def getAllList(self,param,db):
        # 分页控制
        offset       = param['offset']
        rowcount     = param['rowcount']
        offset=offset*rowcount

        # 排序方案
        order        = param['order']
        ascOrDesc    = param['ascOrDesc']

        # 关键字查询
        searchString = param['searchString']

        # 按状态查询
        status       = param['status']

        # 按时间段查询
        startTime    = param['startTime']
        endTime      = param['endTime']

        # 过滤器查询
        filter       = param['filter']

        now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        url_path_large  = config.imageConfig['product.large']['url']
        url_path_banner = config.imageConfig['product.banner']['url']


        SELECT={
            "select" : "id,pid,name,\
                {{CONCAT('%s/'}},{{imagelarge) as imagelarge}},\
                {{CONCAT('%s/'}},{{imageBanners) as imageBanners}},\
                startTime,endTime,statuscode,status,channel,pageindex,\
                level,subindex,a_status_code,a_status,channel_sort,a_starttime,a_endtime" % (url_path_large,url_path_banner),
                                                                    "limit" : "%s,%s" % (offset,rowcount)
        }

        where={ "{{1}}" : "1" }

        if status       : where["a_status_code"]=status
        if startTime    : where["a_startTime"]="{{>='"+startTime+"'}}"
        if endTime      : where["b_endTime"]="{{<='"+endTime+"'}}"
        if searchString : where["name"]="{{ like '%"+searchString+"%'}}"

        if filter=='OPEN' :
            where["a_starttime"]="{{<='"+now+"'}}"
            where["a_endtime"]="{{>='"+now+"'}}"

        if filter=='CLOSE' : where["a_endtime"]="{{<='"+now+"'}}"

        #1. 计算符合条件的记录数
        intCount=db.count('vwAdSenseManage',where)
        if intCount==0 : raise BaseError(802) # 没有找到数据            

        orderBy=order+','+ascOrDesc
        if orderBy==','              : orderBy='STARTTIME,DESC'
        if orderBy=='STARTTIME,ASC'  : SELECT['order']="a_starttime asc,channel_sort,pageindex,level,subindex"
        if orderBy=='STARTTIME,DESC' : SELECT['order']="a_starttime desc,pageindex,level,subindex"
        if orderBy=='CHANNEL,ASC'    : SELECT['order']="channel_sort asc ,pageindex,level,subindex"
        if orderBy=='CHANNEL,DESC'   : SELECT['order']="channel_sort desc,pageindex,level,subindex"

        if where : SELECT['where']=where

        rows=db.getAllToList('vwAdSenseManage',SELECT)            

        #2. 错误处理
        if len(rows)==0: raise BaseError(802) #802 未找到数据

        #3. 打包成json object
        rows = {
            'count' : intCount,
            'list'  : rows
        }
        return rows
    
