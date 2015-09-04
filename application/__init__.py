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
app.jinja_env.globals.update(process_tags=process_tags)

pluginData = get_all_plugin_info()
for p in pluginData:
    for k,v in p['import'].iteritems():
        plugin = "application.plugins."+k
        name = str(v)
        imported = getattr(__import__(plugin, fromlist=[name]), name)

