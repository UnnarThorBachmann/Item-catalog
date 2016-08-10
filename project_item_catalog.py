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
def showCatalog(user=None):
    filterCategoryName = 'none'
    
    categories = session.query(Category).all()
    #if user:  
    #else:
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
    
    if filterItem is not None and filterItem.category.name == categoryName:
       return render_template('item.html', item=filterItem)
    else:
        response = make_response(json.dumps("File not found"), 404)
        response.headers['Content-Type'] = 'application/json'
        return response
 

@app.route('/catalog/<itemName>/edit', methods = ['POST','GET'])
def editItem(itemName):
   categories = session.query(Category).all()
   filterItem = session.query(Item).filter_by(name=itemName).first()
   if filterItem is not None:
      categories = session.query(Category)
      return render_template('edit.html', item=filterItem,categories=categories)
   else:
       response = make_response(json.dumps("File not found"), 404)
       response.headers['Content-Type'] = 'application/json'
       return response
    
@app.route('/catalog/new', methods = ['POST','GET'])
def newItem():
   categories = session.query(Category).all()
   return render_template('newItem.html',categories = categories)
   

@app.route('/catalog/<itemName>/delete', methods = ['POST','GET'])
def deleteItem(itemName):
    return render_template('delete.html')
        
@app.route('/catalog.json')
def jsonItem():
    return str(categories)

@app.route('/login')
def showLogIn():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    response = make_response(render_template('login.html'))
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
        
        return redirect(url_for('showLogIn'))
    else:
        user = session.query(User).filter_by(name=username).first()
        print user
        #user = None
        if user is None or user.password is None or not helper_functions.valid_pw(username,password, user.password):
           flash(username,'login')
           flash('Invalid login','login')
           return redirect(url_for('showLogIn'))
        else:
            login_session['username'] = username
            login_session['email'] = email
            return redirect(url_for('showCatalog'))

@app.route('/signup', methods = ['POST'])
def showSignUp():
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
    
    if (valid_usr is None or user is not None or valid_em is None or valid_pw is None or password !=verify):
        print 'prump'
        return redirect(url_for('showLogIn'))
    else:
        salt = helper_functions.make_salt()
        newUser = User(name=username,
                       email = email,
                       password=helper_functions.make_pw_hash(username,password,salt))
        session.add(newUser)
        session.commit()
        login_session['username'] = username
        login_session['email'] = email
        
        return redirect(url_for('showCatalog'))
    
@app.route('/logout', methods = ['GET'])
def LogOut():
    login_session.clear()
    return redirect(url_for('showCatalog'))
if __name__ == '__main__':
   app.debug = True
   app.run(host = '0.0.0.0', port = 5000)
