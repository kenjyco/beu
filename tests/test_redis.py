import pytest
import beu
from redis import ConnectionError


try:
    beu.REDIS.info()
    REDIS_CONNECTED = True
except (ConnectionError, AttributeError):
    REDIS_CONNECTED = False


@pytest.mark.skipif(REDIS_CONNECTED is False, reason='Not connected to redis')
class TestRedis:
    def test_redis_test_db_is_empty(self):
        assert beu.REDIS.dbsize() == 0
