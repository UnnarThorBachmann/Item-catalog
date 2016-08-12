"""
Author: Unnar Thor Bachmann.
"""

"""
This module uses flask and sqlalchemy to make a multi user CRUD page.
Each user can create and update his item if logged in. Each item is in a different category. 
"""
from flask import Flask,request, render_template, redirect
from flask import url_for, make_response, session as login_session
from flask import flash, jsonify
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User
from datetime import date
import json
import random
import string


# These helper functions were created in the multi user blog project.
from helper_functions import valid_username, valid_password, valid_email, make_salt, make_pw_hash

#Creating the app flask.
app = Flask(__name__)
app.secret_key = '94A4QZCD4Q91YWGQ6PTH12YHTBELYR4A'


#Connecting with a database.
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog')
def showCatalog():
    """
    This method renders the main page of the app. 
    """
    filterCategoryName = 'none'
    items = session.query(Item).order_by(desc(Item.date)).all()
    for item in items:
        print item.date

    queryCategory = session.query(Category)
    # I am going to display at maximum as many items as there are categories.
    n = queryCategory.count()
    
    # Rendering the page differently when user is logged in.
    if login_session.has_key('username'):
       addButtonHide = ''
       logoutButtonHide = ''
       loginButtonHide = 'hidden'
       queryItems = session.query(Item).filter_by(user_id=login_session['id'])
       items = queryItems.order_by(desc(Item.date)).slice(0,n).all()
    else:
        addButtonHide = 'hidden'
        logoutButtonHide = 'hidden'
        loginButtonHide = ''
        items = session.query(Item).order_by(desc(Item.date)).slice(0,n).all()

    #items = items[:n]
    categories = queryCategory.all()
    return render_template('catalog.html',
                           categories=categories,
                           items=items,
                           filterCategoryName = filterCategoryName,
                           addButtonHide= addButtonHide,
                           logoutButtonHide=logoutButtonHide,
                           loginButtonHide=loginButtonHide)

@app.route('/catalog/<categoryName>/items')
def showCategory(categoryName):
    """
    This page render the main page of the app were only items
    in give category are rendered.
    """
    queryCategory = session.query(Category)
    # I am going to display at maximum as many items as there are categories.
    n = queryCategory.count()
    category = queryCategory.filter_by(name=categoryName).first()
    
    filterCategory=categoryName
    

    # Rendering the page differently when user is logged in.
    if login_session.has_key('username'):
       addButtonHide = ''
       logoutButtonHide = ''
       loginButtonHide = 'hidden'
       category = queryCategory.filter_by(name=categoryName).first()
       queryItems = session.query(Item).filter(Item.user_id==login_session['id'])
       items = queryItems.filter(Item.category==category).slice(0,n).all()
    else:
        addButtonHide = 'hidden'
        logoutButtonHide = 'hidden'
        loginButtonHide = ''
        items = session.query(Item).filter_by(category=category).slice(0,n).all()
        
    categories = queryCategory.all()
    return render_template('catalog.html',
                           categories=categories,
                           items=items,
                           filterCategoryName = categoryName,
                           addButtonHide= addButtonHide,
                           logoutButtonHide=logoutButtonHide,
                           loginButtonHide=loginButtonHide,
                           n = len(items))

@app.route('/catalog/<categoryName>/<itemName>')
def showItem(itemName,categoryName):
    """
    Renders a page for a given item.
    """
    
    # Rendering the page differently when user is logged in.
    if login_session.has_key('username'):
       logoutButtonHide = ''
       loginButtonHide = 'hidden'
       editDeleteHide = ''
    else:
        logoutButtonHide = 'hidden'
        loginButtonHide = ''
        editDeleteHide = 'hidden'
    
    filterItem = session.query(Item).filter_by(name=itemName).first()
    email = filterItem.user.email

    # Renders the page only if no user is logged in or if current user
    # has an id matching the user_id of the item
    if filterItem is not None and filterItem.category.name == categoryName\
       and (not login_session.has_key('id') or login_session['id'] == filterItem.user_id):
       return render_template('item.html',
                              item=filterItem,
                              logoutButtonHide=logoutButtonHide,
                              loginButtonHide=loginButtonHide,
                              editDeleteHide=editDeleteHide,
                              email=email)
    else:
        response = make_response(json.dumps("File not found"), 404)
        response.headers['Content-Type'] = 'application/json'
        return response
 

