from flask import Flask,  render_template, redirect
app = Flask(__name__)

#Changing a category to a subject.
categories = [{'name': 'math', 'id': 1},
              {'name': 'icelandic', 'id': 2},
              {'name': 'english', 'id': 3},
              {'name': 'danish', 'id': 4},
              {'name': 'spanish', 'id': 5},
              {'name': 'biology', 'id': 6},
              {'name': 'physics', 'id': 7},
              ]
items = [{'title': 'Calculus 3000', 'description': 'I have Calculus 3000 for sale. Please contact me in 848-0112.', 'category': 'math', 'id':  1},
         {'title': 'Spanish 103', 'description': 'I have Spanish 103 for sale.', 'category': 'spanish', 'id': 2},
         {'title': 'Danish 103', 'description': 'I have Danish 103 for sale.', 'category': 'danish', 'id': 3},
         {'title': 'English 103', 'description': 'I have English 103 for sale.', 'category': 'english', 'id': 4},
         {'title': 'Biology 103', 'description': 'I have Biology 103 for sale.', 'category': 'biology', 'id': 5},      
         {'title': 'Physics 103', 'description': 'I have Physics 103 for sale.', 'category': 'physics', 'id': 6},
         {'title': 'a', 'description': 'I have Physics 103 for sale.', 'category': 'physics', 'id': 7}
       ]
category = categories[0]
item = items[0]
@app.route('/')
@app.route('/catalog')
def showCatalog():
    filterCategory = 'none'
    return render_template('catalog.html', categories=categories,items=items, filterCategory = filterCategory)

@app.route('/catalog/<category>/items')
def showSelectedCategory(category):
    print category
    filterCategory = category
    items2 = []
    for item in items:
        if item['category'] == category:
           items2.append(item)
    return render_template('catalog.html', categories=categories,items=items2, filterCategory = filterCategory, n = len(items2))

@app.route('/catalog/<categoryName>/<itemTitle>')
def showItemFromCategory(itemTitle,categoryName):
    itemSelected = None
    for item in items:
        if itemTitle == item['title'] and categoryName == item['category']:
           itemSelected = item
           return render_template('item.html', item=itemSelected)

    return redirect('/catalog')


@app.route('/catalog/<itemTitle>/edit')
def editItem(itemTitle):
    itemSelected = None
    for item in items:
        if itemTitle == item['title']:
           itemSelected = item
           return render_template('edit.html', item=itemSelected,categories=categories)

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
    return "Display login"

if __name__ == '__main__':
   app.debug = True
   app.run(host = '0.0.0.0', port = 5000)
