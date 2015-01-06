#!/bin/bash
virtualenv venv
source venv/bin/activate

pip install flask
pip install flask-moment
pip install flask-sqlalchemy
pip install sqlalchemy-migrate
pip install flask-login
pip install flask-mail
pip install feedparser
pip install beautifulsoup4
pip install pymysql

./venv/bin/python initial.py

#Clean up files no longer required after setup runs
rm -rf .git
rm api.wsgi.template
rm config.py.template
rm virtualhosts/template.com.conf
rm initial.py
rm setup.sh
