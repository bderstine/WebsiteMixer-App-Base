import os, shutil, signal, urllib, urllib2, zipfile
from flask import render_template, redirect, request, g
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed
from werkzeug import secure_filename

from websitemixer import app
from websitemixer.models import *
from websitemixer.functions import *
from config import *

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

##############################################################################

@app.route('/admin/')
def admin():
    return redirect('/admin/dashboard/')

@app.route('/admin/dashboard/')
@login_required
def admindashboard():
    s = getSettings()
    eventData = Logs.query.order_by(Logs.log_date.desc()).limit(25)
    return render_template('Admin/index.html',eventData=eventData,s=s)

@app.route('/admin/clear-logs/',methods=['GET','POST'])
@login_required
def adminclearlogs():
    #s = getSettings()
    if request.args.get('confirmed'):
        logs = Logs.query.all()
        for e in logs:
            db.session.delete(e)
        return redirect("/admin/")
    else:
        message = 'Are you sure you want to delete ALL logs?<br/><br/>'
        message+= '<a href="/admin/clear-logs/?confirmed=yes">Click here to delete!</a> | '
        message+= '<a href="/admin/">No take me back!</a>'
        return message

@app.route('/admin/posts/')
@login_required
def adminposts():
    s = getSettings()
    postData = Post.query.order_by(Post.date.desc()).all()
    return render_template('Admin/manage-posts.html',postData=postData,s=s)

@app.route('/admin/pages/')
@login_required
def adminpages():
    s = getSettings()
    pageData = Page.query.order_by(Page.title).all()
    return render_template('Admin/manage-pages.html',pageData=pageData,s=s)

@app.route('/admin/settings/',methods=['GET','POST'])
@login_required
def manageSettings():
    s = getSettings()
    if request.method == 'POST':
        for key, value in request.form.iteritems():
            check = Setting.query.filter_by(name=key).first()
            if check is None:
                a = Setting(key,value)
                db.session.add(a)
            else:
                update = Setting.query.filter_by(name=key).update(dict(value=value))
            db.session.commit()
        return redirect('/admin/settings/')
    return render_template('Admin/manage-settings.html',s=s)

@app.route('/admin/files/',methods=['GET','POST'])
@login_required
def manageFiles():
    s = getSettings()
    if request.method == 'POST':
        file = request.files['file']
        #if file and allowed_file(file.filename):
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER,filename))
            return redirect('/admin/files/')
    tree=make_tree(UPLOAD_FOLDER)
    newlist = sorted(tree['children'], key=lambda k: k['name'])
    data = {}
    data['children'] = newlist
    return render_template('Admin/manage-files.html',tree=data,s=s)

@app.route('/admin/users/')
@login_required
def adminusers():
    s = getSettings()
    userData = User.query.order_by(User.username).all()
    return render_template('Admin/manage-users.html',userData=userData,s=s)

@app.route('/admin/users/add/',methods=['GET','POST'])
@login_required
def adminadduser():
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
        addUser = User(username,password1,email)
        db.session.add(addUser)
        db.session.commit()
        return redirect("/admin/users/")
    return render_template('Admin/users-add.html',s=s)

@app.route('/admin/users/profile/', defaults={'user':None}, methods=['GET','POST'])
@app.route('/admin/users/profile/<user>/', methods=['GET','POST'])
@login_required
def adminprofileuser(user):
    s = getSettings()
    if user is None:
        user = current_user.username
    userData = User.query.filter_by(username=user).first()
    if request.method == 'GET':
        return render_template('Admin/users-edit.html',userData=userData,s=s)
    else:
        email = request.form['email']
        fullname = request.form['fullname']
        image = request.form['image']
        facebook = request.form['facebook']
        twitter = request.form['twitter']
        google = request.form['google']
        update = User.query.filter_by(username=user).update(dict(email=email,name=fullname,image=image,facebook=facebook,twitter=twitter,google=google))
        db.session.commit()
        return redirect("/admin/users/")

@app.route('/admin/posts/add/',methods=['GET','POST'])
@login_required
def addpost():
    s = getSettings()
    if request.method == 'GET':
        return render_template('Admin/posts-add.html',s=s)
    else:
        addPost = Post(current_user.username,request.form['title'],request.form['slug'],request.form['content'],request.form['subheading'],request.form['featureimg'],request.form['tags'])
        db.session.add(addPost)
        db.session.commit()
        return redirect("/admin/posts/")

@app.route('/admin/pages/add/',methods=['GET','POST'])
@login_required
def addpage():
    s = getSettings()
    if request.method == 'GET':
        return render_template('Admin/pages-add.html',s=s)
    else:
        addPage = Page(request.form['title'],request.form['slug'],request.form['content'],request.form['subheading'],request.form['featureimg'])
        db.session.add(addPage)
        db.session.commit()
        return redirect("/admin/pages/")

@app.route('/admin/posts/edit/<id>/',methods=['GET','POST'])
@login_required
def editpost(id):
    s = getSettings()
    if request.method == 'GET':
        postData = Post.query.filter_by(id=id).first()
        return render_template('Admin/posts-edit.html',id=id,postData=postData,s=s)
    else:
        update = Post.query.filter_by(id=id).update(dict(title=request.form['title'],slug=request.form['slug'],content=request.form['content'],subheading=request.form['subheading'],image=request.form['featureimg'],modified=datetime.utcnow(),tags=request.form['tags']))
        db.session.commit()
        return redirect("/admin/posts/")

