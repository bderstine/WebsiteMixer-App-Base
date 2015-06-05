#!venv/bin/python
import getpass, sys, os, uuid

print("================================================================================")
#This will need to ask for values and then update and deploy template files with those values.
domain = raw_input('Enter the domain name that will be used (.com/.net/.org): ')
appname = raw_input('Enter the app name that will be used (one word, no special chars!): ')

print("================================================================================")
dbuser = raw_input('Enter MYSQL USERNAME to use: ')
dbpass = getpass.getpass('Enter MYSQL PASSWORD to use: ')
dbname = raw_input('Enter MYSQL DATABASE NAME to use: ')

print("================================================================================")
adminuser = raw_input('Enter ADMIN USERNAME (do not use "admin"!): ')
adminpw1 = getpass.getpass('Enter ADMIN PASSWORD to use: ')
adminpw2 = getpass.getpass('Confirm ADMIN PASSWORD to use: ')
if adminpw1 != adminpw2:
    print 'Admin passwords do not match! Abort!'
    sys.exit(1)
adminemail = raw_input('Enter ADMIN EMAIL address to use: ')

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
    data=myfile.read().replace('[appname]', appname).replace('[domain]',domain).replace('[secretkey]',secretkey).replace('[dbuser]',dbuser).replace('[dbpass]',dbpass).replace('[dbname]',dbname)
f = open('config.py', 'w')
f.write(data)
f.close()

from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from application import db, models
import os.path
db.drop_all()
db.create_all()

#virtualhosts/template.com.conf -> [domain].com.conf, update [domain] and [appname]
with open ("virtualhosts/template.com.conf", "r") as myfile:
    data=myfile.read().replace('[appname]', appname).replace('[domain]', domain)
f = open('virtualhosts/' + domain + '.conf', 'w')
f.write(data)
f.close()

# Create UPLOAD_FOLDER
directory = 'application/static/upload/'
if not os.path.exists(directory):
    print('Creating upload dir: ' + directory)
    os.makedirs(directory)
else:
    print('Upload dir exists: ' + directory)

# Pre-load first user
u = models.User(adminuser,adminpw1,adminemail)
db.session.add(u)

# Pre-load initial settings
settings = {'siteName':appname, 'siteUrl':'http://'+domain, 'headerForeground':'ffffff', 'headerBackground':'cccccc', 'colorLinks':'cccccc', 'colorHover':'666666'}
for k,v in settings.iteritems():
    a = models.Settings(k,v)
    db.session.add(a)
db.session.commit()

# Pre-load initial post
a = models.Posts(adminuser,'Hello World!','/hello-world/','This is the first post! You can delete this post and add more vi /admin/!','','')
db.session.add(a)
db.session.commit()

# Pre-load initial pages
a = models.Pages('About','/about/','Yep, it\'s an about page!','','')
db.session.add(a)
db.session.commit()
a = models.Pages('Contact','/contact/','Yep, it\'s a contact page!','','')
db.session.add(a)
db.session.commit()

print("Setup is complete!")
