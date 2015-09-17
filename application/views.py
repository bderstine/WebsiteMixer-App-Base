import signal, os, time, re, urllib, urllib2, hashlib, shutil, zipfile
from flask import Flask, Response, session, request, url_for, redirect, render_template, abort, g, send_from_directory
from flask.ext.moment import Moment
from flask.ext.login import login_user , logout_user , current_user , login_required
from werkzeug.routing import BaseConverter
from werkzeug import secure_filename
from werkzeug.contrib.atom import AtomFeed
from urlparse import urljoin

from application import app
from models import *
from config import *
from functions import *

#######################################################################
# The following section was added very early oni
# may not be needed and should be tested

from flask.ext.login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

#######################################################################

@app.route('/')
def home():
    s = getSettings()
    blogData = Posts.query.order_by(Posts.post_date.desc()).all()
    return render_template(s['theme']+'/index.html',blogData=blogData,s=s)

@app.route('/login/',methods=['GET','POST'])
def login():
    s = getSettings()
    error = None
    if request.method == 'GET':
        return render_template(s['theme']+'/login.html',s=s)
    username = request.form['username']
    password = hashlib.md5(request.form['password']).hexdigest()
    registered_user = User.query.filter_by(username=username,password=password).first()
    if registered_user is None:
        addLogEvent('Failed login attempt for ' + username)
        return redirect(url_for('login'))
    login_user(registered_user)
    addLogEvent('User ' + username + ' successfully logged in.')
    return redirect(request.args.get('next') or url_for('admin'))

#######################################################################
# Admin handlers

@app.route('/admin/')
@login_required
def admin():
    s = getSettings()
    eventData = Logs.query.order_by(Logs.log_date.desc()).limit(25)
    return render_template('admin/index.html',eventData=eventData,s=s)

@app.route('/admin/clear-logs/',methods=['GET','POST'])
@login_required
def clearlogs():
    if request.args.get('confirmed'):
        logs = Logs.query.all()
        for e in logs:
            db.session.delete(e)
        addLogEvent('Events were cleared by ' + current_user.username)
        return redirect("/admin/")
    else:
        message = 'Are you sure you want to delete ALL logs?<br/><br/>'
        message+= '<a href="/admin/clear-logs/?confirmed=yes">Click here to delete!</a> | '
        message+= '<a href="/admin/">No take me back!</a>'
        return message

@app.route('/admin/themes/')
@login_required
def adminthemes():
    s = getSettings()
    activeTheme = get_theme_info(s['theme'])
    themeData = get_all_theme_info()
    return render_template('admin/manage-themes.html',s=s,themeData=themeData,activeTheme=activeTheme)

@app.route('/admin/themes/add/')
@login_required
def adminthemesadd():
    s = getSettings()
    themeData = []
    themeNames = {}

    current_themes = get_all_theme_info()
    for c in current_themes:
        themeNames.update([(c['basics']['directory'], c['basics']['name'])])

    url = "http://websitemixer.com/api/themes/"
    response = urllib.urlopen(url)
    apiThemeData = json.loads(response.read())
    for a in apiThemeData['json_list']:
        if a['theme_name'] not in themeNames.values():
            themeData.append(a)
    
    return render_template('admin/themes-add.html',s=s,themeData=themeData)

@app.route('/admin/themes/install/<theme>/')
@login_required
def adminthemeinstall(theme):
    s = getSettings()
    url = "http://websitemixer.com/api/themes/"+theme+"/"
    response = urllib.urlopen(url)
    themeData = json.loads(response.read())
    themeFile = urllib2.urlopen(themeData['json_list'][0]['theme_repo']+'/archive/master.zip')
    saveDir = basedir+'/application/templates/'+themeData['json_list'][0]['theme_directory']
    os.makedirs(saveDir)
    output = open(saveDir+'/master.zip','wb')
    output.write(themeFile.read())
    output.close()

    my_dir = saveDir
    my_zip = saveDir+'/master.zip'
    with zipfile.ZipFile(my_zip) as zip_file:
        for member in zip_file.namelist():
            filename = os.path.basename(member)
            # skip directories
            if not filename:
                continue

            # copy file (taken from zipfile's extract)
            source = zip_file.open(member)
            target = file(os.path.join(my_dir, filename), "wb")
            with source, target:
                shutil.copyfileobj(source, target)

    os.remove(saveDir+'/master.zip')
    return redirect('/admin/themes/')