@app.route('/admin/pages/edit/<id>/',methods=['GET','POST'])
@login_required
def editpage(id):
    s = getSettings()
    if request.method == 'GET':
        pageData = Page.query.filter_by(id=id).first()
        return render_template('Admin/pages-edit.html',id=id,pageData=pageData,s=s)
    else:
        form_title=request.form['title']
        form_slug=request.form['slug']
        form_content=request.form['content']
        form_subheading=request.form['subheading']
        form_image=request.form['featureimg']
        update = Page.query.filter_by(id=id).update(dict(title=form_title,slug=form_slug,content=form_content,subheading=form_subheading,image=form_image,modified=datetime.utcnow()))
        db.session.commit()
        return redirect("/admin/pages/")

@app.route('/admin/posts/delete/<id>/')
@login_required
def deletepost(id):
    s = getSettings()
    if request.args.get('confirmed'):
        postData = Post.query.filter_by(id=id).first()
        db.session.delete(postData)
        db.session.commit()
        return redirect("/admin/posts/")
    else:
        message = 'Are you sure you want to delete ID: ' + id + '?<br/><br/>'
        message+= '<a href="/admin/posts/delete/' + id + '/?confirmed=yes">Click here to delete!</a> | '
        message+= '<a href="/admin/posts/">No take me back!</a>'
        return message

@app.route('/admin/pages/delete/<id>/')
@login_required
def deletepage(id):
    s = getSettings()
    if request.args.get('confirmed'):
        pageData = Page.query.filter_by(id=id).first()
        db.session.delete(pageData)
        db.session.commit()
        return redirect("/admin/pages/")
    else:
        message = 'Are you sure you want to delete ID: ' + id + '?<br/><br/>'
        message+= '<a href="/admin/pages/delete/' + id + '/?confirmed=yes">Click here to delete!</a> | '
        message+= '<a href="/admin/">No take me back!</a>'
        return message

@app.route('/admin/files/delete/')
@login_required
def deleteFile():
    s = getSettings()
    filename = request.args.get('filename')
    if request.args.get('confirmed'):
        os.remove(os.path.join(UPLOAD_FOLDER,filename))
        return redirect('/admin/files/')
    else:
        message = 'Are you sure you want to delete the file: ' + filename + '?<br/><br/>'
        message+= '<a href="/admin/files-delete/?filename=' + filename + '&confirmed=yes">Click here to delete!</a> | '
        message+= '<a href="/admin/manage-uploads/">No take me back!</a>'
        return message

@app.route('/admin/users/delete/<id>/')
@login_required
def deleteUser(id):
    userData = User.query.filter_by(id=id).first()
    if request.args.get('confirmed'):
        db.session.delete(userData)
        db.session.commit()
        return redirect('/admin/users/')
    else:
        message = 'Are you sure you want to delete the user: ' + userData.username + '?<br/><br/>'
        message+= '<a href="/admin/users/delete/' + id + '/?confirmed=yes">Click here to delete!</a> | '
        message+= '<a href="/admin/users/">No take me back!</a>'
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
    user = User.query.filter_by(username=username).first()
    encpass = user.set_password(password1)
    update = User.query.filter_by(username=username).update(dict(password=encpass))
    db.session.commit()
    return redirect('/admin/users/')

@app.route('/admin/themes/')
@login_required
def adminthemes():
    s = getSettings()
    activeTheme = get_theme_info(s['theme'])
    themeData = get_all_theme_info()
    return render_template('Admin/manage-themes.html',s=s,themeData=themeData,activeTheme=activeTheme)

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

    return render_template('Admin/themes-add.html',s=s,themeData=themeData)

@app.route('/admin/themes/install/<theme>/')
@login_required
def adminthemeinstall(theme):
    s = getSettings()
    url = "http://websitemixer.com/api/themes/"+theme+"/"
    response = urllib.urlopen(url)
    themeData = json.loads(response.read())
    themeFile = urllib2.urlopen(themeData['json_list'][0]['theme_repo']+'/archive/master.zip')
    saveDir = basedir+'/websitemixer/templates/'+themeData['json_list'][0]['theme_directory']
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
            src = basedir+'/websitemixer/static/'+d
            dst = basedir+'/websitemixer/templates/'+activeTheme['basics']['directory']+'/'
            try:
                shutil.move(src,dst)
            except Exception as e:
                continue
    #move newTheme assets to static folder
    newTheme = get_theme_info(theme)
    if 'assets' in newTheme.keys():
        for d in newTheme['assets'].values():
            src = basedir+'/websitemixer/templates/'+newTheme['basics']['directory']+'/'+d
            dst = basedir+'/websitemixer/static/'
            try:
                shutil.move(src,dst)
            except Exception as e:
                continue
    #update setting in db for newtheme
    u = Setting.query.filter_by(name='theme').update(dict(value=theme))
    db.session.commit()
    return redirect("/admin/themes/")

@app.route('/admin/themes/delete/<theme>/')
@login_required
def adminthemesdelete(theme):
    s = getSettings()
    if request.args.get('confirmed'):
        shutil.rmtree(basedir+'/websitemixer/templates/'+theme)
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
    return render_template('Admin/manage-plugins.html',s=s,pluginData=pluginData)

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

    return render_template('Admin/plugins-add.html',s=s,pluginData=pluginData)

@app.route('/admin/plugins/install/<plugin>/')
@login_required
def adminpluginsinstall(plugin):
    s = getSettings()
    url = "http://websitemixer.com/api/plugins/"+plugin+"/"
    response = urllib.urlopen(url)
    pluginData = json.loads(response.read())
    pluginFile = urllib2.urlopen(pluginData['json_list'][0]['plugin_repo']+'/archive/master.zip')
    saveDir = basedir+'/websitemixer/plugins/'+pluginData['json_list'][0]['plugin_directory']
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
        shutil.rmtree(basedir+'/websitemixer/plugins/'+plugin)
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

