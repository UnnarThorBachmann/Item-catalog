from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

categories = ['math','icelandic', 'english', 'danish','spanish','biology', 'physics']

           
items = [{'title': 'Calculus 3000', 'description': 'I have Calculus 3000 for sale. Please contact me in 848-0112.', 'category': 'math', 'id':  1},
         {'title': 'Spanish 103', 'description': 'I have Spanish 103 for sale.', 'category': 'spanish', 'id': 2},
         {'title': 'Danish 103', 'description': 'I have Danish 103 for sale.', 'category': 'danish', 'id': 3},
         {'title': 'English 103', 'description': 'I have English 103 for sale.', 'category': 'english', 'id': 4},
         {'title': 'Biology 103', 'description': 'I have Biology 103 for sale.', 'category': 'biology', 'id': 5},      
         {'title': 'Physics 103', 'description': 'I have Physics 103 for sale.', 'category': 'physics', 'id': 6},
         {'title': 'a', 'description': 'I have Physics 103 for sale.', 'category': 'physics', 'id': 7}
       ]

# Create dummy user
User1 = User(name="Sigrun", email="sigrun@fa.is")
session.add(User1)
session.commit()

User2 = User(name="Unnar", email="unnar@fa.is")
session.add(User2)
session.commit()


for category in categories:
    cat = Category(name = category)
    session.add(cat)
    session.commit()

for item in items:
    selectedCategory = session.query(Category).filter_by(name=item['category']).one()
    if item['category'] == 'spanish' or item['category'] == 'danish' or item['category'] == 'english' or item['category'] == 'icelandic':
       it = Item(name=item['title'], description = item['description'], user=User1, category = selectedCategory)
    else:
        it = Item(name=item['title'], description = item['description'], user=User2, category = selectedCategory)
    session.add(it)
    session.commit()