@app.route('/admin/themes/activate/<theme>/')
@login_required
def adminthemesactivate(theme):
    s = getSettings()
    #move activeTheme assets back to theme folder
    activeTheme = get_theme_info(s['theme'])
    if 'assets' in activeTheme.keys():
        for d in activeTheme['assets'].values():
            src = basedir+'/application/static/'+d
            dst = basedir+'/application/templates/'+activeTheme['basics']['directory']+'/'
            try:
                shutil.move(src,dst)
            except Exception as e:
                continue
    #move newTheme assets to static folder
    newTheme = get_theme_info(theme)
    if 'assets' in newTheme.keys():
        for d in newTheme['assets'].values():
            src = basedir+'/application/templates/'+newTheme['basics']['directory']+'/'+d
            dst = basedir+'/application/static/'
            try:
                shutil.move(src,dst)
            except Exception as e:
                continue
    #update setting in db for newtheme
    u = Settings.query.filter_by(setting_name='theme').update(dict(setting_value=theme))
    db.session.commit()
    return redirect("/admin/themes/")

#@app.route('/admin/themes/edit/<theme>/')

@app.route('/admin/themes/delete/<theme>/')
@login_required
def adminthemesdelete(theme):
    s = getSettings()
    if request.args.get('confirmed'):
        shutil.rmtree(basedir+'/application/templates/'+theme)
        addLogEvent('Theme "' + theme + '" was deleted by ' + current_user.username)
        return redirect("/admin/themes/")
    else:
        message = 'Are you sure you want to delete theme: ' + theme + '?<br/><br/>'
        message+= '<a href="/admin/themes/delete/' + theme + '/?confirmed=yes">Click here to delete!</a> | '
        message+= '<a href="/admin/themes/">No take me back!</a>'
        return message

@app.route('/admin/plugins/')
@login_required
def adminplugins():
    s = getSettings()
    pluginData = get_all_plugin_info()
    return render_template('admin/manage-plugins.html',s=s,pluginData=pluginData)

@app.route('/admin/plugins/add/')
@login_required
def adminpluginsadd():
    s = getSettings()
    pluginData = []
    pluginNames = {}

    current_plugins = get_all_plugin_info()
    for c in current_plugins:
        pluginNames.update([(c['basics']['directory'], c['basics']['name'])])

    url = "http://websitemixer.com/api/plugins/"
    response = urllib.urlopen(url)
    apiPluginData = json.loads(response.read())
    for a in apiPluginData['json_list']:
        if a['plugin_name'] not in pluginNames.values():
            pluginData.append(a)

    return render_template('admin/plugins-add.html',s=s,pluginData=pluginData)

@app.route('/admin/plugins/install/<plugin>/')
@login_required
def adminpluginsinstall(plugin):
    s = getSettings()
    url = "http://websitemixer.com/api/plugins/"+plugin+"/"
    response = urllib.urlopen(url)
    pluginData = json.loads(response.read())
    pluginFile = urllib2.urlopen(pluginData['json_list'][0]['plugin_repo']+'/archive/master.zip')
    saveDir = basedir+'/application/plugins/'+pluginData['json_list'][0]['plugin_directory']
    os.makedirs(saveDir)
    output = open(saveDir+'/master.zip','wb')
    output.write(pluginFile.read())
    output.close()

    my_dir = saveDir
    my_zip = saveDir+'/master.zip'
    with zipfile.ZipFile(my_zip) as zip_file:
        for member in zip_file.namelist():
            filename = os.path.basename(member)
            dirName = member.split('/')
            dirName.pop(0)
            # skip directories
            if not filename:
                continue

            #print dirName
            if len(dirName)>1:
                if not os.path.isdir(saveDir+'/'+dirName[0]):
                    os.makedirs(saveDir+'/'+dirName[0])

            # copy file (taken from zipfile's extract)
            source = zip_file.open(member)
            targetFile = os.path.join(my_dir, "/".join(dirName))
            target = file(targetFile, "wb")
            with source, target:
                shutil.copyfileobj(source, target)

    os.remove(saveDir+'/master.zip')
    return redirect('/admin/plugins/')

@app.route('/admin/plugins/delete/<plugin>/')
@login_required
def adminpluginsdelete(plugin):
    s = getSettings()
    if request.args.get('confirmed'):
        shutil.rmtree(basedir+'/application/plugins/'+plugin)
        addLogEvent('Plugin "' + plugin + '" was deleted by ' + current_user.username)
        return redirect("/admin/plugins/")
    else:
        message = 'Are you sure you want to delete plugin: ' + plugin + '?<br/><br/>'
        message+= '<a href="/admin/plugins/delete/' + plugin + '/?confirmed=yes">Click here to delete!</a> | '
        message+= '<a href="/admin/plugins/">No take me back!</a>'
        return message

