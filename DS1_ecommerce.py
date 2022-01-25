# 0.0.0 system setup

# 0.0.1 import libraries

import sqlite3
import bottle  # bottle import
from bottle import get, template, static_file, request, redirect, response, Bottle, abort
import time  # other imports
import random
import string
import logging
import logging.handlers

print(sqlite3.sqlite_version_info)

# 0.0.2 setup session management using bottle-session

app = bottle.app()

con = sqlite3.connect('database/usersDB.db')
c = con.cursor()

secretKey = 'BHFEAPNJEGANJPAGN3095U23TF'

# 0.0.3  setup app logs for debugging

log = logging.getLogger('bottle')
log.setLevel('DEBUG')
h = logging.handlers.TimedRotatingFileHandler(
    'logs/nlog', when='midnight', backupCount=9999)
f = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
h.setFormatter(f)
log.addHandler(h)


# 1.0.0 App setup

# 1.1.0 static content

@app.route('/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static/')


@app.route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='./static')
#
@app.route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static')

### TEST ###
@app.route('/static/<filename:path>', name='static')
def serve_static(filename):
    return static_file(filename, root='static/')


# Static Routes
@get("/static/css/<filepath:re:.*\.css>")
def css(filepath):
    return static_file(filepath, root="static/css")

@get("/static/font/<filepath:re:.*\.(eot|otf|svg|ttf|woff|woff2?)>")
def font(filepath):
    return static_file(filepath, root="static/font")

@get("/static/img/<filepath:re:.*\.(jpg|png|gif|ico|svg)>")
def img(filepath):
    return static_file(filepath, root="static/img")

@get("/static/js/<filepath:re:.*\.js>")
def js(filepath):
    return static_file(filepath, root="static/js")



# 1.2.0 Define functions


# 1.2.1 Return SQL Queries in nice form

def printAll(listOfResultsA):
    for item in listOfResultsA:
        print(item)


# 1.2.2 Check database for existing value

def checkinDB(value_to_check, table_var, column_var, id_name_in_db='"%"', id='%'):
    command = 'SELECT IIF ("{string}" IN (SELECT {column} FROM {table} WHERE {id_name_in_db}="{id}") , "MATCH", "MISS")'.format(
        string=value_to_check, table=table_var, column=column_var, id=id, id_name_in_db=id_name_in_db)
    # command='SELECT IIF (TRUE IN (SELECT loggedIn FROM users WHERE "%"="%") , "MATCH", "MISS")'
    c.execute(command)
    result = c.fetchall()
    return result[0][0]


# 1.2.3  Function to check if user is logged in and authorised

def checkAuth():
    loginName = request.get_cookie("user", secret=secretKey)
    randStr = request.get_cookie("randStr", secret=secretKey)
    # cookies return with brackets this will trim them
    if randStr != None:
        randStr = randStr.lstrip("'").rstrip("'")
    log.info(str(loginName) + ' ' + request.method + ' ' +
             request.url + ' ' + request.environ.get('REMOTE_ADDR'))

    # get id to identify table row (it could be done with just username but it is already used in too many places to change)
    id = getUserID(loginName)

    # main body of the function. It lookes for username, random string saved at the login and logged in status in database
    if checkinDB(loginName, "users", "username") == "MATCH" and checkinDB(randStr, "users", "randStr", "userID",
                                                                          id) == "MATCH" and checkinDB("1", "users",
                                                                                                       "loggedIn") == "MATCH":
        # timeout for user session
        if (time.time() - getFromDB("users", "lastSeen", "userID", id)) < 3600:
            updateinDB(id, "users", "lastSeen", time.time(), "userID")
            print("CheckAuth Timeout is ok")
            return "Authenticated"
        else:
            print("CheckAuth Timeout happened")
            redirect('/logout')
    else:
        # if user is not logged in funcion returns unauthenticated. Logout also redirects here
        return "Unauthenticated"


# 1.2.4. Insert value to database

def updateinDB(item_ID, table, column, value, ID_field_name_in_Database):
    command = 'UPDATE {table} SET {column}={value} WHERE {DB_ID}="{item_ID}"'.format(table=table, column=column,
                                                                                     value=value, item_ID=item_ID,
                                                                                     DB_ID=ID_field_name_in_Database)
    c.execute(command)
    con.commit()


# 1.2.5 Get user ID from database
def getUserID(username):
    command = 'SELECT userID from users where username="{userN}"'.format(userN=username)
    c.execute(command)
    result = c.fetchone()
    if result != None:
        return result[0]
    else:
        return None


# 1.2.6 Get specific value from database

