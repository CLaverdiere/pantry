import os
from flask import Flask

# App initialization
app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'db/pantry.db'),
    DEBUG=True,
    SECRET_KEY='pantry key',
))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE']

from pantry.views import *
