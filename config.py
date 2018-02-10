import os
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
DEBUG_TB_PROFILER_ENABLED = True
DEBUG_TB_TEMPLATE_EDITOR_ENABLED = False
SECRET_KEY = '6f9ce79437e3fd1e11cdba78198a31b4fb9225b84efe39cc'
UPLOAD_FOLDER = basedir+'/websitemixer/static/upload/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'])

SQLALCHEMY_DATABASE_URI = 'postgresql://webm:monkey216@localhost:5432/webm_dev'
SQLALCHEMY_TRACK_MODIFICATIONS = True