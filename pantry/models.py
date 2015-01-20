from pantry import app

from flask import session
from flask.ext.sqlalchemy import SQLAlchemy
from pygeocoder import Geocoder

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    real_name = db.Column(db.String(80), unique=True)
    address = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    items_available = db.Column(db.String(1000))
    items_desired = db.Column(db.String(1000))
    points = db.Column(db.Integer)
    num_given = db.Column(db.Integer)
    num_bought = db.Column(db.Integer)
    geo_x = db.Column(db.Float)
    geo_y = db.Column(db.Float)
    created_at = db.Column(db.TIMESTAMP) # TODO fix this being 0.

    def __init__(self, username, password, real_name, address, email):
        self.username = username
        self.password = password
        self.real_name = real_name
        self.address = address
        self.email = email

        geo_results = Geocoder.geocode(self.address)
        self.geo_x = geo_results[0].coordinates[0]
        self.geo_y = geo_results[0].coordinates[1]

    def check_password(self, other_pass):
        return self.password == other_pass

    def is_authenticated(self):
        return session['user_id'] == self.id

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __unicode__(self):
        return self.username

    def __repr__(self):
        return '<User {} {} {} {}' \
                .format(self.username, self.real_name, self.address, self.email)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_from = db.Column(db.String(80))
    name_to = db.Column(db.String(80))
    item = db.Column(db.String(80))
    price = db.Column(db.Float)
    created_at = db.Column(db.TIMESTAMP)

    def __init__(self, name_from, name_to, item, price):
        self.name_from = name_from
        self.name_to = name_to
        self.item = item
        self.price = price

    def __repr__(self):
        return 'Transaction {} {} {} {}' \
               .format(self.name_from, self.name_to, self.item, self.price)
