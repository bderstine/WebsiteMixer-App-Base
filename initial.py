#!venv/bin/python
import getpass, sys, os, uuid

print("================================================================================")
#This will need to ask for values and then update and deploy template files with those values.
domain = raw_input('Enter the domain name that will be used (.com/.net/.org): ')
appname = raw_input('Enter the app name that will be used (one word, no special chars!): ')

print("================================================================================")
adminuser = raw_input('Enter the USERNAME for the first admin user: ')
adminpw1 = getpass.getpass()
adminpw2 = getpass.getpass('Confirm Password: ')
if adminpw1 != adminpw2:
    print 'Admin passwords do not match! Abort!'
    sys.exit(0)
adminemail = raw_input('Enter an EMAIL address for the first admin user: ')

print("================================================================================")
#api.wsgi.template -> api.wsgi, update [domain]
with open ("api.wsgi.template", "r") as myfile:
    data=myfile.read().replace('[domain]', domain)
f = open('api.wsgi', 'w')
f.write(data)
f.close()

#config.py.template -> config.py, update [appname]
secretkey = str(uuid.uuid4())

with open ("config.py.template", "r") as myfile:
    data=myfile.read().replace('[appname]', appname).replace('[domain]',domain).replace('[secretkey]',secretkey)
f = open('config.py', 'w')
f.write(data)
f.close()

#virtualhosts/template.com.conf -> [domain].com.conf, update [domain] and [appname]
with open ("virtualhosts/template.com.conf", "r") as myfile:
    data=myfile.read().replace('[appname]', appname).replace('[domain]', domain)
f = open('virtualhosts/' + domain + '.conf', 'w')
f.write(data)
f.close()

# Create UPLOAD_FOLDER
directory = 'app/static/upload/'
if not os.path.exists(directory):
    print('Creating upload dir: ' + directory)
    os.makedirs(directory)
else:
    print('Upload dir exists: ' + directory)

# Update Apache
# $ ln -s /etc/apache2/virtualhosts/[domain].conf /srv/[domain]/virtualhosts/[domain].conf
# $ a2ensite [domain].conf
# $ service apache2 reload

# Setup database
from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from app import db, models
import os.path

db.create_all()
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    #api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    print('Database already exists!')
    #api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))

# Pre-load first user
u = models.User(adminuser,adminpw1,adminemail)
db.session.add(u)

# Pre-load initial settings
s1 = models.Settings('siteName',appname)
s2 = models.Settings('siteUrl','http://' + domain)
s3 = models.Settings('headerForeground', 'ffffff')
s4 = models.Settings('headerBackground', 'cccccc')
db.session.add(s1)
db.session.add(s2)
db.session.add(s3)
db.session.add(s4)

db.session.commit()

print("Setup.py is complete! You should remove setup.sh!")

