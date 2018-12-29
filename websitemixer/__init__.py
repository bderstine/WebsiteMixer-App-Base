import os
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import login_user, logout_user, current_user, login_required
from flask_login import LoginManager
from flask_moment import Moment

from websitemixer.context import *


db = SQLAlchemy()  # done here so that db is importable
migrate = Migrate()
login_manager = LoginManager()

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py')
    else:
        # load the test config if passed in
        app.config.update(test_config)

    app.debug = app.config['DEBUG']
    toolbar = DebugToolbarExtension(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)
    moment = Moment(app)

    login_manager.init_app(app)
    login_manager.login_view = 'Base.login'

    @app.before_request
    def before_request():
        g.user = current_user

    @app.after_request
    def add_header(response):
        response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
        response.headers['Cache-Control'] = 'public, max-age=0'
        return response

    app.jinja_env.globals.update(first_paragraph=first_paragraph)
    app.jinja_env.globals.update(process_tags=process_tags)
    app.jinja_env.globals.update(is_admin=is_admin)

    from websitemixer.plugins.Admin import Admin
    from websitemixer.plugins.Base import Base
    from websitemixer.plugins.Install import Setup
    app.register_blueprint(Admin.bp)
    app.register_blueprint(Base.bp)
    app.register_blueprint(Setup.bp)

    return app

