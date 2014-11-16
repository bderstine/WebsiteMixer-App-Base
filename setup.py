#!venv/bin/python
#This will need to ask for values and then update and deploy template files with those values.

#check for /srv/[domain]

#api.wsgi.template -> api.wsgi
# [domain]

#config.py.template -> config.py
# [appname]

#virtualhosts/template.com.conf -> [domain].com.conf
# [domain]
# [appname]

# $ ln -s /etc/apache2/virtualhosts/[domain].conf /srv/[domain]/virtualhosts/[domain].conf
# $ a2ensite [domain].conf
# $ service apache2 reload