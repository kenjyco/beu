import beu

links = beu.UniqueRedThing('vs', 'link')


if __name__ == '__main__':
    if links.size == 0:
        links.add(link='https://blah.net', domain='blah.net')
        links.add(link='https://blah.net?stuff=1&this=that', domain='blah.net')
