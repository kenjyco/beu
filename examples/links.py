import beu

link_collection = beu.UniqueRedThing('vs', 'link')


if __name__ == '__main__':
    if link_collection.size == 0:
        link_collection.add(link='https://blah.net', domain='blah.net')
        link_collection.add(link='https://blah.net?stuff=1&this=that', domain='blah.net')