def getFromDB(table_var, column_var, id_var, checked_userID):
    command = 'SELECT {column} FROM {table} WHERE {id_var}="{checked_userID}"'.format(column=column_var,
                                                                                      table=table_var, id_var=id_var,
                                                                                      checked_userID=checked_userID)
    c.execute(command)
    result = c.fetchone()
    if result != None:
        return result[0]
    else:
        return None


# 1.2.7 Function that returns max id value in the table. Used to create next id for new items

def getMaxID(table_name, id_column_name):
    command = 'SELECT MAX ({column_name}) FROM {table}'.format(column_name=id_column_name, table=table_name)
    c.execute(command)
    result = c.fetchone()
    if result != None:
        return result[0]
    else:
        return 0


# 1.2.8 Convert bottle form to python dictionary

def form_to_dict(web_form):
    form_dict = {}
    for item in web_form:
        form_dict[item] = web_form.get(item)
    return form_dict


# each adding function
# def add_user():


def create_clientdata_package(formdata):
    client_package = {}

    mapping_dictionary = {'areacode': 'areanumber'}

    new_id = getMaxID("users", 'userID')
    if new_id != None:
        new_id = new_id + 1
    else:
        new_id = 1
    printAll(formdata)
    client_package['userID'] = new_id
    for d_key in ['name', 'surname', 'email', 'telnum', 'areacode']:

        if d_key in mapping_dictionary:
            map_d_key = mapping_dictionary.get(d_key)
            client_package[map_d_key] = formdata.get(d_key)
        else:
            client_package[d_key] = formdata.get(d_key)

    return client_package


def create_users_package(formdata):
    user_pack = {}

    mapping_dictionary = {'login': 'username'}

    new_id = getMaxID("users", 'userID')
    if new_id != None:
        new_id = new_id + 1
    else:
        new_id = 1

    user_pack['userID'] = new_id
    for d_key in ('login', 'password'):
        if d_key in mapping_dictionary:
            map_d_key = mapping_dictionary.get(d_key)
            user_pack[map_d_key] = formdata.get(d_key)
        else:
            user_pack[d_key] = formdata.get(d_key)
    return user_pack


def create_address_package(formdata, userID):
    address_package = {}

    # names differ between forms and database. This mapping will be used to convert them
    mapping_dictionary = {'streetname': 'street', 'streetnumber': 'building', 'flatnumber': 'flat', 'city': 'city',
                          'zipcode': 'zipcode'}

    new_id = getMaxID("address", 'addressID')
    if new_id != None:
        new_id = new_id + 1
    else:
        new_id = 1
    address_package['addressID'] = new_id
    address_package['userID'] = userID
    for d_key in ('streetname', 'streetnumber', 'flatnumber', 'city', 'zipcode', 'country'):
        if d_key in mapping_dictionary:
            map_d_key = mapping_dictionary.get(d_key)
            address_package[map_d_key] = formdata.get(d_key)
        else:
            address_package[d_key] = formdata.get(d_key)
    return address_package


def insert_into_db(table, dictionary, commit):
    keylist = list(dictionary.keys())
    vallist = list()
    for i in dictionary.keys():
        vallist.append(dictionary.get(i))
    # python returns list in square brackets and SQL doesn't like that
    keylist_round = str(", ".join(keylist))
    vallist_round = str(", ".join(repr(v) for v in vallist))
    command = 'INSERT INTO {table} ({keylist}) VALUES ({vallist})'.format(table=table, vallist=vallist_round,
                                                                          keylist=keylist_round)
    c.execute(command)
    if commit == 1:
        con.commit()


def add_user(userpack, addresspack, clientpack):
    insert_into_db('users', userpack, 0)
    insert_into_db('address', addresspack, 0)
    insert_into_db('client_data', clientpack, 0)
    con.commit()

Products: dict[str, int] = {
    'pen': 0,
    'apple': 0,
    'apple pen': 0,
    'pineapple': 0,
    'pineapple pen': 0,
    'pen pineapple apple pen':0
}






# HERE PAGE SETUP STARTS


# 2.0.0 Route index page

@app.route('/')
@app.route('/index.html')
@app.route('/index')
def home():
    login_status = checkAuth()
    return template('index', loginINFO=login_status)


# 3.0.0 Registration page. It just displays data form and passes it to the newcustomer page

@app.route('/register', method=['GET', 'POST'])
def register():
    login_status = checkAuth()
    return template('register', loginINFO=login_status)


# 4.0.0 New customer page. It receives data from registration page, order details page, or from itself after pressing submit button

