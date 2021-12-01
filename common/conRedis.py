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
    def checkSetKey(key, value):
        r = conRedis.getConn()
        if len(r.smembers(key)) == 0:
            r.sadd(key, value)
        else:
            print('had')


if __name__=='__main__':
    conRedis.checkSetKey('Xs.WhiteList.SuperVoice.White', 105002338)


