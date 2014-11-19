#!/bin/bash
virtualenv venv
source venv/bin/activate

pip install flask
pip install flask-moment
pip install flask-sqlalchemy
pip install sqlalchemy-migrate
pip install flask-login
pip install flask-mail

python initial.py
rm initial.py

