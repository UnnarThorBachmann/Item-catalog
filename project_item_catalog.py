"""
Author: Unnar Thor Bachmann.

Methods for logging in and out with Facebook and Google written in class. Motified by Unnar Thor Bachmann to correct errors and fit to my project.
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
import httplib2
import urllib
import requests
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

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
       pictureExists=True
       picture = login_session['picture']
       print picture
    else:
        addButtonHide = 'hidden'
        logoutButtonHide = 'hidden'
        loginButtonHide = ''
        items = session.query(Item).order_by(desc(Item.date)).slice(0,n).all()
        pictureExists = False
        picture = ''

    
    categories = queryCategory.all()
    
    return render_template('catalog.html',
                           categories=categories,
                           items=items,
                           filterCategoryName = filterCategoryName,
                           addButtonHide= addButtonHide,
                           logoutButtonHide=logoutButtonHide,
                           loginButtonHide=loginButtonHide,
                           pictureExists=pictureExists,
                           picture=picture)

@app.route('/catalog/<categoryName>/items')
def showCategory(categoryName):
    """
    Renders the main page of the app were only items
    in give category are rendered.
    """
    queryCategory = session.query(Category)
    # I am going to display at maximum as many items as there are categories.
    category = queryCategory.filter_by(name=categoryName).first()
    
    filterCategory=categoryName
    

    # Rendering the page differently when user is logged in.
    if login_session.has_key('username'):
       addButtonHide = ''
       logoutButtonHide = ''
       loginButtonHide = 'hidden'
       pictureExists= True
       picture = login_session['picture']
       category = queryCategory.filter_by(name=categoryName).first()
       queryItems = session.query(Item).filter(Item.user_id==login_session['id'])
       items = queryItems.filter(Item.category==category).all()
    else:
        addButtonHide = 'hidden'
        logoutButtonHide = 'hidden'
        loginButtonHide = ''
        pictureExists= False
        picture = ''
        items = session.query(Item).filter_by(category=category).all()
        
    categories = queryCategory.all()
    return render_template('catalog.html',
                           categories=categories,
                           items=items,
                           filterCategoryName = categoryName,
                           addButtonHide= addButtonHide,
                           logoutButtonHide=logoutButtonHide,
                           loginButtonHide=loginButtonHide,
                           n = len(items),
                           pictureExists=pictureExists,
                           picture=picture)

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
       pictureExists=True
       picture = login_session['picture']
    else:
        logoutButtonHide = 'hidden'
        loginButtonHide = ''
        editDeleteHide = 'hidden'
        pictureExists=False
        picture = ''
    
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
                              email=email,
                              pictureExists=pictureExists,
                              picture=picture)
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
          pictureExists=True
          picture = login_session['picture']
          categories = session.query(Category).all()
          # Splitting the query do to length. The item is filtered
          # with respect to name and the id of the current user.
          query =  session.query(Item).filter(Item.name==itemName)
          currentUser = session.query(User).filter_by(email = login_session['email']).first()
          filterItem = query.filter(Item.user == currentUser).first()

          #If the item does not exist the page is not rendered.
          if filterItem is not None:          
             categories = session.query(Category)
             #The item id is put into the loggin session for editing.
             login_session['itemId'] = int(filterItem.id)
             return render_template('edit.html',
                                    item=filterItem,
                                    categories=categories,
                                    logoutButtonHide=logoutButtonHide,
                                    loginButtonHide=loginButtonHide,
                                    pictureExists= pictureExists,
                                    picture = picture)
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
        itemEdited.user = session.query(User).filter_by(email=login_session['email']).first()
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
          pictureExists=True
          picture = login_session['picture']
          categories = session.query(Category).all()
          return render_template('newItem.html',
                                 categories = categories,
                                 logoutButtonHide=logoutButtonHide,
                                 loginButtonHide=loginButtonHide,
                                 pictureExists=pictureExists,
                                 picture = picture)
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
        user = session.query(User).filter_by(email=login_session['email']).first()

        category = session.query(Category).filter_by(name=itemCategory).first()

        #Creating the user

        newItem = Item(name=itemName,
                       description = itemDescription,
                       user_id = user.id,
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
          pictureExists=True
          picture = login_session['picture']
          login_session['itemId'] = int(itemToDelete.id)
       
          return render_template('delete.html',
                                 logoutButtonHide=logoutButtonHide,
                                 loginButtonHide=loginButtonHide,
                                 itemName=itemToDelete.name,
                                 pictureExists=pictureExists,
                                 picture = picture)
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
    if login_session.has_key('username'):
       return redirect(url_for('logout'))
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))

    # The log in session keeps a state variable to prevent forgery as in class.
    login_session['state'] = state
    loginButtonHide = 'hidden'
    logoutButtonHide = 'hidden'
    
    
    return render_template('login.html',
                           loginButtonHide=loginButtonHide,
                           logoutButtonHide=logoutButtonHide,
                           signup='false',
                           STATE=state)
    

    
@app.route('/logout', methods = ['GET'])
def logOut():
    """
    Logs out the users.

    Redirects to the main page.
    """
    if not login_session.has_key('provider'):
       return redirect(url_for('showCatalog'))
    if login_session['provider']=='facebook':
       facebook_id = login_session['id']
       # The access token must be included to successfully logout
       access_token = login_session['access_token']
       url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
       h = httplib2.Http()
       result = h.request(url, 'DELETE')[1]
       
    elif login_session['provider']=='google':
        # Only disconnect a connected user.
        #login_session['credentials'] = credentials.access_token

        #credentials = login_session.get('credentials')
        access_token = login_session.get('credentials')
        if access_token is None:
           response = make_response(
            json.dumps('Current user not connected.'), 401)
           response.headers['Content-Type'] = 'application/json'
           return response
        #access_token = login_session['']#credentials.access_token
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]
        if result['status'] != '200':
           # For whatever reason, the given token was invalid.
           response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
           response.headers['Content-Type'] = 'application/json'
           return response
        
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

@app.route('/fblogin', methods=['POST'])
def fbLogIn():
    """
    This method is called when user is logs in by Facebook.
    
    This method was written in class but motified a little bit.
    
    Redirects back to ajax call which redirects to the success function.
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token
    #Reading the app id and secret from server file
    jsonSecret = json.loads(open('fb_client_secrets.json', 'r').read())
    app_id = jsonSecret['web']['app_id']
    app_secret = jsonSecret['web']['app_secret']


    # This was covered in class. Receiving information about the user.
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    token = result.split("&")[0]

    
    url = 'https://graph.facebook.com/v2.7/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    
    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]

    
    # This was written in class.
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token
    # see if user exists
    user = session.query(User).filter_by(email=login_session['email']).first()
    
    if user is None:
       user = User(name=login_session['username'],
                   email= login_session['email'])
       session.add(user)
       session.commit()

    login_session['id'] = user.id
    # Redirection is done with the ajax success function.
    # Directed to the success function.
    return 'ok'


