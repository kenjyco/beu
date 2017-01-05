import random
import beu
from pprint import pprint

notes = beu.RedThing('ns', 'note', index_fields='tag')


def input_session(prompt='> '):
    while True:
        text = beu.user_input(prompt)
        if text:
            notes.add(text=text)
        else:
            break


if __name__ == '__main__':
    input_session()
