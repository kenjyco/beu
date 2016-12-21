import random
import pytest
import beu
from redis import ConnectionError


try:
    DBSIZE = beu.REDIS.dbsize()
    REDIS_CONNECTED = True
except (ConnectionError, AttributeError):
    DBSIZE = float('inf')
    REDIS_CONNECTED = False


WORDS = ['goats', 'dogs', 'grapes', 'bananas', 'smurfs', 'snorks', 'links', 'queries']


def generate_rt1_data():
    return {
        'x': random.randint(1, 9),
        'y': random.randint(100, 999),
        'z': random.randint(10000, 99999),
    }


def generate_rt23_data():
    return {
        'a': random.choice(WORDS),
        'b': ' & '.join(random.sample(WORDS, 2)),
        'c': ', '.join(random.sample(WORDS, 3)),
        'data': {
            'x': random.randint(1, 9),
            'y': random.randint(100, 999),
            'z': random.randint(10000, 99999),
            'range': list(range(random.randint(10, 50))),
        },
    }


@pytest.fixture
def rt1():
    return beu.RedThing('test', 'rt1')


@pytest.fixture
def rt2():
    return beu.RedThing('test', 'rt2', json_fields=['data'])


@pytest.fixture
def rt3():
    return beu.RedThing('test', 'rt3', index_fields=['a'], json_fields=['data'])


@pytest.mark.skipif(DBSIZE != 0, reason='Database is not empty')
@pytest.mark.skipif(REDIS_CONNECTED is False, reason='Not connected to redis')
class TestRedThing:
    @classmethod
    def teardown_class(cls):
        _rt1 = rt1()
        _rt2 = rt2()
        _rt3 = rt3()
        _rt1.clear_keyspace()
        _rt2.clear_keyspace()
        _rt3.clear_keyspace()

    def test_add_and_get(self, rt1):
        data = generate_rt1_data()
        hash_id = rt1.add(**data)
        retrieved = rt1.get(hash_id)
        assert retrieved == data

    def test_add_and_get_some(self, rt1):
        data = generate_rt1_data()
        hash_id = rt1.add(**data)
        retrieved = rt1.get(hash_id, 'x', 'y')
        assert retrieved == {k: v for k, v in data.items() if k in ('x', 'y')}

    def test_add_and_get_one(self, rt1):
        data = generate_rt1_data()
        hash_id = rt1.add(**data)
        retrieved = rt1.get(hash_id, 'x')
        assert retrieved == {'x': data['x']}

    def test_add_and_get_with_json(self, rt2):
        data = generate_rt23_data()
        hash_id = rt2.add(**data)
        retrieved = rt2.get(hash_id)
        assert retrieved == data

    def test_add_and_get_with_index(self, rt3):
        data = generate_rt23_data()
        hash_id = rt3.add(**data)
        retrieved = rt3.get(hash_id)
        assert retrieved == data

    def test_add_multiple_and_size(self, rt3):
        for _ in range(19):
            rt3.add(**generate_rt23_data())

        assert rt3.size() == 20


    def test_base_key(self, rt1, rt2, rt3):
        rt1._base_key == 'test:rt1'
        rt2._base_key == 'test:rt2'
        rt3._base_key == 'test:rt3'

    def test_keyspace_in_use(self, rt1, rt2, rt3):
        assert rt1.size() > 0
        assert rt2.size() > 0
        assert rt3.size() > 0
