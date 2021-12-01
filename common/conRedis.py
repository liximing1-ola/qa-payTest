# coding=utf-8
import redis

class conRedis:

    @staticmethod
    def getConn():
        redis_config = {
            'host': '127.0.0.1',
            'port': 6379
        }
        pool = redis.ConnectionPool(host=redis_config['host'], port=redis_config['port'], decode_responses=True)
        r = redis.Redis(connection_pool=pool)
        return r

    @staticmethod
    def checkSetKey(key):
        r = conRedis.getConn()
        print(r.smembers(key))
        print(type(r.smembers(key)))


if __name__=='__main__':
    conRedis.checkSetKey('Xs.WhiteList.SuperVoice.White')


