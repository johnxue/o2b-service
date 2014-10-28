import redis
import msgpack
import config


'''
Mysql 主
Redis 从
 基本结构应该是：
    1. 存入MySQL-- > 复制到Redis
    2. 查询Redis -- > 查询MySQL
'''
def operator_status(func):  
    #得到操作状态
    def gen_status(*args, **kwargs):  
        error, result = None, None  
        try:  
            result = func(*args, **kwargs)  
        except Exception as e:  
            error = str(e)  
  
        return {'result': result, 'error':  error}  
  
    return gen_status  
  
class RedisCache(object):  
    def __init__(self):
        if not hasattr(RedisCache, 'pool'):  # 如果RedisCache中无属性'pool'，则创建
            RedisCache.create_pool(self,config.RedisConfig)
        self._connection = redis.Redis(connection_pool = RedisCache.pool)  
        
    '''
    @staticmethod  
    def open(self):
        if not hasattr(RedisCache, 'pool'):  # 如果RedisCache中无属性'pool'，则创建
            RedisCache.create_pool(self,self.config)
        self._connection = redis.Redis(connection_pool = RedisCache.pool)  
        return self._connection
    '''       

    @staticmethod  
    def create_pool(self,config):  
        RedisCache.pool = redis.ConnectionPool(**config)  
 
    @operator_status  
    def set_data(self, key, value):  
        #设置KV数据(key, value) 
        return self._connection.set(key, value)  
 
    @operator_status  
    def get_data(self, key):  
        #根据key得到value
        return self._connection.get(key)  
 
    @operator_status  
    def del_data(self, key):  
        #删除key
        return self._connection.delete(key) 

    @operator_status  
    def jsonToString(self,jsonData) :
        return ' '.join('%s %s' % (k,v) for k,v in jsonData.items())
    
    @operator_status  
    def hmset(self,key,data) :
        return 'HMSET %s '+ RedisCache.jsonToString(self, data)
    
    @operator_status
    def save_list(self,table,data,id=None,RL='R'):
        if id is None : id = ''
        luaScript_Save = '''
            if #ARGV[1]==0 or ARGV[1]='{}' then
               return 0
            end
            
            local key
            local data=ARGV[1]
            if KEYS[2]=='' then
               key=KEYS[1]
            else
               key = KEYS[1]..':'..KEYS[2]
            end
            if KEYS[3]=='R' then 
               redis.call("rpush", key,data)
            else 
               redis.call("lpush", key,data)
            end
            return 1
        '''
        ls=self._connection.register_script(luaScript_Save)
        return ls(keys=[table,id,RL],args=[data])
    
        
    @operator_status  
    def save(self,table,data,id=None) :
        luaScript_Save = '''
            local tab = {}
            local key = KEYS[1]..':'..KEYS[2]
            local id  = 1  -- 如果是修改记录，则返回的值为1

            local value=cjson.decode(ARGV[1])
            for k, v in pairs(value) do
                tab[#tab + 1] = k
                tab[#tab + 1] = v
            end
            
            if redis.call("EXISTS", key) ~= 1 then
               -- 如果是新增记录，COUNT 计数器+1
               id=redis.call("INCR", KEYS[1]..':COUNT')
               -- 将id添加到list列表尾部
               redis.call("RPUS", KEYS[1]..":LIST",id)
               if KEYS[2]=='id' then
                  key=KEYS[1]..':'..id
               end
            end

            -- 新增或更改记录
            redis.call("HMSET", key,unpack(tab))
            return id

        '''
        #self._connection.eval(luaScript,2,table,id,data)
        ls=self._connection.register_script(luaScript_Save)
        return ls(keys=[table,id],args=[data])
        
    @operator_status  
    def delete(self,table,id) :
        luaScript_Del = '''
            local key = KEYS[1]..':'..KEYS[2]

            local rw=redis.call("DEL",key)
            if rw==1 then
               redis.call("DECR",KEYS[1]..':COUNT')
               -- 总是从右边向左边查找
               redis.call("LREM",KEYS[1]..':LIST',-1,KEYS[2])
            end

            return rw
        '''
        #self._connection.eval(luaScript,2,table,id,data)
        ls=self._connection.register_script(luaScript_Del)
        return ls(keys=[table,id])


    @operator_status  
    def get(self,table,id) :
        luaScript_Del = '''
            local key = KEYS[1]..':'..KEYS[2]
            local r=redis.call("HGETALL",key)
            local t={}
            for i=1,#r,2 do 
                t[r[i]]=r[i+1]
            end
            return cmsgpack.pack(t)
        '''
        ls=self._connection.register_script(luaScript_Del)
        info=msgpack.unpackb(ls(keys=[table,id]),encoding='utf-8')
        return info