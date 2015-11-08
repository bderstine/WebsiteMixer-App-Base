from bs4 import BeautifulSoup
import json, collections, ast
from application import app
from models import *
from config import *

from datetime import date, datetime, timedelta

def addLogEvent(eventText):
    e = Logs(eventText)
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
    except OSError as e:
        print e
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                size = os.path.getsize(fn)
                mtime = datetime.utcfromtimestamp(os.path.getmtime(fn))
                tree['children'].append(dict(name=name,size=size,mtime=mtime))
    return tree

def get_role_num(roleid):
    r = RoleMembership.query.filter_by(role_id=roleid).all()
    return len(r)

def get_rolename(rid):
    r = Roles.query.filter_by(id=rid).first()
    if r is None:
        return "Unknown Role"
    else:
        return r.rolename

def get_page_name(pageid):
    page = Pages.query.filter_by(id=pageid).first()
    return page.page_title

def get_displayname(sid):
    u = User.query.filter_by(id=sid).first()
    if u is None:
        return "Unknown User"
    if u.name is None:
        return u.username
    else:
        return u.name

def incrementDate(d,i):
    increment = timedelta(days=i)
    d += increment
    return d

def getDOW(d):
    dow = d.weekday()
    if dow == 0:
        dowText = "Monday"
    elif dow == 1:
        dowText = "Tuesday"
    elif dow == 2:
        dowText = "Wednesday"
    elif dow == 3:
        dowText = "Thursday"
    elif dow == 4:
        dowText = "Friday"
    elif dow == 5:
        dowText = "Saturday"
    elif dow == 6:
        dowText = "Sunday"
    return dowText

def cleansyntax(content):
    if content is not None:
        doclines = content.splitlines()
        c = ''.join(doclines)
        c = c.replace('\'','\\\'')
        return c

def get_option_value(d,num):
    search = "value"+num
    return d[search]

def first_paragraph(content):
    #take content and return just the first <p></p> content, used in blog loop template
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

def get_author_data(author):
    get_user = User.query.filter_by(username=author).first()
    return get_user

def get_theme_info(theme):
    conf = basedir+'/application/templates/'+theme+'/config.json'
    with open(conf) as data_file:
        data = json.load(data_file)
    return dict(data)

def get_all_theme_info():
    themeData = []
    dirs = os.walk(basedir+'/application/templates/')
    for x in dirs:
        if os.path.isfile(x[0]+'/config.json'):
            with open(x[0]+'/config.json') as data_file:    
                data = json.load(data_file)
            themeData.append(data)
    return themeData

def get_all_plugin_info():
    pluginData = []
    dirs = os.walk(basedir+'/application/plugins/')
    for x in dirs:
        if os.path.isfile(x[0]+'/config.json'):
            with open(x[0]+'/config.json') as data_file:
                data = json.load(data_file)
            pluginData.append(data)
    return pluginData

def get_all_menu_info():
    menuData = []
    menus = Menus.query.all()
    for m in menus:
        menuData.append(m)
    return menuData

def get_adminnav():
    am = get_all_plugin_info()
    an = {}
    for a in am:
        if a['adminnav']:
            an.update(a['adminnav'])
    adminnav = collections.OrderedDict(sorted(an.items()))
    return adminnav.iteritems()

def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data

#This is the required_roles decorator
def required_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            k = any(x in get_user_roles() for x in roles)
            if k is False:
                return 'You do not have access to this page!'
            return f(*args, **kwargs)
        return wrapped
    return wrapper

#This is used in the required_roles decorator
def get_current_user_role():
    user = User.query.filter_by(username=current_user.username).first()
    if user.is_admin():
        return 'admin'
    else:
        return 'user'
