from bs4 import BeautifulSoup
import json
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

def get_page_name(pageid):
    page = Pages.query.filter_by(id=pageid).first()
    return page.page_title

def get_handbookpage_num():
    c = Handbook.query.all()
    return len(c)

def get_team_num():
    t = TeamCenter.query.all()
    return len(t)

def get_schedule_num():
    s = ScheduleCenter.query.all()
    return len(s)

def get_schedulelinks_num():
    s = ScheduleLinks.query.all()
    return len(s)

def get_hospitallinks_num():
    s = HospitalLinks.query.all()
    return len(s)

def get_traininglinks_num():
    s = TrainingLinks.query.all()
    return len(s)

def get_marketinglinks_num():
    s = MarketingLinks.query.all()
    return len(s)

def get_formfield_num():
    n = FormFieldTypes.query.all()
    return len(n)

def count_questions(moduleid):
    q = QuizModule.query.filter_by(id=moduleid).first()
    fieldData = json.loads(q.modulefields)
    return len(fieldData)

def get_meetingcentercats_num():
    n = MeetingCenterCategories.query.all()
    return len(n)

def get_policycentercats_num():
    n = PolicyCenterCategories.query.all()
    return len(n)

def get_displayname(sid):
    u = User.query.filter_by(id=sid).first()
    if u is None:
        return "Unknown User"
    if u.profile == 0:
        return u.username
    else:
        d = TeamCenter.query.filter_by(id=u.profile).first()
        return d.teamDisplayName

def getScheduleDates(wso):
    oneday = timedelta(days=1)
    oneweek = timedelta(days=7)
    year = 2014

    start = date.today()
    if date.today().weekday() != wso:
        start -= oneweek

    days = []
    while start.weekday() != wso:
        start += oneday
        #days = []
    while start.year == year:
        days.append(start)
        start += oneweek

    return days

def getScheduleData(userid,scheduledate):
    get = ScheduleData.query.filter_by(sd_user=userid,sd_date=scheduledate).first()
    if get == None:
        return ""
    else:
        return get.sd_entry

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

def buildFormField(d):
    #get field from db, update and return html
    print d
    return "<h3>" + d['fieldtype'] + "</h3>"

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

def get_theme_info():
    themeData = []
    dirs = os.walk(basedir+'/application/templates/')
    for x in dirs:
        if os.path.isfile(x[0]+'/config.json'):
            with open(x[0]+'/config.json') as data_file:    
                data = json.load(data_file)
            themeData.append(data)
    print themeData
    return themeData



