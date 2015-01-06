import os, time, re, urllib2
from flask import Flask, Response, session, request, url_for, redirect, render_template, abort, g, send_from_directory
from flask.ext.moment import Moment
from flask.ext.login import login_user , logout_user , current_user , login_required
from werkzeug.routing import BaseConverter
from werkzeug import secure_filename
from app import app
from models import *
from config import *

import feedparser
from feedparser import _parse_date as parse_date
from bs4 import BeautifulSoup

from functions import *

#######################################################################
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
    c = 0
    instagram = []
    feedurl = "http://iconosquare.com/feed/bderstine528"
    d = feedparser.parse(feedurl)
    for e in d.entries:
        soup = BeautifulSoup(e.summary)
        rawimage = soup.findAll('img')
        image = str(rawimage[0]).replace('<img src="','').replace('"/>','')
        link = e.link
	pub_date = e.published_parsed
        if c < 8:
            instagram.append({"image":image,"link":link,"pub_date":pub_date})
        c += 1
    return render_template('index.html',blogData=blogData,instagram=instagram,s=s)

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
def adminclearlogs():
    #s = getSettings()
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
        update = Settings.query.filter_by(setting_name='siteUrl').update(dict(setting_value=request.form['siteUrl']))
        update = Settings.query.filter_by(setting_name='headerBackground').update(dict(setting_value=request.form['headerBackground']))
        update = Settings.query.filter_by(setting_name='headerForeground').update(dict(setting_value=request.form['headerForeground']))
        update = Settings.query.filter_by(setting_name='colorLinks').update(dict(setting_value=request.form['colorLinks']))
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
    tree=make_tree(UPLOAD_FOLDER)
    newlist = sorted(tree['children'], key=lambda k: k['name'])
    data = {}
    data['children'] = newlist
    return render_template('admin/manage-files.html',tree=data,s=s)

@app.route('/admin/users/')
@login_required
def adminusers():
    s = getSettings()
    userData = User.query.order_by(User.username).all()
    return render_template('admin/manage-users.html',userData=userData,s=s)

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
    userData = User.query.filter_by(username=user).first()
    if request.method == 'GET':
        tc = TeamCenter.query.order_by(TeamCenter.teamDisplayName).all()
        return render_template('admin/edituser.html',userData=userData,s=s,tc=tc)
    else:
        tcemail = request.form['email']
        tcprofile = request.form['profile']
        update = User.query.filter_by(username=user).update(dict(email=tcemail,profile=tcprofile))
        db.session.commit()
        
        teamLink = '/user-center/' + str(userData.id) + '/'
        u = TeamCenter.query.filter_by(id=tcprofile).update(dict(teamLink=teamLink))
        db.session.commit()

        return redirect("/admin/users/")

@app.route('/admin/posts/add/',methods=['GET','POST'])
@login_required
def addpost():
    s = getSettings()
    if request.method == 'GET':
        return render_template('admin/posts-add.html',s=s)
    else:
        addPost = Posts(current_user.username,request.form['title'],request.form['slug'],request.form['content'],request.form['subheading'],request.form['featureimg'])
        db.session.add(addPost)
        db.session.commit()
        return redirect("/admin/posts/")

@app.route('/admin/pages/add/',methods=['GET','POST'])
@login_required
def addpage():
    s = getSettings()
    if request.method == 'GET':
        return render_template('admin/pages-add.html',s=s)
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
        addLogEvent('Post "' + request.form['title'] + '" was updated by ' + current_user.username)
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
        update = Pages.query.filter_by(id=id).update(dict(page_title=form_title,page_slug=form_slug,page_content=form_content,page_subheading=form_subheading,page_image=form_image,page_modified=datetime.utcnow()))
        db.session.commit()
        addLogEvent('Page "' + form_title + '" was updated by ' + current_user.username)
        return redirect("/admin/pages/")

@app.route('/admin/deletepost/<id>/')
@login_required
def deletepost(id):
    s = getSettings()
    if request.args.get('confirmed'):
        postData = Posts.query.filter_by(id=id).first()
        db.session.delete(postData)
        db.session.commit()
        addLogEvent('Post "' + postData.post_title + '" was deleted by ' + current_user.username)
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
        addLogEvent('Page "' + pageData.page_title + '" was deleted by ' + current_user.username)
        return redirect("/admin/pages/")
    else:
        message = 'Are you sure you want to delete ID: ' + id + '?<br/><br/>'
        message+= '<a href="/admin/deletepage/' + id + '/?confirmed=yes">Click here to delete!</a> | '
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
        addLogEvent('File "' + filename + '" was deleted by ' + current_user.username)
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
        addLogEvent('User "' + userData.username + '" was deleted by ' + current_user.username)
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

