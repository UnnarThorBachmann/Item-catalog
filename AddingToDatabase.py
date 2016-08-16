"""
Author: Unnar Thor Bachmann.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User
import random
from datetime import date

# Connecting to the database.
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Allowed categories
categories = ['math',
              'english',
              'humanities',
              'science',
              'sports',
              'foreign languages',
              'social science']

# Items initally in the database.      
items = [{'title': 'Calculus 3000',
          'description': 'I have Calculus 3000 for sale.',
          'category': 'math',
          'id':
          1},
         {'title': 'Spanish 103',
          'description': 'I have Spanish 103 for sale.',
          'category': 'foreign languages',
          'id': 2},
         {'title': 'Sports 103',
          'description': 'I have Sports 103 for sale. I am listening to offers.',
          'category': 'sports',
          'id': 3},
         {'title': 'English 103',
          'description': 'I have English 103 for sale. Price 40 dollars.',
          'category': 'english',
          'id': 4},
         {'title': 'The Secret Diary of Socrates',
          'description': 'The first year textbook. Price 30 dollars',
          'category': 'humanities',
          'id': 5},      
         {'title': 'Physics 103',
          'description': 'I have Physics 103 for sale. Price 40 dollars.',
          'category': 'science',
          'id': 6},
         {'title': 'Theories of Karl Marx',
          'description': 'I am listening to offers. Telephone 848-0112.',
          'category': 'social science',
          'id': 7}
       ]

# Create two dummy users with the same methods
# as we did in the multi users blogg project.

username = "Laura"
email = "laura@fa.is"
User1 = User(name=username,
            email = email)

session.add(User1)
session.commit()

username = "Adam"
email = "adam@fa.is"
User2 = User(name=username,
            email = email)

session.add(User2)
session.commit()

# Adding the categories to the database.
for category in categories:
    cat = Category(name = category)
    session.add(cat)
    session.commit()

# Adding the items to the database.
for item in items:
    selectedCategory = session.query(Category).filter_by(name=item['category']).one()
    randInt = random.randint(0,1)
    if randInt == 0:
       it = Item(name=item['title'],
                 description = item['description'],
                 user=User1, category =
                 selectedCategory,
                 date=date(random.randint(2008,2016),
                           random.randint(1,12),
                           random.randint(1,28)))
                 
    else:
        it = Item(name=item['title'],
                  description = item['description'],
                  user=User2,
                  category = selectedCategory,
                  date=date(random.randint(2008,2016),
                           random.randint(1,12),
                           random.randint(1,28)))
    session.add(it)
    session.commit()
