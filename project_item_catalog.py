from flask import Flask, request,  render_template, redirect, url_for, make_response,session as login_session, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User
import json
import random
import string
import helper_functions

app = Flask(__name__)
app.secret_key = 'unnar'


engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog')
def showCatalog():
    filterCategoryName = 'none'
    if login_session.has_key('username'):
       addButtonHide = ''
       logoutButtonHide = ''
       loginButtonHide = 'hidden'
       items = session.query(Item).filter_by(user_id=login_session['id']).all()
    else:
        addButtonHide = 'hidden'
        logoutButtonHide = 'hidden'
        loginButtonHide = ''
        items = session.query(Item).all()


    categories = session.query(Category).all()
    return render_template('catalog.html',
                           categories=categories,
                           items=items,
                           filterCategoryName = filterCategoryName,
                           addButtonHide= addButtonHide,
                           logoutButtonHide=logoutButtonHide,
                           loginButtonHide=loginButtonHide)

@app.route('/catalog/<categoryName>/items')
def showCategory(categoryName):
    category = session.query(Category).filter_by(name=categoryName).first()
    filterCategory=categoryName

    if login_session.has_key('username'):
       addButtonHide = ''
       logoutButtonHide = ''
       loginButtonHide = 'hidden'
       category = session.query(Category).filter_by(name=categoryName).first()
       items = session.query(Item).filter(Item.user_id==login_session['id']).filter(Item.category==category).all()
    else:
        addButtonHide = 'hidden'
        logoutButtonHide = 'hidden'
        loginButtonHide = ''
        items = session.query(Item).filter_by(category=category).all()

    categories = session.query(Category).all()
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
    if filterItem is not None and filterItem.category.name == categoryName\
       and (not login_session.has_key('id') or login_session['id'] == filterItem.user_id):
       return render_template('item.html',
                              item=filterItem,
                              logoutButtonHide=logoutButtonHide,
                              loginButtonHide=loginButtonHide,
                              editDeleteHide=editDeleteHide,
                              email=email)
    else:
        # Not sure if this is the right response.
        response = make_response(json.dumps("File not found"), 404)
        response.headers['Content-Type'] = 'application/json'
        return response
 

@app.route('/catalog/<itemName>/edit', methods = ['POST','GET'])
def editItem(itemName):
    if login_session.has_key('username'):
       logoutButtonHide = ''
       loginButtonHide = 'hidden'
    else:
        return redirect(url_for('showCatalog'))

    if request.method == 'GET':
       categories = session.query(Category).all()
       filterItem = session.query(Item).filter_by(name=itemName).first()
    
       if filterItem is not None:
          categories = session.query(Category)
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
        itemName = request.form['name']
        itemDescription = request.form['description']
        
        itemCategory = session.query(Category).filter_by(name=request.form['category']).first()
        itemEdited = session.query(Item).filter_by(name=itemName).first()
        itemEdited.name=itemName
        itemEdited.description = itemDescription
        itemEdited.category = itemCategory
        itemEdited.category_id = itemCategory.id
        itemEdited.user = session.query(User).filter_by(name=login_session['username']).first()
        itemEdited.user_id = int(login_session['id'])
        session.add(itemEdited)
        session.commit()
        return redirect(url_for('showCatalog'))
        
@app.route('/catalog/new', methods = ['POST','GET'])
def newItem():
    if login_session.has_key('username'):
       logoutButtonHide = ''
       loginButtonHide = 'hidden'
    else:
        return redirect(url_for('showCatalog'))
    
    if request.method == 'GET':   
       categories = session.query(Category).all()
       return render_template('newItem.html',
                              categories = categories,
                              logoutButtonHide=logoutButtonHide,
                              loginButtonHide=loginButtonHide)
    else:   
        itemName = request.form['name']
        itemDescription = request.form['description']
        itemCategory = request.form['category']
        
        user = session.query(User).filter_by(name=login_session['username']).first()
        category = session.query(Category).filter_by(name=itemCategory).first()
        newItem = Item(name=itemName,
                       description = itemDescription,
                       user_id = int(login_session['id']),
                       user = user,
                       category = category,
                       category_id = category.id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('showCatalog'))          
        

