"""
Author: Unnar Thor Bachmann.
"""
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    """
    class User: A datamodel which represents a user.
    
    Inherits from the Base class
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250),nullable=True)


class Category(Base):
    """
    class Category: A datamodel which represents a category.
    
    Inherits from the Base class
    """
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)


class Item(Base):
    """
    class User: A datamodel which represents an item.
    
    Inherits from the Base class

    This class has function decorator to enable it
    to be serializable.
    """
    __tablename__ = 'item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    date = Column(Date,nullable=False)

    @property
    def serialize(self):
        return {
          'name': self.name,
          'description': self.description,
          'contact': self.user.email
        }    
engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
