from pantry.forms import *
from pantry.utils import *

import sqlite3, math, requests, os

from flask import Flask, url_for, render_template, request, redirect, abort, flash, g
from flask.ext import login
from flask.ext.login import LoginManager, login_user, logout_user, current_user
from flask.ext.security import login_required
from pagination import Pagination

# Login Manager init
login_manager = LoginManager()
login_manager.init_app(app)

# Default config settings
PER_PAGE = 10
venmo_api_code = ''

@app.route("/")
def pantry():
    return render_template('home.html')

# TODO refactor redundant code with shopping_list
# TODO capitalize food names.
@app.route("/add_to_pantry", methods=["POST"])
@login_required
def add_to_pantry():
    foods = request.form['food-names-pantry']
    if(foods):
        desired = False
        food_names = foods.replace(' ', '').strip(',').split(',')
        for food_name in food_names:
            food = Food(food_name, current_user.username, foods.count(food_name), desired)
            db.session.add(food)
        db.session.commit()
        flash("Added new foods to your pantry!", 'success')
    else:
        flash("Invalid food list supplied. Sorry.", 'error')
    return redirect(url_for('dashboard'))

@app.route("/add_to_sl", methods=["POST"])
@login_required
def add_to_sl():
    foods = request.form['food-names-sl']
    if(foods):
        desired = True
        food_names = foods.replace(' ', '').strip(',').split(',')
        for food_name in food_names:
            food = Food(food_name, current_user.username, foods.count(food_name), desired)
            db.session.add(food)
        db.session.commit()
        flash("Added new foods to your shopping list!", 'success')
    else:
        flash("Invalid food list supplied. Sorry.", 'error')
    return redirect(url_for('dashboard'))

#TODO eliminate passing all users.
#TODO remove redundancy with pantry and sl.
@app.route("/dashboard", defaults={'page':1})
@app.route("/dashboard/<int:page>")
@login_required
def dashboard(users=[], user_pantry=[], user_sl=[], geo_info=[], page=1):
    user_pantry = Food.query.filter(Food.owner == current_user.username) \
                            .filter(Food.desired == False) \
                            .order_by(Food.name).all()

    user_sl = Food.query.filter(Food.owner == current_user.username) \
                        .filter(Food.desired == True) \
                        .order_by(Food.name).all()

    cx, cy = current_user.geo_x, current_user.geo_y
    users = User.query.order_by('abs(geo_x - {}) + abs(geo_y - {})'.format(cx, cy))

    names = [user.real_name for user in users]
    dists = [round(haversine_miles(user.geo_x, user.geo_y, cx, cy), 2) for user in users]
    geo_info = {name:dist for (name, dist) in zip(names, dists)}

    count = users.count()
    users = users.offset(PER_PAGE * (page - 1)).limit(PER_PAGE)
    pagination = Pagination(page, PER_PAGE, count)
    return render_template('dashboard.html', users=users, \
            user_pantry=user_pantry, user_sl=user_sl, geo_info=geo_info,
            pagination=pagination)


# TODO redundant
@app.route("/empty_pantry")
@login_required
def empty_pantry():
    owned_foods = Food.query.filter(Food.owner == current_user.username) \
                            .filter(Food.desired == False).all()
    for food in owned_foods:
        db.session.delete(food)
    db.session.commit()
    flash("Cleared your list!", 'success')
    return redirect(url_for('dashboard'))

@app.route("/empty_sl")
@login_required
def empty_sl():
    desired_foods = Food.query.filter(Food.owner == current_user.username) \
                              .filter(Food.desired == True).all()
    for food in desired_foods:
        db.session.delete(food)
    db.session.commit()
    flash("Cleared your list!", 'success')
    return redirect(url_for('dashboard'))

