import beu
import random
import time
from pprint import pprint


events = beu.RedThing('ns', 'event', index_fields='name,type,tag', json_fields='data')


fake_dict_keys = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh']
try:
    with open('/usr/share/dict/words', 'r') as fp:
        text = fp.read()
        words = text.split('\n')
except FileNotFoundError:
    words = fake_dict_keys[:] * 50


def generate_event(add=True, show=False):
    """Generate a dict of event data

    - add: if True, automatically add the genarated event to 'events'
    - show: if True, pprint the generated data to the screen
    """
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
    if add:
        event_id = events.add(**event_data)
    if show:
        pprint(event_data)

    return (event_id, event_data)


def generate_and_add_events(num):
    """Generate num events, adding each event to 'events' and show metrics"""
    initial_used_memory = beu.REDIS.info()['used_memory_human']
    start = time.time()
    for _ in range(num):
        generate_event(add=True)
    end = time.time()
    final_used_memory = beu.REDIS.info()['used_memory_human']
    print('Added {} events in {} seconds'.format(num, end - start))
    print('Memory usage went from {} to {}'.format(initial_used_memory, final_used_memory))


def slow_trickle_events(sleeptime=.234, show=False, randomsleep=False):
    """Slowly generate events and add to 'events'

    - sleeptime: an exact time to sleep between generating each event
    - show: if True, pprint the generated data to the screen
    - randomsleep: if True, choose a random sleep duration between 0 and 1 sec
      after generating each event
    """
    sleeper = lambda: time.sleep(sleeptime)
    if randomsleep:
        sleeper = lambda: time.sleep(random.random())
    while True:
        try:
            generate_event(add=True, show=show)
            sleeper()
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    if events.size == 0:
        generate_and_add_events(15)

    print('\nevents size:', events.size)
    print('\nTop 3 index values per index:')
    pprint(events.index_field_info(3))
