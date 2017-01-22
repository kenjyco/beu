import beu

links = beu.RedThing('vs', 'link', unique_field='link')


if __name__ == '__main__':
    if links.size == 0:
        links.add(link='https://blah.net', domain='blah.net')
        links.add(link='https://blah.net?stuff=1&this=that', domain='blah.net')