@app.route('/admin/plugins/restart/')
@login_required
def adminpluginsrestart():
    os.kill(os.getpid(), signal.SIGINT)
    return redirect("/admin/plugins/")

@app.route('/admin/posts/')
@login_required
def manageposts():
    s = getSettings()
    postData = Posts.query.order_by(Posts.post_date.desc()).all()
    return render_template('admin/manage-posts.html',postData=postData,s=s)

@app.route('/admin/posts/add/',methods=['GET','POST'])
@login_required
def postsadd():
    s = getSettings()
    if request.method == 'GET':
        return render_template('admin/posts-add.html',s=s)
    else:
        addPost = Posts(current_user.username,request.form['title'],request.form['slug'],request.form['content'],request.form['subheading'],request.form['featureimg'],request.form['tags'])
        db.session.add(addPost)
        db.session.commit()
        return redirect("/admin/posts/")

@app.route('/admin/posts/edit/<id>/',methods=['GET','POST'])
@login_required
def postsedit(id):
    s = getSettings()
    if request.method == 'GET':
        postData = Posts.query.filter_by(id=id).first()
        return render_template('admin/posts-edit.html',id=id,postData=postData,s=s)
    else:
        update = Posts.query.filter_by(id=id).update(dict(post_title=request.form['title'],post_slug=request.form['slug'],post_content=request.form['content'],post_subheading=request.form['subheading'],post_image=request.form['featureimg'],post_modified=datetime.utcnow()))
        db.session.commit()
        addLogEvent('Post "' + request.form['title'] + '" was updated by ' + current_user.username)
        return redirect("/admin/posts/")

@app.route('/admin/posts/delete/<id>/')
@login_required
def postsdelete(id):
    s = getSettings()
    if request.args.get('confirmed'):
        postData = Posts.query.filter_by(id=id).first()
        db.session.delete(postData)
        db.session.commit()
        addLogEvent('Post "' + postData.post_title + '" was deleted by ' + current_user.username)
        return redirect("/admin/posts/")
    else:
        message = 'Are you sure you want to delete ID: ' + id + '?<br/><br/>'
        message+= '<a href="/admin/posts/delete/' + id + '/?confirmed=yes">Click here to delete!</a> | '
        message+= '<a href="/admin/posts/">No take me back!</a>'
        return message

@app.route('/admin/pages/')
@login_required
def managepages():
    s = getSettings()
    pageData = Pages.query.order_by(Pages.page_title).all()
    return render_template('admin/manage-pages.html',pageData=pageData,s=s)

@app.route('/admin/pages/add/',methods=['GET','POST'])
@login_required
def pagesadd():
    s = getSettings()
    if request.method == 'GET':
        return render_template('admin/pages-add.html',s=s)
    else:
        addPage = Pages(request.form['title'],request.form['slug'],request.form['content'],request.form['subheading'],request.form['featureimg'])
        db.session.add(addPage)
        db.session.commit()
        return redirect("/admin/pages/")

@app.route('/admin/pages/edit/<id>/',methods=['GET','POST'])
@login_required
def pagesedit(id):
    s = getSettings()
    if request.method == 'GET':
        pageData = Pages.query.filter_by(id=id).first()
        return render_template('admin/pages-edit.html',id=id,pageData=pageData,s=s)
    else:
        form_title=request.form['title']
        form_slug=request.form['slug']
        form_content=request.form['content']
        form_subheading=request.form['subheading']
        form_image=request.form['featureimg']
        update = Pages.query.filter_by(id=id).update(dict(page_title=form_title,page_slug=form_slug,page_content=form_content,page_subheading=form_subheading,page_image=form_image,page_modified=datetime.utcnow()))
        db.session.commit()
        addLogEvent('Page "' + form_title + '" was updated by ' + current_user.username)
        return redirect("/admin/pages/")

@app.route('/admin/pages/delete/<id>/')
@login_required
def pagesdelete(id):
    s = getSettings()
    if request.args.get('confirmed'):
        pageData = Pages.query.filter_by(id=id).first()
        db.session.delete(pageData)
        db.session.commit()
        addLogEvent('Page "' + pageData.page_title + '" was deleted by ' + current_user.username)
        return redirect("/admin/pages/")
    else:
        message = 'Are you sure you want to delete ID: ' + id + '?<br/><br/>'
        message+= '<a href="/admin/pages/delete/' + id + '/?confirmed=yes">Click here to delete!</a> | '
        message+= '<a href="/admin/">No take me back!</a>'
        return message

