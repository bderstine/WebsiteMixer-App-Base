import os
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
DEBUG_TB_INTERCEPT_REDIRECTS = False
DEBUG_TB_PROFILER_ENABLED = True
DEBUG_TB_TEMPLATE_EDITOR_ENABLED = False
SECRET_KEY = '395c494289c0f7909336c53feac4079f6d7760ed763269b4'
UPLOAD_FOLDER = basedir+'/websitemixer/static/upload/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'])

SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir,'myapp.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True