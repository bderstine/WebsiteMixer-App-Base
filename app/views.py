import os, time, re, urllib2
from flask import Flask, Response, session, request, url_for, redirect, render_template, abort, g, send_from_directory
from flask.ext.moment import Moment
from flask.ext.login import login_user , logout_user , current_user , login_required
from werkzeug.routing import BaseConverter
from werkzeug import secure_filename
from app import app
from models import *
from config import *

#######################################################################
from flask.ext.login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

def addEvent(eventText):
    e = Events(eventText)
    db.session.add(e)
    db.session.commit()

def getSettings():
    d = {}
    settings = Settings.query.all()
    for u in Settings.query.all():
        d[u.setting_name] = u.setting_value
    return d

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def make_tree(path):
    tree = dict(name=os.path.basename(path), children=[])
    try: lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                size = os.path.getsize(fn)
                #mtime = time.ctime(os.path.getmtime(fn))
                #mtime = os.path.getmtime(fn)
                mtime = datetime.utcfromtimestamp(os.path.getmtime(fn))
                tree['children'].append(dict(name=name,size=size,mtime=mtime))
    return tree

#######################################################################

@app.route('/')
def home():
    s = getSettings()
    blogData = Posts.query.order_by(Posts.post_date.desc()).all()
    return render_template('index.html',blogData=blogData,s=s)

@app.route('/login/',methods=['GET','POST'])
def login():
    s = getSettings()
    error = None
    if request.method == 'GET':
        return render_template('login.html',s=s)
    username = request.form['username']
    password = request.form['password']
    registered_user = User.query.filter_by(username=username,password=password).first()
    if registered_user is None:
        addEvent('Failed login attempt for ' + username)
        return redirect(url_for('login'))
    login_user(registered_user)
    addEvent('User ' + username + ' successfully logged in.')
    return redirect(request.args.get('next') or url_for('admin'))

#######################################################################
# Admin handlers

@app.route('/admin/')
@login_required
def admin():
    s = getSettings()
    eventData = Events.query.order_by(Events.event_date.desc()).limit(25)
    return render_template('admin/index.html',eventData=eventData,s=s)

@app.route('/admin/posts/')
@login_required
def adminposts():
    s = getSettings()
    postData = Posts.query.order_by(Posts.post_date.desc()).all()
    return render_template('admin/manage-posts.html',postData=postData,s=s)

@app.route('/admin/pages/')
@login_required
def adminpages():
    s = getSettings()
    pageData = Pages.query.order_by(Pages.page_title).all()
    return render_template('admin/manage-pages.html',pageData=pageData,s=s)

@app.route('/admin/settings/',methods=['GET','POST'])
@login_required
def manageSettings():
    s = getSettings()
    if request.method == 'POST':
        update = Settings.query.filter_by(setting_name='siteName').update(dict(setting_value=request.form['siteName']))
        update = Settings.query.filter_by(setting_name='siteSubheading').update(dict(setting_value=request.form['siteSubheading']))
        update = Settings.query.filter_by(setting_name='siteUrl').update(dict(setting_value=request.form['siteUrl']))
        update = Settings.query.filter_by(setting_name='headerBackground').update(dict(setting_value=request.form['headerBackground']))
        update = Settings.query.filter_by(setting_name='headerForeground').update(dict(setting_value=request.form['headerForeground']))
        db.session.commit()
        return redirect(url_for('manageSettings'))
    return render_template('admin/manage-settings.html',s=s)

@app.route('/admin/files/',methods=['GET','POST'])
@login_required
def manageFiles():
    s = getSettings()
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER,filename))
            return redirect(url_for('manageFiles'))
    return render_template('admin/manage-files.html',tree=make_tree(UPLOAD_FOLDER),s=s)

@app.route('/admin/users/')
@login_required
def adminusers():
    s = getSettings()
    userData = User.query.order_by(User.username).all()
    return render_template('admin/manage-users.html',userData=userData,s=s)

@app.route('/admin/adduser/',methods=['GET','POST'])
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
    return render_template('admin/adduser.html',s=s)

@app.route('/admin/profile/',methods=['GET','POST'])
@login_required
def adminprofile():
    s = getSettings()
    if request.method == 'GET':
        userData = User.query.filter_by(username=current_user.username).first()
        return render_template('admin/edituser.html',userData=userData,s=s)
    else:
        update = User.query.filter_by(username=current_user.username).update(dict(email=request.form['email']))
        db.session.commit()
        return redirect("/admin/users/")

@app.route('/admin/profile/<user>/',methods=['GET','POST'])
@login_required
def adminprofileuser(user):
    s = getSettings()
    if request.method == 'GET':
        userData = User.query.filter_by(username=user).first()
        return render_template('admin/edituser.html',userData=userData,s=s)
    else:
        update = User.query.filter_by(username=user).update(dict(email=request.form['email']))
        db.session.commit()
        return redirect("/admin/users/")

@app.route('/admin/addpost/',methods=['GET','POST'])
@login_required
def addpost():
    s = getSettings()
    if request.method == 'GET':
        return render_template('admin/addpost.html',s=s)
    else:
        addPost = Posts(current_user.username,request.form['title'],request.form['slug'],request.form['content'],request.form['subheading'],request.form['featureimg'])
        db.session.add(addPost)
        db.session.commit()
        return redirect("/admin/posts/")

