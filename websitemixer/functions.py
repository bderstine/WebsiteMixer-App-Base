import os
import json
from flask import session
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup

from websitemixer import db
from websitemixer.models import User, Setting, Post, Page

#from config import *


def is_admin():
    check = User.query.filter_by(id=session['user_id']).first()
    return check.is_admin()


def getSettings():
    d = {}
    try:
        for u in Setting.query.all():
            d[u.name] = u.value
    except:
        pass  # ignore errors
    return d


def make_tree(path):
    tree = dict(name=os.path.basename(path), children=[])
    try:
        lst = os.listdir(path)
    except OSError as e:
        print(e)
        pass  # ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                size = os.path.getsize(fn)
                mtime = datetime.utcfromtimestamp(os.path.getmtime(fn))
                tree['children'].append(dict(name=name,
                                             size=size,
                                             mtime=mtime))
    return tree


def first_paragraph(content=""):
    # take content and return just the first <p></p> content,
    # used in blog loop template
    soup = BeautifulSoup(content, "html.parser")
    thespan = soup.find('p')
    if thespan is None:
        return ''
    else:
        return thespan.string


def process_tags(tags):
    rettags = ''
    taglist = [x.strip() for x in tags.split(',')]
    for t in taglist:
        rettags = rettags + '<a href="/tag/'+t+'/">'+t+'</a> '
    return rettags


def get_plugin_info(plugin):
    conf = basedir+'/websitemixer/plugins/'+plugin+'/config.json'
    with open(conf) as data_file:
        data = json.load(data_file)
    return dict(data)

def get_theme_info(theme):
    conf = basedir+'/websitemixer/templates/'+theme+'/config.json'
    with open(conf) as data_file:
        data = json.load(data_file)
    return dict(data)


def get_all_theme_info():
    themeData = []
    dirs = os.walk(basedir+'/websitemixer/templates/')
    for x in dirs:
        if os.path.isfile(x[0]+'/config.json'):
            with open(x[0]+'/config.json') as data_file:
                data = json.load(data_file)
            themeData.append(data)
    return themeData


def get_all_plugin_info():
    pluginData = []
    dirs = os.walk(basedir+'/websitemixer/plugins/')
    for x in dirs:
        if os.path.isfile(x[0]+'/config.json'):
            with open(x[0]+'/config.json') as data_file:
                data = json.load(data_file)
            pluginData.append(data)
    return pluginData

def check_new_settings(k,v):
    check = Setting.query.filter_by(name=k).first()
    if check is None:
        a = Setting(k, v)
        db.session.add(a)
    return True

