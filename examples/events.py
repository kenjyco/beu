import beu
import random
import time
from pprint import pprint


QueryEvent = beu.RedThing('ev', 'query', index_fields=['name', 'type'], json_fields=['data'])


fake_dict_keys = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh']
try:
    with open('/usr/share/dict/words', 'r') as fp:
        text = fp.read()
        words = text.split('\n')
except FileNotFoundError:
    words = fake_dict_keys[:] * 50


def generate_event(send=True):
    event_data = {
        'name': random.choice(['google', 'yahoo', 'askjeeves', 'altavista']),
        'type': random.choice([
            'tv shows', 'sports', 'movies', 'howtos', 'tutorials', 'news', 'articles',
            'gifs', 'vids', 'politics', 'business', 'science', 'health',
        ]),
        'query': ' '.join(random.sample(words, random.randint(2, 7))),
        'description': ' '.join(random.sample(words, random.randint(20, 70))),
        'data': {
            random.choice(fake_dict_keys): [
                random.randint(50, 5000)
                for __ in range(random.randint(3, 6))
            ]
            for _ in range(random.randint(1, 4))
        },
    }

    event_id = None
    if send:
        event_id = QueryEvent.add(**event_data)

    return (event_id, event_data)


def generate_and_add_events(n):
    initial_used_memory = beu.REDIS.info()['used_memory_human']
    start = time.time()
    for _ in range(n):
        generate_event(send=True)
    end = time.time()
    final_used_memory = beu.REDIS.info()['used_memory_human']
    print('Added {} events in {} seconds'.format(n, end - start))
    print('Memory usage went from {} to {}'.format(initial_used_memory, final_used_memory))


if QueryEvent.size == 0:
    generate_and_add_events(15)

print('\nQueryEvent size:', QueryEvent.size)
print('\nTop 3 index values per index:')
pprint(QueryEvent.index_field_info(3))