@app.route('/catalog/<itemName>/edit', methods = ['POST','GET'])
def editItem(itemName):
    """
    This function is for editing an item.

    Args: Name of the item. 

    GET: Renders a form for editing the name, description and category.
    
    POST: Updates the item in the database and redirects to the main page.
    """

    if request.method == 'GET':
       #The GET method.
        
       # The page is only rendered if there is a user logged in.
       if login_session.has_key('username'):
          logoutButtonHide = ''
          loginButtonHide = 'hidden'
          categories = session.query(Category).all()
          # Splitting the query do to length. The item is filtered
          # with respect to name and the id of the current user.
          query =  session.query(Item).filter_by(name=itemName)
          filterItem = query.filter_by(user_id = int(login_session['id'])).first()

          #If the item does not exist the page is not rendered.
          if filterItem is not None:          
             categories = session.query(Category)
             #The item id is put into the loggin session for editing.
             login_session['itemId'] = int(filterItem.id)
             return render_template('edit.html',
                                    item=filterItem,
                                    categories=categories,
                                    logoutButtonHide=logoutButtonHide,
                                    loginButtonHide=loginButtonHide)
          else:
              response = make_response(json.dumps("File not found"), 404)
              response.headers['Content-Type'] = 'application/json'
              return response
       else:
           return redirect(url_for('showLogIn',
                           signup='false'))
       
    else:
        #The POST method.
        
        #The form is read.
        itemName = request.form['name']
        itemDescription = request.form['description']   
        itemCategory = session.query(Category).filter_by(name=request.form['category']).first()
        #Item has to be selected by id. The name could have changed.
        itemEdited = session.query(Item).filter_by(id=login_session['itemId']).first()
        
        # Returns error if the item does not exist or if current user is not
        # the owner of it.
        if itemEdited is None or itemEdited.user_id != login_session['id']:
           response = make_response(json.dumps("File not found"), 404)
           response.headers['Content-Type'] = 'application/json'
           return response

        # Item is updated
        itemEdited.name=itemName
        itemEdited.description = itemDescription
        itemEdited.category = itemCategory
        itemEdited.category_id = itemCategory.id
        itemEdited.user = session.query(User).filter_by(name=login_session['username']).first()
        itemEdited.user_id = int(login_session['id'])
        itemEdited.date = date.today()
        
        # The database is updated.
        session.add(itemEdited)
        session.commit()
        return redirect(url_for('showCatalog'))
        
@app.route('/catalog/new', methods = ['POST','GET'])
def newItem():
    """
    This function is for createing a new item.

    GET: Renders the form for making a new item.
    POST: Creates a new item.
    """
    
    if request.method == 'GET':
       # The GET method.
       
       # If user is not logged in the he is redirected
       # to the log in page.
       if login_session.has_key('username'):
          logoutButtonHide = ''
          loginButtonHide = 'hidden'
          categories = session.query(Category).all()
          return render_template('newItem.html',
                                 categories = categories,
                                 logoutButtonHide=logoutButtonHide,
                                 loginButtonHide=loginButtonHide)
       else:
           redirect(url_for('showLogIn',
                            signup='false'))
            
       
    else:
        #The POST method.
        
        #Reading the form.
        itemName = request.form['name']
        itemDescription = request.form['description']
        itemCategory = request.form['category']

        # Finding the user and the category of the item from database.
        user = session.query(User).filter_by(name=login_session['username']).first()
        category = session.query(Category).filter_by(name=itemCategory).first()

        #Creating the user
        newItem = Item(name=itemName,
                       description = itemDescription,
                       user_id = int(login_session['id']),
                       user = user,
                       category = category,
                       category_id = category.id,
                       date=date.today())
        session.add(newItem)
        session.commit()
        return redirect(url_for('showCatalog'))          
        

