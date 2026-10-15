"""
common/conRedis.py 单元测试

全部 mock redis 模块，可在无 Redis 环境下直接运行：
    python -m pytest tests/test_conRedis.py -v
"""
import sys
import unittest
from unittest.mock import MagicMock, patch


class TestRedisConnection(unittest.TestCase):
    """RedisConnection 连接池管理"""

    def setUp(self):
        from common.con_redis import RedisConnection
        RedisConnection._pools = {}
        self.mock_redis_module = MagicMock()
        self._patcher = patch.dict(sys.modules, {'redis': self.mock_redis_module})
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_get_pool_creates_new_pool(self):
        """首次调用应为新 host 创建连接池"""
        from common.con_redis import REDIS_CONFIG, RedisConnection
        mock_pool = MagicMock()
        self.mock_redis_module.ConnectionPool.return_value = mock_pool

        pool = RedisConnection.get_pool('host1')
        self.assertIs(pool, mock_pool)
        self.mock_redis_module.ConnectionPool.assert_called_once_with(
            host='host1',
            port=REDIS_CONFIG['port'],
            decode_responses=REDIS_CONFIG['decode_responses']
        )

    def test_get_pool_reuses_existing(self):
        """同一 host 应复用已有连接池"""
        from common.con_redis import RedisConnection
        mock_pool = MagicMock()
        self.mock_redis_module.ConnectionPool.return_value = mock_pool

        RedisConnection.get_pool('host1')
        RedisConnection.get_pool('host1')
        self.mock_redis_module.ConnectionPool.assert_called_once()

    def test_get_pool_different_hosts(self):
        """不同 host 应各自创建连接池"""
        from common.con_redis import RedisConnection
        pools = [MagicMock(), MagicMock()]
        self.mock_redis_module.ConnectionPool.side_effect = pools

        p1 = RedisConnection.get_pool('host1')
        p2 = RedisConnection.get_pool('host2')
        self.assertIs(p1, pools[0])
        self.assertIs(p2, pools[1])

    def test_get_connection_returns_redis_instance(self):
        """get_connection 应返回 Redis 实例"""
        from common.con_redis import RedisConnection
        mock_pool = MagicMock()
        self.mock_redis_module.ConnectionPool.return_value = mock_pool
        mock_r = MagicMock()
        self.mock_redis_module.Redis.return_value = mock_r

        conn = RedisConnection.get_connection('host1')
        self.assertIs(conn, mock_r)
        self.mock_redis_module.Redis.assert_called_once_with(connection_pool=mock_pool)


class TestConRedis(unittest.TestCase):
    """conRedis 操作方法"""

    def setUp(self):
        from common.con_redis import RedisConnection
        RedisConnection._pools = {}
        self.mock_redis_module = MagicMock()
        self._patcher = patch.dict(sys.modules, {'redis': self.mock_redis_module})
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    @patch('common.con_redis.config')
    def test_get_conn_default_host(self, mock_config):
        """默认 host 应从 config.redis_host_46 读取"""
        from common.con_redis import conRedis
        mock_config.redis_host_46 = 'default-host'
        mock_r = MagicMock()
        self.mock_redis_module.Redis.return_value = mock_r

        conn = conRedis.get_conn()
        self.assertIs(conn, mock_r)

    def test_get_conn_custom_host(self):
        """指定 host 应直接使用"""
        from common.con_redis import conRedis
        mock_r = MagicMock()
        self.mock_redis_module.Redis.return_value = mock_r

        conn = conRedis.get_conn(host='custom-host')
        self.assertIs(conn, mock_r)

    def test_check_set_key_empty_set(self):
        """集合为空时应 sadd"""
        from common.con_redis import conRedis
        mock_r = MagicMock()
        mock_r.scard.return_value = 0
        self.mock_redis_module.Redis.return_value = mock_r

        conRedis.check_set_key('mykey', 'val1')
        mock_r.sadd.assert_called_once_with('mykey', 'val1')

    def test_check_set_key_non_empty_set(self):
        """集合非空时不应 sadd"""
        from common.con_redis import conRedis
        mock_r = MagicMock()
        mock_r.scard.return_value = 5
        self.mock_redis_module.Redis.return_value = mock_r

        conRedis.check_set_key('mykey', 'val1')
        mock_r.sadd.assert_not_called()

    def test_del_key(self):
        """del_key 应遍历 values 并 hdel"""
        from common.con_redis import conRedis
        mock_r = MagicMock()
        self.mock_redis_module.Redis.return_value = mock_r

        conRedis.del_key('hash_key', ['field1', 'field2'], ['field3'])
        self.assertEqual(mock_r.hdel.call_count, 3)
        mock_r.hdel.assert_any_call('hash_key', 'field1')
        mock_r.hdel.assert_any_call('hash_key', 'field2')
        mock_r.hdel.assert_any_call('hash_key', 'field3')

    def test_del_key_with_host(self):
        """指定 host 时应使用对应连接"""
        from common.con_redis import conRedis
        mock_r = MagicMock()
        self.mock_redis_module.Redis.return_value = mock_r

        conRedis.del_key('hash_key', ['f1'], host='other-host')
        mock_r.hdel.assert_called_once()

if __name__ == '__main__':
    unittest.main()
