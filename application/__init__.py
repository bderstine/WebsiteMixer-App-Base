from flask import Flask
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
mail = Mail(app)
moment = Moment(app)

from application import views, models

from functions import *
app.jinja_env.globals.update(first_paragraph=first_paragraph)

from application.plugins.landingpage import landingpage

