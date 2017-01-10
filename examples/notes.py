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


if __name__ == '__main__':
    input_session()