# TODO eliminate geolocation redundancy
@app.route("/find/<food_name>")
@login_required
def find(users=[], food_name=None, geo_info=[]):
    if food_name:
        cx, cy = current_user.geo_x, current_user.geo_y
        # users = Food.query.filter(Food.owner == current_user.username) \
        #                   .order_by('abs(geo_x - {}) + abs(geo_y - {})'.format(cx, cy))
        food_owners = [food.owner for food in Food.query.filter(Food.name == food_name) \
                                                        .filter(Food.owner != current_user.username) \
                                                        .filter(Food.desired == False).all()]
        users = User.query.order_by('abs(geo_x - {}) + abs(geo_y - {})'.format(cx, cy)) \
                          .filter(User.username.in_(food_owners)).all()
        names = [user.real_name for user in users]
        dists = [round(haversine_miles(user.geo_x, user.geo_y, cx, cy), 2) for user in users]
        geo_info = {name:dist for (name, dist) in zip(names, dists)}

    return render_template('find.html', users=users, food_name=food_name, geo_info=geo_info)

@app.route("/examples")
def examples():
    return render_template('examples.html')

@app.route("/login", methods=["GET", "POST"])
def login(form=None):
    form = LoginForm()
    if form.validate_on_submit():
        user = form.get_user(db)
        login_user(user)
        flash("Logged in!", 'success')
        session['user_id'] = form.user.id
        g.user = user
        return redirect(request.args.get("next") or url_for('dashboard'))
    if(form.username.data):
        flash("Bad login credentials, try again!", 'error')
    return render_template("home.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out!", 'success')
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if(request.method == 'GET'):
        return render_template('register.html')
    else:
        username = request.form['username']
        password = request.form['password']
        realname = request.form['realname']
        address = request.form['address']
        email = request.form['email']

        data = [username, password, realname, address, email]
        if any(not field for field in data):
            flash("Everything is required! Everything! Do it over!", 'error')
            return render_template('register.html')

        new_guy = User(*data)
        db.session.add(new_guy)
        db.session.commit()

        flash("That's pretty much it. You're registered. Have fun!", 'success')
        return render_template('home.html')

# TODO Decide if keeping venmo.
# @app.route('/venmo/<info>')
# @login_required
# def venmo_login(info=''):
#     def buy_item():
#         name, food = info.split('-')
#         user = User.query.filter_by(username=name).first()
#         user.items_available = ','.join([a for a in \
#             user.items_available.split(',') if a != food])
#         current_user.items_desired = ','.join([a for a in \
#             current_user.items_desired.split(',') if a != food])
#         db.session.commit()
#
#     # Time to make this nicer this later.
#     if info:
#         buy_item()
#         return redirect('https://api.venmo.com/v1/oauth/authorize?client_id=2284&response_type=code&scope=make_payments')
#     else:
#         flash("Item purchasing failed.")
#         return redirect('/dashboard')

# @app.route('/venmo2')
# @login_required
# def venmo_connect():
#     try:
#         venmo_api_code = request.args.get('code')
#     except:
#         flash("Venmo API Connect failed.")
#         return redirect('/dashboard')
#
#     data = {}
#     data ['client_id'] = '2284'
#     data ['client_secret'] = '4L23sdF428pwBQYrMe3UQKrdQpdC4GvC'
#     data ['code'] = venmo_api_code
#     data ['scope'] = 'make_payments'
#
#     url = 'https://api.venmo.com/v1/oauth/access_token'
#     response = requests.post(url,data)
#     print(response.json())
#
#     flash("You successfully purchased the ingredient!",'success')
#     return redirect('/dashboard')

# TODO Find out why this is here.
def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

def init_sample_db():
    try:
        os.remove(app.config["DATABASE"])
    except:
        print("Warning: Database already empty or no database file found.")

    db.create_all()

    u1 = User('admin', 'root', 'Admin', '4317 Madonna Rd', 'admin@pantry.com')
    u2 = User('chlaver1', 'root', 'Chris Laverdiere', '10000 Hilltop Circle', 'cmlaverdiere@gmail.com')
    u3 = User('kcoxe1', 'root', 'Kevin Coxe', '4502 Oak Ridge Dr', 'kcoxe1@gmail.com')

    db.session.add(u1)
    db.session.add(u2)
    db.session.add(u3)

    db.session.commit()
    print("Sample database created.")