@app.route('/admin/settings/',methods=['GET','POST'])
@login_required
def managesettings():
    s = getSettings()
    if request.method == 'POST':
        for key, value in request.form.iteritems():
            check = Settings.query.filter_by(setting_name=key).first()
            if check is None:
                a = Settings(key,value)
                db.session.add(a)
            else:
                update = Settings.query.filter_by(setting_name=key).update(dict(setting_value=value))
            db.session.commit()
        return redirect('/admin/settings/')
    return render_template('admin/manage-settings.html',s=s)

@app.route('/admin/files/',methods=['GET','POST'])
@login_required
def managefiles():
    s = getSettings()
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER,filename))
            return redirect(url_for('managefiles'))
    tree=make_tree(UPLOAD_FOLDER)
    newlist = sorted(tree['children'], key=lambda k: k['name'])
    data = {}
    data['children'] = newlist
    return render_template('admin/manage-files.html',tree=data,s=s)

@app.route('/admin/files/delete/')
@login_required
def filesdelete():
    s = getSettings()
    filename = request.args.get('filename')
    if request.args.get('confirmed'):
        os.remove(os.path.join(UPLOAD_FOLDER,filename))
        return redirect(url_for('managefiles'))
        addLogEvent('File "' + filename + '" was deleted by ' + current_user.username)
    else:
        message = 'Are you sure you want to delete the file: ' + filename + '?<br/><br/>'
        message+= '<a href="/admin/files/delete/?filename=' + filename + '&confirmed=yes">Click here to delete!</a> | '
        message+= '<a href="/admin/manage-uploads/">No take me back!</a>'
        return message

@app.route('/admin/users/')
@login_required
def manageusers():
    s = getSettings()
    userData = User.query.order_by(User.username).all()
    return render_template('admin/manage-users.html',userData=userData,s=s)

@app.route('/admin/users/add/',methods=['GET','POST'])
@login_required
def usersadd():
    s = getSettings()
    if request.method == 'POST':
        username = request.form['username']
        if User.query.get(username) is not None:
            return "That username is already in use! Click back and try again!"
        password1 = request.form['password1']
        password2 = request.form['password2']
        if password1 != password2:
            return "Passwords do not match! Click back and try again!"
        email = request.form['email']
        password = hashlib.md5(request.form['password1']).hexdigest()
        addUser = User(username,password,email)
        db.session.add(addUser)
        db.session.commit()
        return redirect("/admin/users/")
    return render_template('admin/users-add.html',s=s)

@app.route('/admin/users/delete/<id>/')
@login_required
def usersdelete(id):
    userData = User.query.filter_by(id=id).first()
    if request.args.get('confirmed'):
        db.session.delete(userData)
        db.session.commit()
        addLogEvent('User "' + userData.username + '" was deleted by ' + current_user.username)
        return redirect(url_for('adminusers'))
    else:
        message = 'Are you sure you want to delete the user: ' + userData.username + '?<br/><br/>'
        message+= '<a href="/admin/deleteuser/' + id + '/?confirmed=yes">Click here to delete!</a> | '
        message+= '<a href="/admin/users/">No take me back!</a>'
        return message

@app.route('/admin/users/profile/',methods=['GET','POST'])
@login_required
def profile():
    s = getSettings()
    if request.method == 'GET':
        userData = User.query.filter_by(username=current_user.username).first()
        return render_template('admin/users-edit.html',userData=userData,s=s)
    else:
        update = User.query.filter_by(username=current_user.username).update(dict(email=request.form['email']))
        db.session.commit()
        return redirect("/admin/users/")

@app.route('/admin/users/profile/<user>/',methods=['GET','POST'])
@login_required
def adminprofileuser(user):
    s = getSettings()
    userData = User.query.filter_by(username=user).first()
    if request.method == 'GET':
        return render_template('admin/users-edit.html',userData=userData,s=s)
    else:
        email = request.form['email']
        name = request.form['name']
        notes = request.form['notes']
        image = request.form['image']
        fb = request.form['fb']
        tw = request.form['tw']
        gp = request.form['gp']
        update = User.query.filter_by(username=user).update(dict(email=email,name=name,description=description,image=image,facebook=fb,twitter=tw,google=gp))
        db.session.commit()
        return redirect("/admin/users/")

@app.route('/admin/users/roles/')
@login_required
def adminusersroles():
    s = getSettings()
    roles = Roles.query.order_by(Roles.rolename).all()
    return render_template('admin/manage-roles.html',roles=roles,s=s)

