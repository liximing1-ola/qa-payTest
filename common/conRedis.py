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
    def getSmebers(name):
        r = getConn()
        print(r.smember(name))


if __name__=='__main__':
    conRedis.getSmebers('Xs.WhiteList.SuperVoice.White')


