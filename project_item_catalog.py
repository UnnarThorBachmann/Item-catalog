from flask import Flask
app = Flask(__name__)

categories = [{'name': 'math', 'id': 1},
              {'name': 'icelandic', 'id': 2},
              {'name': 'english', 'id': 3},
              {'name': 'danish', 'id': 4}]
category = categories[0]

@app.route('/')
@app.route('/catalog')
def showCatalog():
    str = "<ul>"
    str += "<li>Navigation bar on top.</li>"
    str += "<li>Main page. Categories to the left and items to the right.</li>"
    str += "<li>Login/logout button. Add item button if user logged in.</li>"
    str += "</ul>"
    return str

@app.route('/catalog/<category>/items')
def showSelectedCategory(category):
    str = "<ul>"
    str += "<li>Navigation bar on top.</li>"
    str += "<li>Main page. Categories to the left.</li>"
    str += "<li>Main page. Items in category %s to the right.</li>" % category 
    str += "<li>Login/logout button. Add item button if user logged in.</li>"
    str += "</ul>"
    return str


@app.route('/catalog/<category>/<item>')
def showItemFromCategory(category,item):
    str = "<ul>"
    str += "<li>Navigation bar on top.</li>"
    str += "<li>%s name from category %s</li>" % (item,category)
    str += "<li>%s description from category %s</li>" % (item,category)
    str += "<li>Edit and delete button</li>"
    str += "</ul>"
    return str

@app.route('/catalog/<item>/edit')
def editItem(item):
    str = "<ul>"
    str += "<li>Navigation bar on top.</li>"
    str += "<li>Edit form</li>"
    str += "<li>%s name </li>" % item
    str += "<li>%s description</li>" % item
    str += "<li>%s category</li>" % item
    str += "</ul>"
    return str

@app.route('/catalog/<item>/delete')
def deleteItem(item):
    str = "<ul>"
    str += "<li>Navigation bar on top.</li>"
    str += "<li>Are you sure?</li>"
    str += "<li>submit button</li>" 
    str += "</ul>"
    return str

@app.route('/<name>.json')
def jsonItem(name):
    return "%s.json" % name

@app.route('/login')
def showLogin():
    return "Display login"

if __name__ == '__main__':
   app.debug = True
   app.run(host = '0.0.0.0', port = 5000)
