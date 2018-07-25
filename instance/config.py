import os
from flask import current_app

DEBUG = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
DEBUG_TB_PROFILER_ENABLED = True
DEBUG_TB_TEMPLATE_EDITOR_ENABLED = True
SECRET_KEY = 'websitemixersupersecretkey1234567890'

SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

DATABASE = '/srv/WebsiteMixer-App-Base/instance/websitemixer.sqlite'
