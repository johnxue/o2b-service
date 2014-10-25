import redis

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
    def __init__(self,config):  
        if not hasattr(RedisCache, 'pool'):  # 如果RedisCache中无属性'pool'，则创建
            RedisCache.create_pool(self,config)  
        self._connection = redis.Redis(connection_pool = RedisCache.pool)  
 
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
    def jsonToString(self,datas) :
        return ' '.join('%s %s' % (k,v) for k,v in datas.items())
    
    @operator_status  
    def hmset(self,key,data) :
        return 'HMSET %s '+ RedisCache.jsonToString(self, data)
    
    @operator_status  
    def save(self,table,data,id=None) :
        luaScript = '''
            local tab = {}
            local value=cjson.decode(ARGV[1])
            for key, value in pairs(value) do
                tab[#tab + 1] = key
                tab[#tab + 1] = value
            end
            if KEYS[2]==nil then
               index=redis.call("GET",KEYS[1]..':COUNT')
               key=KEYS[1]..':'..index+1
            else
               key=KEYS[1]..':'..id
            end
            
            if KEYS[2]~=nil then 
               if redis.call("HEXISTS", KEYS[1], KEYS[2]) != 1 then
                  redis.call("INCR", KEYS[1]..':COUNT')
               end
            end
            redis.call("HMSET", key,unpack(tab))
        '''
        r.eval(luaScript,2,table,id,data)  