@app.route('/success')
def success():
    """
    This function is called when user is logged successfully in
    by Amazon, Google or Facebook.
    """
    flash("Now logged in as %s" % login_session['username'],'success')
    return redirect(url_for('showCatalog'))
    
@app.route('/amazonlogin', methods=['POST'])
def amazonLogIn():
    """
    This was not shown in class. This is the Authorization Code Grant method
    which is one of two methods Amazon give up on their website to connect to them.
    Mainly because it is more secure and relies on server site scripting.
    """
    # To prevent cross site request forgery.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Getting client id and secret
    jsonSecret = json.loads(open('amazon_client_secrets.json', 'r').read())
    client_id = jsonSecret['web']['app_id']
    client_secret = jsonSecret['web']['app_secret']

    # Receiving the  code from Amazon.
    code = request.data

    # Requesting the access token from Amazon.
    grant_type = 'authorization_code'
    post_data = {'client_id': client_id,'client_secret': client_secret,'code':code,'grant_type':grant_type}
    url = 'https://api.amazon.com/auth/o2/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    h = httplib2.Http()
    access_token_response = json.loads(h.request(url,'POST',urllib.urlencode(post_data),headers=headers)[1])
    
    # If no access token then return error.
    if not access_token_response.has_key('access_token'):
       response = make_response(json.dumps('Invalid state parameter.'), 401)
       response.headers['Content-Type'] = 'application/json'
       return response

    # Use the access token to gain the user profile
    access_token = access_token_response['access_token']
    
    h = httplib2.Http()
    user_profile_response = json.loads(h.request('https://api.amazon.com/user/profile?access_token=%s' % access_token,'GET')[1])
    
    # If the user profile was gained log the user in. Otherwise return an error.
    if user_profile_response['name']:
       login_session['username'] = user_profile_response['name']
       login_session['email'] = user_profile_response['email']

       user = session.query(User).filter_by(email = login_session['email']).first()
       if user is None:
          user = User(name=login_session['username'],
                      email = login_session['email'])
          session.add(user)
          session.commit()
          
       login_session['id'] = user.id
       login_session['provider'] = 'amazon'
       # Did not find a mechanism to retrive pictures.
       

       login_session['picture'] = url_for('static', filename='me.png')
       return 'Ok'
    else: 
        return 'error'

    
@app.route('/glogin', methods=['POST'])
def gLogIn():
    """
    Logs the user to the system with gmail.

    Redirects to main page on success.

    This method was mostly written in class but debugged and motified by Unnar Thor Bachmann.
    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        print "Oauth object."
        print  oauth_flow 
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    CLIENT_ID = "56296313039-v0t49qs2gjcc5dkia7533fq6sejefp0q.apps.googleusercontent.com"
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    
    # Add provider to the log in session.
    login_session['provider'] = 'google'
    

    # see if user exists, if it doesn't make a new one
    
    user = session.query(User).filter_by(email=login_session['email']).first()

    if user is None:
       user = User(name=login_session['username'],
                   email= login_session['email'])
       session.add(user)
       session.commit()

    login_session['id'] = user.id
    
    # Fixed after reading forum.
    login_session['credentials'] = credentials.access_token
    
    
    print "Finishing with gmail login."
    return 'ok'

if __name__ == '__main__':
   app.debug = True
   app.run(host = '0.0.0.0', port = 8000)