@app.route('/newcustomer', method=['POST', 'GET'])
def newcustomer():
    login_status = checkAuth()

    # Database packages

    user_package = {}
    client_package = {}
    address_package = {}

    # initial values for variables

    # 4.1.0 Check how newcustomer page was entered

    fromdone = request.query.done  # value taken from page URL, !! it is stored as text !!
    from_page = request.query.fromproceed

    # if entered from register or order detail page
    if from_page == "1":
        # save form data from previous page
        register_formdata = request.forms

        # 4.1.2.2 Prepare personal data from personal forms

        client_package = create_clientdata_package(register_formdata)
        print(client_package)
        response.set_cookie("client_pack", client_package, secret=secretKey)

        # 4.1.2.3 Prepare address data from personal forms
        address_package = create_address_package(register_formdata, client_package['userID'])
        print(address_package)
        response.set_cookie("address_pack", address_package, secret=secretKey)

        # 4.1.2.4 Display newcustomer template

        return template('newcustomer', duplicate_password_flag_HTML=False, password_dont_match_HTML=False,
                        duplicate_account_flag_HTML=False, loginINFO=login_status)

    # 4.1.1 From clicking done button. If thats the case the variable fromdone = 1. Clicking "Done" button appends value in URL mimicking "GET" method. This means login and password form was filled and sent

    if fromdone == "1":
        client_package = request.get_cookie("client_pack", secret=secretKey)
        address_package = request.get_cookie("address_pack", secret=secretKey)
        # From done means the form was filled and sent. The page ot reloaded. Password and login data are taken from the form.

        # save form data
        newcustomer_form = request.forms
        # 4.1.1.0 Check if passwords match
        password1 = newcustomer_form.get('password')
        password2 = newcustomer_form.get('password2')

        if password1 != password2:
            password_dont_match = True
            return template('newcustomer', password_dont_match_HTML=password_dont_match,
                            duplicate_account_flag_HTML=False, loginINFO=login_status)
        else:

            # 4.1.1.1 Check for duplicate username in database. This is the only restriction user creation has.
            proposedLogin = newcustomer_form.get('login')
            duplicate = checkinDB(proposedLogin, "users", "username")

            if duplicate == "MATCH":
                duplicate_account_flag = True
                return template('newcustomer', password_dont_match_HTML=False,
                                duplicate_account_flag_HTML=duplicate_account_flag, loginINFO=login_status)
            else:

                # 4.1.1.2 If passwords match and loggin is not a duplicate then new user can be created.

                # prepare all data packets necessary for user creation and use them in add user function

                user_package = create_users_package(newcustomer_form)
                add_user(user_package, address_package, client_package)

                # login after account is created
                loginName = user_package.get('username')
                password = user_package.get('password')
                randStr = ''.join(random.choice(
                    string.ascii_uppercase + string.digits) for _ in range(18))

                # request to database won't work unless randStr is put into quotes
                randStr = "'" + randStr + "'"

                return loginf(loginName, password, randStr, "NO")
                # redirect

        # 4.1.1.4 Redirect to index page
        redirect('/index')


    else:

        # 4.1.2.3 By entering URL manually. There is no form data and database import will result in error. Redirect to register page

        redirect('/register')


# 5.0.0 login page as defined during classes

@app.route('/login')
@app.route('/login/')
@app.route('/login', method='POST')
def login():
    login_status = checkAuth()
    # newcustomer=request.query.new

    if login_status != "Unauthenticated":
        redirect('/index')

    randStr = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(18))

    # request to database won't work unless randStr is put into quotes
    randStr = "'" + randStr + "'"

    # Login from dataform

    loginName = request.forms.get('login', default=False)
    password = request.forms.get('password', default=False)
    log.info(str(loginName) + ' ' + request.method + ' ' +
             request.url + ' ' + request.environ.get('REMOTE_ADDR'))

    return loginf(loginName, password, randStr, login_status)


def loginf(loginName, password, randStr, login_status):
    print(loginName)
    print(password)
    print(checkinDB(loginName, "users", "username"))
    print(checkinDB(password, "users", "password"))
    if checkinDB(loginName, "users", "username") == "MATCH" and checkinDB(password, "users", "password") == "MATCH":
        uID = getUserID(loginName)
        response.set_cookie("user", loginName, secret=secretKey)
        response.set_cookie("randStr", randStr, secret=secretKey)
        updateinDB(uID, "users", "loggedIn", True, "userID")
        # users[loginName]["loggedIn"] = True
        updateinDB(uID, "users", "randStr", randStr, "userID")
        # users[loginName]["randStr"] = randStr
        updateinDB(uID, "users", "lastSeen", time.time(), "userID")
        # users[loginName]["lastSeen"] = time.time()
        redirect('/index')
        return True
    else:
        return template('login', loginINFO=login_status)

#Basket



# def update_product_qty(key):
#     if key in Products.keys():
#         Products[key] =






