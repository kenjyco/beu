import random
import beu
from pprint import pprint

notes = beu.RedThing('ns', 'note', index_fields='tag')


def input_session(prompt_string='', ch='> '):
    """Continue prompting for input until none is given

    - prompt_string: string to display when asking for input
    - ch: string appended to the main prompt_string
    """
    while True:
        text = beu.user_input(prompt_string, ch)
        if text:
            notes.add(text=text)
        else:
            break


def hand_pick_from(**find_kwargs):
    find_kwargs.update(dict(
        admin_fmt=True, all_fields=True, include_meta=True
    ))
    selected = beu.make_selections(
        notes.find(**find_kwargs),
        item_format='{_ts} -> {text}',
        wrap=False
    )
    import pdb; pdb.set_trace()


if __name__ == '__main__':
    input_session()
