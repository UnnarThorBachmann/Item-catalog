from flask import Flask,  render_template, redirect, url_for
app = Flask(__name__)
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

@app.route('/')
@app.route('/catalog')
def showCatalog():
    filterCategory = 'none'
    categories = session.query(Category).all()
    items = session.query(Item).all()
    return render_template('catalog.html', categories=categories,items=items, filterCategoryName = filterCategoryName)

@app.route('/catalog/<categoryName>/items')
def showSelectedCategory(categoryName):
    filterCategory = session.query(Category).filter_by(name=categoryName).one()
    items = session.query(Item).filter_by(category=filterCategory).all()
    categories = session.query(Category)
    return render_template('catalog.html', categories=categories,items=items, filterCategoryName = categoryName, n = len(items))

@app.route('/catalog/<categoryName>/<itemName>')
def showItemFromCategory(itemName,categoryName):
    filterItem = session.query(Item).filter_by(name=itemName).first()
    if filterItem is not None and filterItem.category == categoryName:
       return render_template('item.html', item=filterItem)
    else:
        return 'File not found, 404'
 

@app.route('/catalog/<itemName>/edit',methods = ['POST','GET'])
def editItem(itemTitle):
    if request.method == 'GET':
       filterItem = session.query(Item).filter_by(name=itemName).first()
       if filterItem is not None:
          categories = session.query(Category)
          return render_template('edit.html', item=itemSelected,categories=categories)
       else:
           return 'File not found, 404'
    
        

@app.route('/catalog/<itemTitle>/delete')
def deleteItem(itemTitle):
    itemSelected = None
    for item in items:
        if itemTitle == item['title']:
           itemSelected = item
           return render_template('delete.html')
        
@app.route('/catalog.json')
def jsonItem():
    return str(categories)

@app.route('/login')
def showLogin():
    return render_template('login.html')

if __name__ == '__main__':
   app.debug = True
   app.run(host = '0.0.0.0', port = 5000)
