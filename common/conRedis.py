"""
Redis数据库操作模块
"""
from common.Config import config


# Redis配置（host 从 Config 读取）
REDIS_CONFIG = {
    'decode_responses': True,
    'port': 6379,
}


class RedisConnection:
    """Redis连接管理器"""

    _pools = {}

    @classmethod
    def get_pool(cls, host):
        """获取连接池（单例）"""
        import redis
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
        import redis
        return redis.Redis(connection_pool=cls.get_pool(host))


class conRedis:
    """Redis操作类"""

    @staticmethod
    def getConn(host=None):
        """获取Redis连接"""
        if host is None:
            host = config.redis_host_46
        return RedisConnection.get_connection(host)

    @staticmethod
    def checkSetKey(key, value):
        """检查并设置集合key"""
        r = conRedis.getConn()
        if r.scard(key) == 0:
            r.sadd(key, value)

    @staticmethod
    def delKey(key, *values):
        """删除哈希key中的字段"""
        r = conRedis.getConn(config.redis_host_ali)
        for value in values:
            for k in value:
                r.hdel(key, k)


if __name__ == '__main__':
    conRedis.checkSetKey('Xs.WhiteList.SuperVoice.White', 100287189)
