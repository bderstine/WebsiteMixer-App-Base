# README #

This README would normally document whatever steps are necessary to get your application up and running.

### Do these steps after unzipping...

Need to add this as a setup.py, but documenting manual steps.

* python setup.py
* mkdir /srv/[domain]
* cd /srv/[domain]
* mv virtualhosts/template.com.conf virtualhosts/[domain].conf
* replace [appname] with appname from setup.py
* replace [domain] with domain from setup.py
* cd /etc/apache2/sites-available
* ln -s /srv/[domain]/virtualhosts/[domain].conf [domain].conf
* a2ensite [domain].conf
* service apache2 reload

### Run this to setup venv
* virtualenv venv
* source venv/bin/activate
* pip install flask
* pip install flask-sqlalchemy
* pip install flask-mail

### Template codes to replace... so far...
* [domain]
* [appname]