# 5.1.0 Logout page
# logging out will use logout page rather than call logout function directly

@app.route('/logout')
# 1.2.3.2 Logout function
def logout():
    loginName = request.get_cookie("user", secret=secretKey)
    randStr = request.get_cookie("randStr", secret=secretKey)
    id = getUserID(loginName)
    updateinDB(id, "users", "loggedIn", 0, "userID")
    print(id)
    response.delete_cookie("user")
    response.delete_cookie("randStr")
    redirect('/index')


@app.route('/myaccount')
def myaccount():
    login_status = checkAuth()
    print(login_status)
    if login_status == 'Unauthenticated':
        redirect('/login')

    return template('my-account', loginINFO=login_status)


@app.route('/myorders')
def myorders():
    login_status = checkAuth()
    if login_status=='Unauthenticated':
        redirect('/login')
    else:
        uID=getUserID(request.get_cookie('user',secret=secretKey))
        command='SELECT * FROM "orders" WHERE userID = {ID}'.format(ID=uID)
        c.execute(command)
        orders=c.fetchall()
        print(uID)
        print(orders)





        return template('myorders', loginINFO=login_status)


##6 Basket Site:

@app.route('/cart')
def cart():
    login_status = checkAuth()
    return template('cart', loginINFO=login_status)


@app.route('/products')
def products():
    login_status = checkAuth()
    command = 'Select * FROM products'
    c.execute(command)
    downloaded_products = c.fetchall()
    print(downloaded_products)
    printAll((downloaded_products[0]))

# def split():
#     for each x in downloaded_products

    return template('shop', loginINFO=login_status, prod_down=downloaded_products)


# The below function takes quantity of products when user goes to the checkout site:
@app.route('/products', method=['POST'])
def test_function():
    login_status = checkAuth()

    #pen = request.forms.get(product[1])
    # apple = request.forms.get("apple")
    # apple_pen = request.forms.get("apple_pen")
    # pineapple = request.forms.get("pineapple")
    # pineapple_pen = request.forms.get("pineapple_pen")
    # ppap = request.forms.get("ppap")
    # #change dictionary value
    # Products["pen"] = int(pen)
    # Products["apple"] = int(apple)
    # Products["apple pen"] = int(apple_pen)
    # Products["pineapple"] = int(pineapple)
    # Products["pineapple pen"] = int(pineapple_pen)
    # Products["pen pineapple apple pen"] = int(ppap)
    # print(Products)



    return template('checkout', loginINFO=login_status)




@app.route('/checkout', method=['POST'])
def checkout_site():
    login_status = checkAuth()

    my_dict = {}

    prod_collection = form_to_dict(request.forms)
    print(prod_collection)

    product_id_list = prod_collection.keys()
    print(product_id_list)

    for k in product_id_list:
        prod_name = getFromDB("products", "product_name", "product_id", k)
        my_dict[prod_name + "_name"] = getFromDB("products", "product_name", "product_id", k)
        my_dict[prod_name + "_price"] = getFromDB("products", "price", "product_id", k)
        my_dict[prod_name + "_qty"] = prod_collection[k]

    print(my_dict)
    response.set_cookie("cart", my_dict, secret=secretKey)

    # getFromDB(table_var, column_var, id_var, checked_userID)



    #
    # prod_collectionrequest.forms
    # for x in prod_collection:
    #     my_dict =
    # pen = request.forms.get("1")
    # print(pen)
    #
    #
    # command = 'Select * FROM products'
    # c.execute(command)
    # downloaded_products = c.fetchall()
    # print(downloaded_products)
    # a=downloaded_products
    # print(a[0][1])
    # b= list(downloaded_products)
    # print(b)
    #
    #
    #
    # apple = request.forms.get(product)
    # apple_pen = request.forms.get("Apple pen")
    # pineapple = request.forms.get("Pineapple")
    # pineapple_pen = request.forms.get("Pineapple pen")
    # ppap = request.forms.get("Pen Pineapple Apple Pen")
    # print(apple,apple_pen,pineapple,pineapple_pen,ppap)
    # sth = request.forms
    # for item in sth:
    #     print(sth.get(item))
    # printAll(apple)
    return template('checkout', loginINFO=login_status)

@app.route('/test')
def test_site():
    login_status = checkAuth()
    command = 'Select * FROM products'
    c.execute(command)
    downloaded_products = c.fetchall()
    print(downloaded_products)
    a=downloaded_products
    print(a[0][3])

    return template('test_product', loginINFO=login_status, prod_down=downloaded_products)


#
# @app.route('/example')
# def example_site():
#     login_status = checkAuth()
#     return template('example_page', loginINFO=login_status)

app.run(host='localhost', port=2137, reloader=False, debug=False)
