import beu
from pprint import pprint
from examples.events import (
    events, generate_event, generate_and_add_events, slow_trickle_events, now
)
from examples.notes import notes, input_session
from examples.prompts import prompts, prompt_session
from examples.links import links


def select_entries_to_tag(redthing, menu_item_format='', **find_kwargs):
    """For a given redthing, find items matching find_kwargs and make selections

    - menu_item_format: format string for each menu item
    - find_kwargs: a dict of kwargs for the redthing.find method
        - note: admin_fmt=True and include_meta=True cannot be over-written

    Once selections are made, user will be prompted to enter a tag name
    """
    find_kwargs.update(dict(admin_fmt=True, include_meta=True))
    selected = beu.make_selections(
        redthing.find(**find_kwargs),
        item_format=menu_item_format,
        wrap=False
    )

    if selected:
        pprint(selected)
        tag = beu.user_input('tag name')
        if tag:
            for item in selected:
                redthing.update(item['_id'], tag=tag)

if __name__ == '__main__':
    from pprint import pprint
    print('\nUse dir() to see what is available')
