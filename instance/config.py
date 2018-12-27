import os
basedir = os.path.abspath(os.path.dirname(__file__))

APPDIR = os.getcwd()
DEBUG = False
DEBUG_TB_INTERCEPT_REDIRECTS = False
DEBUG_TB_PROFILER_ENABLED = True
DEBUG_TB_TEMPLATE_EDITOR_ENABLED = False
SECRET_KEY = '33e276ccbc4a1c31fe695a30bfd464a3d8c2477339c57218'
UPLOAD_FOLDER = APPDIR+'/websitemixer/static/upload/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'])

SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir,'myapp.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True