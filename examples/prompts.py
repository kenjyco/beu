import random
import beu
from pprint import pprint

prompts = beu.RedThing('ns', 'prompt', index_fields='p,tag')
prompt_strings = [
    'basketball player', 'super hero', 'favorite food', 'video game',
    'movie', 'tv show'
]


def prompt_session(prompt_string=None, ch='> '):
    prompt_string = prompt_string or random.choice(prompt_strings)
    while True:
        text = beu.user_input(prompt_string + ch)
        if text:
            prompts.add(text=text, p=prompt_string)
        else:
            break


if __name__ == '__main__':
    print('\nPress <Enter> twice to stop prompting.\n')
    prompt_session()
