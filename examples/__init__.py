from examples.events import (
    QueryEvent, generate_event, generate_and_add_events, slow_trickle_events, now
)
from examples.notes import notes, input_session, hand_pick_from
from examples.links import link_collection
from examples.prompts import prompts, prompt_session

if __name__ == '__main__':
    import beu
    from pprint import pprint
    print('\nUse dir() to see what is available')
