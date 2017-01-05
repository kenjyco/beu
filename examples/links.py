import beu

link_collection = beu.UniqueRedThing('vs', 'link')
link_collection.add(link='https://blah.net', domain='blah.net')
link_collection.add(link='https://blah.net?stuff=1&this=that', domain='blah.net')