@app.route('/catalog/<itemName>/delete', methods = ['POST','GET'])
def deleteItem(itemName):
    itemToDelete = session.query(Item).filter_by(name=itemName).first()
    if login_session.has_key('username'):
       logoutButtonHide = ''
       loginButtonHide = 'hidden'
    else:
        return redirect(url_for('showCatalog'))

    if request.method == 'GET':   
       return render_template('delete.html',
                              logoutButtonHide=logoutButtonHide,
                              loginButtonHide=loginButtonHide,
                              itemName=itemToDelete.name)
    else:
        
        if itemToDelete.user_id == login_session['id']:
           session.delete(itemToDelete)
           session.commit()
           return redirect(url_for('showCatalog'))
           
        else:
            response = make_response(json.dumps("You have not permission for deleting this item."),
                                                 400)
            response.headers['Content-Type'] = 'application/json'
            return response
        
@app.route('/catalog.json')
def jsonItem():
    return str(categories)

@app.route('/login')
def showLogIn():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    loginButtonHide = 'hidden'
    logoutButtonHide = 'hidden'
    
    response = make_response(render_template('login.html',
                                             loginButtonHide=loginButtonHide,
                                             logoutButtonHide=logoutButtonHide,
                                             signup='false'))
    response.set_cookie('state', state)
    return response
    
@app.route('/loginuser', methods = ['POST'])
def loginUser():
    if login_session['state'] != request.cookies.get('state'):
       response = make_response(json.dumps('Invalid state parameter.'), 401)
       response.headers['Content-Type'] = 'application/json'
       return response

    passed_tests = True
  
    username = request.form['logInName']
    password  = request.form['logInPassword']
    
          
    valid_usr = helper_functions.valid_username(username)
    valid_pw = helper_functions.valid_username(password)
    #If sentence to detect error in login.
    error_login = ''
  
    if (valid_usr is None or valid_pw is None):
        flash(username,'login')
        flash('Invalid username or password','login')
        
        return redirect(url_for('showLogIn',
                                signup='false'))
    else:
        user = session.query(User).filter_by(name=username).first()
        
        if user is None or user.password is None or not helper_functions.valid_pw(username,
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
    if login_session['state'] != request.cookies.get('state'):
       response = make_response(json.dumps('Invalid state parameter.'), 401)
       response.headers['Content-Type'] = 'application/json'
       return response
    
    username = request.form['nameSignUp']
    password  = request.form["passwordSignUp"]
    verify  = request.form["verifySignUp"]
    email  = request.form["emailSignUp"]

    user = session.query(User).filter_by(name=username).first()
    
    
    flash(username,'signup')
    valid_usr = helper_functions.valid_username(username)
    valid_pw = helper_functions.valid_username(password)
    valid_em = helper_functions.valid_email(email)

    if (valid_usr is None):
        flash('Invalid username','signup')
    else:
        if user is not None:
           flash('User exists','signup')
        else:
            flash('','signup')
            
    if (valid_pw is None):
       flash("That wasn't a valid password",'signup')
       flash('','signup')
    else:
        flash('','signup')
        if password != verify:
           flash("Your passwords didn't match.",'signup')
        else:
            flash('','signup')
            
    if (valid_em is None):
       flash('This is not a valid email.','signup')
    else:
        flash('','signup')
        
    flash(email,'signup')
    
    if (valid_usr is None or user is not None or valid_em is None or valid_pw is None or password != verify):
        return render_template('login.html',
                               loginButtonHide='hidden',
                               logoutButtonHide='hidden',
                               signup='true')
    else:
        salt = helper_functions.make_salt()
        newUser = User(name=username,
                       email = email,
                       password=helper_functions.make_pw_hash(username,password,salt))
        session.add(newUser)
        session.commit()
        login_session['username'] = username
        login_session['email'] = email
        login_session['id'] = int(newUser.id)
        flash('You have signed in as %s' % username,'success')
        return redirect(url_for('showCatalog'))
    
@app.route('/logout', methods = ['GET'])
def logOut():
    login_session.clear()
    flash('You have logged out','success')
    return redirect(url_for('showCatalog'))

if __name__ == '__main__':
   app.debug = True
   app.run(host = '0.0.0.0', port = 5000)
