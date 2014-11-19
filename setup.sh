#!/bin/bash
virtualenv venv
source venv/bin/activate

pip install flask
pip install flask-moment
pip install flask-sqlalchemy
pip install sqlalchemy-migrate
pip install flask-login
pip install flask-mail

./venv/bin/python initial.py
rm initial.py
rm setup.sh

rm -rf .git