@app.route('/admin/addpage/',methods=['GET','POST'])
@login_required
def addpage():
    s = getSettings()
    if request.method == 'GET':
        return render_template('admin/addpage.html',s=s)
    else:
        addPage = Pages(request.form['title'],request.form['slug'],request.form['content'],request.form['subheading'],request.form['featureimg'])
        db.session.add(addPage)
        db.session.commit()
        return redirect("/admin/pages/")

@app.route('/admin/editpost/<id>/',methods=['GET','POST'])
@login_required
def editpost(id):
    s = getSettings()
    if request.method == 'GET':
        postData = Posts.query.filter_by(id=id).first()
        return render_template('admin/editpost.html',id=id,postData=postData,s=s)
    else:
        update = Posts.query.filter_by(id=id).update(dict(post_title=request.form['title'],post_slug=request.form['slug'],post_content=request.form['content'],post_subheading=request.form['subheading'],post_image=request.form['featureimg'],post_modified=datetime.utcnow()))
        db.session.commit()
        addEvent('Post "' + request.form['title'] + '" was updated by ' + current_user.username)
        return redirect("/admin/posts/")

@app.route('/admin/editpage/<id>/',methods=['GET','POST'])
@login_required
def editpage(id):
    s = getSettings()
    if request.method == 'GET':
        pageData = Pages.query.filter_by(id=id).first()
        return render_template('admin/editpage.html',id=id,pageData=pageData,s=s)
    else:
        form_title=request.form['title']
        form_slug=request.form['slug']
        form_content=request.form['content']
        form_subheading=request.form['subheading']
        form_image=request.form['featureimg']
        update = Pages.query.filter_by(id=id).update(dict(page_title=form_title,page_slug=form_slug,page_content=form_content,page_subheading=form_subheading,page_image=form_image))
        db.session.commit()
        addEvent('Page "' + form_title + '" was updated by ' + current_user.username)
        return redirect("/admin/pages/")

@app.route('/admin/deletepost/<id>/')
@login_required
def deletepost(id):
    s = getSettings()
    if request.args.get('confirmed'):
        postData = Posts.query.filter_by(id=id).first()
        db.session.delete(postData)
        db.session.commit()
        addEvent('Post "' + postData.post_title + '" was deleted by ' + current_user.username)
        return redirect("/admin/posts/")
    else:
        message = 'Are you sure you want to delete ID: ' + id + '?<br/><br/>'
        message+= '<a href="/admin/deletepost/' + id + '/?confirmed=yes">Click here to delete!</a> | '
        message+= '<a href="/admin/posts/">No take me back!</a>'
        return message

@app.route('/admin/deletepage/<id>/')
@login_required
def deletepage(id):
    s = getSettings()
    if request.args.get('confirmed'):
        pageData = Pages.query.filter_by(id=id).first()
        db.session.delete(pageData)
        db.session.commit()
        addEvent('Page "' + pageData.page_title + '" was deleted by ' + current_user.username)
        return redirect("/admin/pages/")
    else:
        message = 'Are you sure you want to delete ID: ' + id + '?<br/><br/>'
        message+= '<a href="/admin/deletepost/' + id + '/?confirmed=yes">Click here to delete!</a> | '
        message+= '<a href="/admin/">No take me back!</a>'
        return message

@app.route('/admin/delete-file/')
@login_required
def deleteFile():
    s = getSettings()
    filename = request.args.get('filename')
    if request.args.get('confirmed'):
        os.remove(os.path.join(UPLOAD_FOLDER,filename))
        return redirect(url_for('manageFiles'))
        addEvent('File "' + filename + '" was deleted by ' + current_user.username)
    else:
        message = 'Are you sure you want to delete the file: ' + filename + '?<br/><br/>'
        message+= '<a href="/admin/delete-file/?filename=' + filename + '&confirmed=yes">Click here to delete!</a> | '
        message+= '<a href="/admin/manage-uploads/">No take me back!</a>'
        return message

@app.route('/admin/deleteuser/<id>/')
@login_required
def deleteUser(id):
    userData = User.query.filter_by(id=id).first()
    if request.args.get('confirmed'):
        db.session.delete(userData)
        db.session.commit()
        addEvent('User "' + userData.username + '" was deleted by ' + current_user.username)
        return redirect(url_for('adminusers'))
    else:
        message = 'Are you sure you want to delete the user: ' + userData.username + '?<br/><br/>'
        message+= '<a href="/admin/deleteuser/' + id + '/?confirmed=yes">Click here to delete!</a> | '
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
    update = User.query.filter_by(username=username).update(dict(password=password1))
    db.session.commit()
    addEvent('Password changed for ' + username + ' by ' + current_user.username)
    return redirect(url_for('adminusers'))

@app.route("/admin/logout/")
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('home'))

#######################################################################
# Process content

@app.route('/<path:path>')
def content(path):
    s = getSettings()
    slug = "/" + path
    # check if path=post_slug, if yes show
    postData = Posts.query.filter_by(post_slug=slug).first()
    if postData is not None:
        return render_template('post.html',postData=postData,s=s)
    # check if path=page_slug, if yes show
    pageData = Pages.query.filter_by(page_slug=slug).first()
    if pageData is not None:
        return render_template('page.html',pageData=pageData,s=s)
    # else show 404
    return render_template('404.html',s=s), 404

#######################################################################
# Error handlers

@app.errorhandler(404)
def not_found_error(error):
    s = getSettings()
    return render_template('404.html',s=s), 404

@app.errorhandler(500)
def internal_error(error):
    s = getSettings()
    db.session.rollback()
    return render_template('500.html',s=s), 500