@app.route('/admin/users/roles/add/',methods=['GET','POST'])
@login_required
def adminaddrole():
    s = getSettings()
    u = User.query.all()
    if request.method == 'POST':
        rolename = request.form['name']
        roledesc = request.form['description']
        atr = request.form.getlist('atr')

        addRole = Roles(rolename,roledesc)
        db.session.add(addRole)
        db.session.commit()

        roleId = Roles.query.filter_by(rolename=rolename).first()

        for u in atr:
            addRoleMember = RoleMembership(roleId.id,u)
            db.session.add(addRoleMember)
            db.session.commit()

        return redirect("/admin/users/roles/")
    return render_template('admin/roles-add.html',s=s,u=u)

@app.route('/admin/users/roles/edit/<roleid>/',methods=['GET','POST'])
@login_required
def admineditrole(roleid):
    s = getSettings()
    u = User.query.all()
    if request.method == 'POST':
        clearRoles = RoleMembership.query.filter_by(role_id=roleid).delete()
        db.session.commit()

        rolename = request.form['name']
        roledesc = request.form['description']
        atr = request.form.getlist('atr')

        u = Roles.query.filter_by(id=roleid).update(dict(rolename=rolename,roledesc=roledesc))
        db.session.commit()

        for u in atr:
            addRoleMember = RoleMembership(roleid,u)
            db.session.add(addRoleMember)
            db.session.commit()
        return redirect("/admin/users/roles/")

    else:
        role = Roles.query.filter_by(id=roleid).first()
        roleMembers = RoleMembership.query.filter_by(role_id=roleid).all()
        return render_template('admin/roles-edit.html',role=role,roleMembers=roleMembers,s=s,u=u)

@app.route('/admin/users/roles/delete/<roleid>/',methods=['GET','POST'])
@login_required
def admindeleterole(roleid):
    s = getSettings()
    if request.args.get('confirmed'):
        delEntry = Roles.query.filter_by(id=roleid).first()
        db.session.delete(delEntry)
        db.session.commit()
        return redirect('/admin/users/roles/')
    else:
        message = 'Are you sure you want to delete ID: ' + roleid + '?<br/><br/>'
        message+= '<a href="/admin/users/roles/delete/' + roleid + '/?confirmed=yes">Click here to delete!</a> | '
        message+= '<a href="/admin/users/roles/">No take me back!</a>'
        return message

@app.route('/admin/changepassword/',methods=['POST'])
@login_required
def changePW():
    s = getSettings()
    username = request.form['username']
    password1 = request.form['password1']
    password2 = request.form['password2']
    if password1 != password2:
        return "Passwords do not match! Click back and try again!"
    password = hashlib.md5(request.form['password1']).hexdigest()
    update = User.query.filter_by(username=username).update(dict(password=password))
    db.session.commit()
    addLogEvent('Password changed for ' + username + ' by ' + current_user.username)
    return redirect(url_for('adminusers'))

@app.route("/admin/logout/")
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('home'))

#######################################################################
# Process content

from urlparse import urljoin
from flask import request
from werkzeug.contrib.atom import AtomFeed

def make_external(url):
    return urljoin(request.url_root, url)

@app.route('/feed/',defaults={'tag': None})
@app.route('/feed/<tag>/')
def recent_feed(tag):
    feed = AtomFeed('Recent Articles', feed_url=request.url, url=request.url_root)
    if tag:
        articles = Posts.query.filter(Posts.post_tags.like('%'+tag+'%')).order_by(Posts.post_date.desc()).limit(15).all()
    else:
        articles = Posts.query.order_by(Posts.post_date.desc()).limit(15).all()
    for article in articles:
        feed.add(article.post_title, unicode(article.post_content),
                 content_type='html',
                 author=article.post_author,
                 url=make_external(article.post_slug),
                 updated=article.post_modified,
                 published=article.post_date)
    return feed.get_response()

@app.route('/<path:path>')
def content(path):
    s = getSettings()
    slug = "/" + path
    # check if path=post_slug, if yes show
    postData = Posts.query.filter_by(post_slug=slug).first()
    if postData is not None:
        authorData = get_author_data(postData.post_author)
        return render_template(s['theme']+'/post.html',postData=postData,s=s,authorData=authorData)
    # check if path=page_slug, if yes show
    pageData = Pages.query.filter_by(page_slug=slug).first()
    if pageData is not None:
        return render_template(s['theme']+'/page.html',pageData=pageData,s=s)
    # else show 404
    return render_template(s['theme']+'/404.html',s=s), 404

#######################################################################
# Error handlers

@app.errorhandler(404)
def not_found_error(error):
    s = getSettings()
    return render_template(s['theme']+'/404.html',s=s), 404

@app.errorhandler(500)
def internal_error(error):
    s = getSettings()
    db.session.rollback()
    return render_template(s['theme']+'/500.html',s=s), 500

