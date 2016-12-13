import beu
import random


QueryEvent = beu.RedThing('ev', 'query', index_fields=['name'], json_fields=['data'])


fake_dict_keys = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh']
try:
    with open('/usr/share/dict/words', 'r') as fp:
        text = fp.read()
        words = text.split('\n')
except FileNotFoundError:
    words = fake_dict_keys[:]


def generate_event(send=True):
    event_data = {
        'name': random.choice(['google', 'yahoo', 'askjeeves']),
        'query': ' '.join(random.sample(words, random.randint(2, 7))),
        'data': {
            random.choice(fake_dict_keys): random.randint(50, 5000)
            for _ in range(random.randint(1, 4))
        },
    }

    event_id = None
    if send:
        event_id = QueryEvent.add(**event_data)

    return (event_id, event_data)
