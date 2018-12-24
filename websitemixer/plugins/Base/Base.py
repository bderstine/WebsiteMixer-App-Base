import os
from flask import render_template, redirect, request, url_for, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.contrib.atom import AtomFeed

from websitemixer import app
from websitemixer.models import *
from websitemixer.functions import *


@app.route('/', defaults={'tag': None})
@app.route('/tag/<tag>/')
def home(tag):
    if 'UPLOAD_FOLDER' not in globals():
        return redirect('/setup/step1/')

    s = getSettings()
    if tag:
        blogData = Post.query.filter(Post.tags.like('%'+tag+'%')).\
                       order_by(Post.date.desc()).all()
    else:
        blogData = Post.query.order_by(Post.date.desc()).limit(5)
    return render_template(s['theme'] + '/index.html', blogData=blogData, s=s)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    s = getSettings()
    error = None
    if request.method == 'GET':
        return render_template(s['theme'] + '/login.html', s=s)
    username = request.form['username']
    password = request.form['password']
    registered_user = User.validate(username, password)
    if registered_user is False:
        return redirect('/login/')
    u = User.query.filter_by(username=username).first()
    login_user(u)
    return redirect('/admin/')


@app.route("/logout/")
def logout():
    session.clear()
    logout_user()
    return redirect('/')


@app.route('/feed/', defaults={'tag': None})
@app.route('/feed/<tag>/')
def recent_feed(tag):
    feed = AtomFeed('Recent Articles', feed_url=request.url,
                    url=request.url_root)
    if tag:
        articles = Post.query.filter(Post.tags.like('%'+tag+'%'))\
                       .order_by(Post.date.desc()).limit(15).all()
    else:
        articles = Post.query.order_by(Post.date.desc()).limit(15).all()
    for article in articles:
        feed.add(article.title, str(article.content),
                 content_type='html',
                 author=article.author,
                 url=make_external(article.slug),
                 updated=article.modified,
                 published=article.date)
    return feed.get_response()


@app.route('/<path:path>')
def content(path):
    s = getSettings()
    slug = "/" + path
    # check if path=slug, if yes show
    postData = Post.query.filter_by(slug=slug).first()
    if postData is not None:
        return render_template(s['theme']+'/post.html', postData=postData, s=s)
    # check if path=slug, if yes show
    pageData = Page.query.filter_by(slug=slug).first()
    if pageData is not None:
        return render_template(s['theme'] + '/page.html',
                               pageData=pageData,
                               s=s)
    # else show 404
    return render_template(s['theme'] + '/404.html', s=s), 404

#######################################################################
# Error handlers


@app.errorhandler(404)
def not_found_error(error):
    s = getSettings()
    return render_template(s['theme'] + '/404.html', s=s), 404


@app.errorhandler(500)
def internal_error(error):
    s = getSettings()
    db.session.rollback()
    return render_template(s['theme'] + '/500.html', s=s, error=error), 500
