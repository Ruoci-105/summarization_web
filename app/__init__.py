import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
basedir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(basedir, 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(data_dir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'
migrate = Migrate(app, db)

from app import view
from app.models import *

