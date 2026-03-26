"""
Redis数据库操作模块
"""
import redis


# Redis配置
REDIS_CONFIG = {
    'host_46': '192.168.11.46',
    'host_ali': '127.0.0.1',
    'port': 6379,
    'decode_responses': True,
}


class RedisConnection:
    """Redis连接管理器"""

    _pools = {}

    @classmethod
    def get_pool(cls, host):
        """获取连接池（单例）"""
        if host not in cls._pools:
            cls._pools[host] = redis.ConnectionPool(
                host=host,
                port=REDIS_CONFIG['port'],
                decode_responses=REDIS_CONFIG['decode_responses']
            )
        return cls._pools[host]

    @classmethod
    def get_connection(cls, host):
        """获取Redis连接"""
        return redis.Redis(connection_pool=cls.get_pool(host))


class conRedis:
    """Redis操作类"""

    @staticmethod
    def getConn(host):
        """获取Redis连接"""
        return RedisConnection.get_connection(host)

    @staticmethod
    def checkSetKey(key, value):
        """检查并设置集合key"""
        r = conRedis.getConn(REDIS_CONFIG['host_46'])
        if r.scard(key) == 0:
            r.sadd(key, value)

    @staticmethod
    def delKey(key, *values):
        """删除哈希key中的字段"""
        r = conRedis.getConn(REDIS_CONFIG['host_ali'])
        for value in values:
            for k in value:
                r.hdel(key, k)


if __name__ == '__main__':
    conRedis.checkSetKey('Xs.WhiteList.SuperVoice.White', 100287189)