@app.route('/catalog/<itemName>/delete', methods = ['POST','GET'])
def deleteItem(itemName):
    """
    A method to delete an item.

    Args: The name of the item.

    POST: Deletes the item.
    
    GET: Renders the form (consisting of a single button). On pressing the
         button the item is deleted.
    """
    

    if request.method == 'GET':
       # The GET method
       itemToDelete = session.query(Item).filter_by(name=itemName).first()

       # Renders the page the user is logged on and if the user has
       # the same id as the item to delete.
       
       if login_session.has_key('username')\
          and login_session["id"] == itemToDelete.user_id:
           
          logoutButtonHide = ''
          loginButtonHide = 'hidden'
          
          login_session['itemId'] = int(itemToDelete.id)
       
          return render_template('delete.html',
                                 logoutButtonHide=logoutButtonHide,
                                 loginButtonHide=loginButtonHide,
                                 itemName=itemToDelete.name)
       else:
           # Otherwise redirect to the log in page.
           return redirect(url_for('showLogIn',
                                   signup='false'))
       
    else:
        # The POST method.
        itemToDelete = session.query(Item).filter_by(id=login_session['itemId']).first()
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showCatalog'))
           
        
@app.route('/login')
def showLogIn():
    """
    Renders the log in page.
    The log in page contains three forms.
    
    Two forms to for the local log system.
    One for a facebook log in. 
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))

    # The log in session keeps a state variable to prevent forgery as in class.
    login_session['state'] = state
    loginButtonHide = 'hidden'
    logoutButtonHide = 'hidden'
    
    response = make_response(render_template('login.html',
                                             loginButtonHide=loginButtonHide,
                                             logoutButtonHide=logoutButtonHide,
                                             signup='false'))
    
    # The state is written to a cookie.
    response.set_cookie('state', state)
    return response
    
@app.route('/loginuser', methods = ['POST'])
def loginUser():
    """
    This method reads the log in form and renders appropirate page.
    """
    
    # From class. In case of the state variable in the cookie
    # is not the same as in the login_session.
    if login_session['state'] != request.cookies.get('state'):
       response = make_response(json.dumps('Invalid state parameter.'), 401)
       response.headers['Content-Type'] = 'application/json'
       return response

    # Read the log in form.
    username = request.form['logInName']
    password  = request.form['logInPassword']
    
    # Validates the username and password
    valid_usr = valid_username(username)
    valid_pw = valid_username(password)

    # If the username and password are not valid
    # the log in page is rerendered with a flash message.
    if (valid_usr is None or valid_pw is None):
        flash(username,'login')
        flash('Invalid username or password','login')
        return redirect(url_for('showLogIn',
                                signup='false'))
    else:
        # If the user exists then render the
        # catalog page. Else redirect to the login page with
        # appropirate flash messages.
        
        user = session.query(User).filter_by(name=username).first()
        if user is None or user.password is None or not valid_password(username,
                                                                 password,
                                                                 user.password):
           flash(username,'login')
           flash('Invalid login','login')
           return redirect(url_for('showLogIn',
                                   signup='false'))
        else:
            login_session['username'] = username
            login_session['email'] = user.email
            login_session['id'] = int(user.id)
            flash('You are now logged in as %s' % username,'success')
            return redirect(url_for('showCatalog'))

@app.route('/signup', methods = ['POST'])
def signUp():
    """
    This method reads the sign up form and renders appropirate page.
    """
    
    # From class. In case of the state variable in the cookie
    # is not the same as in the login_session.
    if login_session['state'] != request.cookies.get('state'):
       response = make_response(json.dumps('Invalid state parameter.'), 401)
       response.headers['Content-Type'] = 'application/json'
       return response

    # Read the sign up form.
    username = request.form['nameSignUp']
    password  = request.form["passwordSignUp"]
    verify  = request.form["verifySignUp"]
    email  = request.form["emailSignUp"]


    # To check if user exists.
    user = session.query(User).filter_by(name=username).first()
    
    # Check if username, email and password is valid.
    
    valid_usr = valid_username(username)
    valid_pw = valid_username(password)
    valid_em = valid_email(email)

    # Flash appropirate messages depending on what can go
    # wrong.
    
    flash(username,'signup')
    if (valid_usr is None):
        flash('Invalid username','signup')
    else:
        # If user exists.
        flash('User exists','signup') if user is not None else flash('','signup')
    if (valid_pw is None):
       flash("That wasn't a valid password",'signup')
       flash('','signup')
    else:
        flash('','signup')
        flash("Your passwords didn't match.",'signup')\
                    if password != verify else flash('','signup')

    flash('This is not a valid email.','signup')\
                if valid_em is None else flash('','signup')
    
    flash(email,'signup')
    # If user exists or parameters are invalid.
    if (valid_usr is None\
        or user is not None\
        or valid_em is None\
        or valid_pw is None\
        or password != verify):
        return render_template('login.html',
                               loginButtonHide='hidden',
                               logoutButtonHide='hidden',
                               signup='true')
    else:
        # If user does not exist, password, username and email are valid,
        # create  a user and redirect to the main page.
        salt = make_salt()
        newUser = User(name=username,
                       email = email,
                       password=make_pw_hash(username,password,salt))
        session.add(newUser)
        session.commit()
        login_session['username'] = username
        login_session['email'] = email
        login_session['id'] = int(newUser.id)
        flash('You have signed in as %s' % username,'success')
        return redirect(url_for('showCatalog'))
    
@app.route('/logout', methods = ['GET'])
def logOut():
    """
    When the log out button is pressed the
    log in session is cleared and the main
    page is rerendered.
    """
    
    login_session.clear()
    flash('You have logged out','success')
    return redirect(url_for('showCatalog'))

@app.route('/item/<itemName>.json')
def jsonItem(itemName):
    """
    Returns a json of an item.

    Args: The name of the item.
    """
    item = session.query(Item).filter_by(name=itemName).first()
    if item is None:
       response = make_response(json.dumps('Item not found.'), 404)
       response.headers['Content-Type'] = 'application/json'
       return response
    else:
        return jsonify(item.serialize)

@app.route('/category/<categoryName>.json')
def jsonCategory(categoryName):
    """
    Returns an array of json elements in category categoryName

    Args: The name of the category name.
    """
    categoryFiltered = session.query(Category).filter_by(name=categoryName).first()
    items = session.query(Item).filter_by(category=categoryFiltered).all()
    if items is None or categoryFiltered is None:
       response = make_response(json.dumps('No category found.'), 404)
       response.headers['Content-Type'] = 'application/json'
       return response
    else:
        return jsonify(items=[item.serialize for item in items])

if __name__ == '__main__':
   app.debug = True
   app.run(host = '0.0.0.0', port = 8000)
