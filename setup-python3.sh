#!/bin/bash
#virtualenv venv
#source venv/bin/activate
pyvenv venv
. venv/bin/activate

pip install flask
pip install flask-moment
pip install flask-sqlalchemy
pip install sqlalchemy-migrate
pip install flask-login
pip install flask-mail
pip install feedparser
pip install beautifulsoup4
pip install pymysql

./venv/bin/python3 initial.py

if [ $? -eq 0 ]; then
  #Clean up files no longer required after initial.py successfully runs
  rm -rf .git
  rm api.wsgi.template
  rm config.py.template
  rm virtualhosts/template.com.conf
  rm initial.py
  rm setup.sh
fi
