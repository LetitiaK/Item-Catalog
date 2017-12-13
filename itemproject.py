#!/usr/bin/env python
import os
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from database_setup import Category, Item, User
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash  # NOQA
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Load the client id required for the Google API from the json file
CLIENT_ID = json.loads(
            open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "The Classy Geek"

Base = declarative_base()
engine = create_engine('postgresql+psycopg2://lilly:12345@localhost/items_db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Required snippet to ensure that the css file is updated
# This is due to the cache settings of the browser
# and is especially required for Chrome
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


# Endpoint for the index / showHomepage
@app.route('/')
@app.route('/index')
def showHomepage():
    '''The three most recently added categories and items, respectively
    as well as the login status of the user are quried. The function the
    function then returns the index template'''
    categories = session.query(Category).order_by(Category.id.desc()).limit(3)
    items = session.query(Item).order_by(Item.id.desc()).limit(3)
    status = True
    if 'username' not in login_session:
        status = False
    return render_template('index.html', categories=categories, items=items,
                           status=status)


# Endpoint for the login_session
@app.route('/login')
def showLogin():
    '''A pseudo-random string is generated as an anti forgery state token.
    The function then returns the login template'''
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Endpoint for the Google connection
@app.route('/gconnect', methods=['POST'])
def gconnect():
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
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)  # NOQA
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

    # Check if the user already exists in the database
    # If not, create a new user, else retrieve the user id
    if not session.query(exists().where(User.email == login_session['email'])).scalar():  # NOQA
        createUser(login_session)
    else:
        getUserID(login_session['email'])

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1><br>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 150px; height: 150px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"><br>'  # NOQA
    return output


# Helper function to create a new user
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Helper function to get the user information based on the id
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# Helper function to get the user id based on the email
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


# Endpoint for the Google logout
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)  # NOQA
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showHomepage'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)  # NOQA
        response.headers['Content-Type'] = 'application/json'
        return response


# Endpoint to create a new category - takes methods GET and POST
@app.route('/categories/new', methods=['GET', 'POST'])
def newCategory():
    '''It is checked if the category already exists in the database and if yes
    returns a flash message. Otherwise the category is added to the database.
    The function returns either the new_category template or redirects to
    the homepage'''
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if not session.query(exists().where(Category.name == request.form['name'])).scalar():  # NOQA
            user = session.query(User).filter_by(email=login_session['email']).one()  # NOQA
            user_id = user.id
            newCategory = Category(name=request.form['name'],
                                   image_url=request.form['img_url'],
                                   user_id=user_id)
            session.add(newCategory)
            session.commit()
            return redirect(url_for('showHomepage'))
        else:
            print("Category already exists!")
            flash("This Category already exists!")
            return redirect(url_for('newCategory'))
    else:
        return render_template('new_category.html', status=True)


# Endpoint to give an overview over all exisiting categories
@app.route('/categories')
def showCategories():
    status = True
    if 'username' not in login_session:
        status = False
    categories = session.query(Category).order_by(Category.name).all()
    return render_template('all_categories.html', categories=categories,
                           status=status)


# Endpoint to show all existing categories in a JSON format
@app.route('/categories/JSON')
def showCategoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Category=[i.serialize for i in categories])


# Enpdoint to show all items of specific category
# based on the id in a JSON format
@app.route('/categories/<int:category_id>/JSON')
def showCategoryJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).all()
    return jsonify(Category=[i.serialize for i in category])


# Endpoint to show all items for a specific category based on the id
@app.route('/categories/<int:category_id>')
def showCategory(category_id):
    status = True
    if 'username' not in login_session:
        status = False
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return render_template('category.html', category=category, items=items,
                           status=status)


# Enpdoint to show all existing items from all categories in the JSON format
@app.route('/items/JSON')
def showItemsJSON():
    items = session.query(Item).all()
    return jsonify(Item=[i.serialize for i in items])


# Endpoint to show a specific item based on the id in the JSON format
@app.route('/items/<int:item_id>/JSON')
def showItemJSON(item_id):
    item = session.query(Item).filter_by(id=item_id).all()
    return jsonify(Item=[i.serialize for i in item])


# Endpoint to show a specific item based on the id
@app.route('/items/<int:item_id>')
def showItem(item_id):
    status = True
    authorization = False
    item = session.query(Item).filter_by(id=item_id).one()
    item_user = item.user_id
    if 'username' not in login_session:
        status = False
    else:
        if session.query(exists().where(User.email == login_session['email'])).scalar():  # NOQA
            user = session.query(User).filter_by(email=login_session['email']).one()  # NOQA
            user_id = user.id
            if item_user == user_id:
                authorization = True
    return render_template('item.html', item=item, status=status,
                           authorization=authorization)


# Endpoint to edit a specific item based on the id
@app.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        cat = request.form['category']
        cat_obj = session.query(Category).filter_by(name=cat).one()
        cat_id = cat_obj.id
        item.name = request.form['name']
        item.description = request.form['description']
        item.price = request.form['price']
        item.link = request.form['link']
        item.img_url = request.form['img_url']
        item.category_id = cat_id
        session.commit()
        return redirect(url_for('showItem', item_id=item.id))
    else:
        categories = session.query(Category).all()
        return render_template('edit_item.html', item=item,
                               categories=categories, status=True)


# Endpoint to create a new item
# At least one category must exist to create a new item
@app.route('/items/new', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        user = session.query(User).filter_by(email=login_session['email']).one()  # NOQA
        user_id = user.id
        cat = request.form['category']
        cat_obj = session.query(Category).filter_by(name=cat).one()
        cat_id = cat_obj.id
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       price=request.form['price'],
                       link=request.form['link'],
                       img_url=request.form['img_url'], category_id=cat_id,
                       user_id=user_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('showHomepage'))
    else:
        categories = session.query(Category).all()
        return render_template('new_item.html', categories=categories,
                               status=True)


# Endpoint to delete an item based on a specific id
@app.route('/items/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        session.query(Item).filter_by(id=item_id).delete()
        return redirect(url_for('showHomepage'))
    else:
        item = session.query(Item).filter_by(id=item_id).one()
        return render_template('delete_item.html', item=item, status=True)


if __name__ == '__main__':
    app.secret_key = 'my_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
