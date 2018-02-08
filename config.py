import os
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
DEBUG_TB_INTERCEPT_REDIRECTS = False
DEBUG_TB_PROFILER_ENABLED = True
DEBUG_TB_TEMPLATE_EDITOR_ENABLED = False
SECRET_KEY = 'fb44917aa467dbb2b18149957b776454e8e841225ab61fd8'
UPLOAD_FOLDER = basedir+'/websitemixer/static/upload/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'])

SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir,'myapp.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True