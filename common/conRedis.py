import redis
class conRedis:
    redis_config = {
        'host_46': '192.168.11.46',  # 46 redis
        'host_ali': '127.0.0.1',  # PT测试服务器 redis
        'port': 6379  # 端口
    }

    @staticmethod
    def getConn(host):
        pool = redis.ConnectionPool(host=host, port=conRedis.redis_config['port'], decode_responses=True)
        r = redis.Redis(connection_pool=pool)
        return r

    @staticmethod
    def checkSetKey(key, value):
        r = conRedis.getConn(conRedis.redis_config['host_46'])
        if r.scard(key) == 0:
            r.sadd(key, value)

    @staticmethod
    def delKey(key, *values):
        r = conRedis.getConn(conRedis.redis_config['host_ali'])
        for value in values:
            for k in value:
                r.hdel(key, k)


if __name__=='__main__':
    conRedis.checkSetKey('Xs.WhiteList.SuperVoice.White', 105002338)
    # conRedis.delKey('User.Big.Area.Id', tuple(i for i in conRedis.pt_user.values()))