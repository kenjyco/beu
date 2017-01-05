__all__ = ['events', 'links', 'notes', 'prompts']

import examples.events as events
import examples.links as links
import examples.notes as notes
import examples.prompts as prompts

if __name__ == '__main__':
    print('\nLoaded the following examples: {}'.format(', '.join(__all__)))
