from datetime import datetime
from app import db

class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key=True)
    post_author = db.Column(db.String(255))
    post_title = db.Column(db.String(255))
    post_subheading = db.Column(db.String(255))
    post_slug = db.Column(db.String(255))
    post_content = db.Column(db.Text)
    post_image = db.Column(db.Text)
    post_status = db.Column(db.Integer, default = 1)
    comment_status = db.Column(db.Integer, default = 1)
    post_date = db.Column(db.DateTime, default = datetime.utcnow())
    post_modified = db.Column(db.DateTime, default = datetime.utcnow())

    def __init__(self,author,title,slug,content,subheading,image):
        self.post_author = author
        self.post_title = title
        self.post_subheading = subheading
        self.post_slug = slug
        self.post_content = content
        self.post_image = image

class Pages(db.Model):
    __tablename__ = 'pages'
    id = db.Column(db.Integer,primary_key=True)
    page_title = db.Column(db.String(255))
    page_subheading = db.Column(db.String(255))
    page_slug = db.Column(db.String(255))
    page_content = db.Column(db.Text)
    page_image = db.Column(db.Text)
    page_status = db.Column(db.Integer, default = 1)
    comment_status = db.Column(db.Integer, default = 0)
    page_modified = db.Column(db.DateTime, default = datetime.utcnow())
    page_parent = db.Column(db.Integer, default = 0)

    def __init__(self,title,slug,content,subheading,image):
        self.page_title = title
        self.page_subheading = subheading
        self.page_slug = slug
        self.page_content = content
        self.page_image = image

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column('user_id',db.Integer,primary_key=True)
    username = db.Column('username',db.String(20),unique=True,index=True)
    password = db.Column('password',db.String(10))
    email = db.Column('email',db.String(50),unique=True,index=True)
    registered_on = db.Column('registered_on',db.DateTime)
    admin = db.Column('admin',db.Integer,default=0)

    def __init__(self,username,password,email):
        self.username = username
        self.password = password
        self.email = email
        self.registered_on = datetime.utcnow()
        self.is_admin = 0

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def is_admin(self):
        if self.admin==1:
            return True
        else:
            return False

    def __repr__(self):
        return '<User %r>' % (self.username)

class Events(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer,primary_key=True)
    event_message = db.Column(db.Text)
    event_date = db.Column(db.DateTime)

    def __init__(self,content):
        self.event_message = content
        self.event_date = datetime.utcnow()

class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer,primary_key=True)
    setting_name = db.Column(db.String(255))
    setting_value = db.Column(db.Text)

    def __init__(self,settingname,settingvalue):
        self.setting_name = settingname
        self.setting_value = settingvalue

