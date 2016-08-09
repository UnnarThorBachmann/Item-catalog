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
    
@app.route('/welcome', methods = ['POST'])
def showWelcome():
    if login_session['state'] != request.cookies.get('state'):
       response = make_response(json.dumps('Invalid state parameter.'), 401)
       response.headers['Content-Type'] = 'application/json'
       return response

    passed_tests = True
  
    username = request.form['logInName']
    password  = request.form['logInPassword']
    
          
    p1 = helper_functions.valid_username(username)
    p2 = helper_functions.valid_username(password)
    print username,password
    print p1,p2
    #If sentence to detect error in login.
    error_login = ''
  
    if (p1 is None or p2 is None):
        flash(username)
        flash('Invalid username or password')
    
        #response = make_response(json.dumps('Invalid username or password'), 401)
        #response.headers['Content-Type'] = 'application/json'
        #return response
        return redirect(url_for('showLogIn'))
    else:
        user = session.query(User).filter_by(name=username).first()
        #user = None
        if user is None or user.password is None or not helper_functions.valid_pw(username,password, user.password):
           flash(username)
           flash('Invalid login')
           return redirect(url_for('showLogIn'))
        else:
            print 'user exists'
            return redirect(url_for('showCatalog'))

@app.route('/signup', methods = ['POST'])
def showSignUp():    
    username = request.form['nameSignUp']
    password  = request.form["passwordSignUp"]
    verify  = request.form["verifySignUp"]
    email  = request.form["emailSignUp"]
    print username,password,verify,email
    """
    

    valid_usr = helper_functions.valid_username(username)
    valid_pw = helper_functions.valid_username(password)
    valid_em = helper_functions.valid_email(email)

    error_username = ''
    error_password =''
    error_verify = ''
    error_email=''
    passed_tests = True
    if (valid_usr is None):
       error_username = 'This is not a valid username.'
       passed_tests = False
    if (valid_pw is None):
       error_password= "That wasn't a valid password"
       passed_tests = False
    else:
        if password != verify:
           error_verify = "Your passwords didn't match."
           passed_tests = False
 
    if (valid_em is None and email != ''):
       error_email = "This is not a valid email."
       passed_tests = False

    if passed_tests:
       users = db.GqlQuery("SELECT* FROM User WHERE username=:user",user=username)
       for user in users:
           if user.username == username:
              passed_tests = False
              error_username="User already exists."
              break
    if self.request.cookies.get('name'):
        if self.request.cookies.get('name').split("|")[0] == username:
            passed_tests = False
            error_username="User already exists."
  
    if passed_tests:
       salt = helper_functions.make_salt()
       u = user_module.User(username=username, password=helper_functions.make_pw_hash(username,password,salt),email = email)
       u.put()
       self.response.headers.add_header('Set-Cookie', 'name=' + str(username) + '|' + str(helper_functions.make_pw_hash(username,password,salt)) + '; Path=/') 
       self.redirect("/blogs")
    else:
        self.render("signup.html",
                  login="",
                  logout="hidden",
                  signup="",
                  newpost="hidden",
                  blogs="hidden",
                  username = username,
                  password = password,
                  verify = verify,
                  email = email,
                  error_username = error_username,
                  error_password = error_password,
                  error_verify = error_verify,
                  error_email = error_email)
    """
    return 'prump'
if __name__ == '__main__':
   app.debug = True
   app.run(host = '0.0.0.0', port = 5000)
