from datetime import datetime
from application import db
import hashlib

#=======================================================
# Standard database tables

class Posts(db.Model):
    __tablename__ = 'site_posts'
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
    post_tags = db.Column(db.Text)

    def __init__(self,author,title,slug,content,subheading,image,tags):
        self.post_author = author
        self.post_title = title
        self.post_subheading = subheading
        self.post_slug = slug
        self.post_content = content
        self.post_image = image
        self.post_date = datetime.utcnow()
        self.post_modified = datetime.utcnow()
        self.post_tags = tags

class Pages(db.Model):
    __tablename__ = 'site_pages'
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
    __tablename__ = 'site_users'
    id = db.Column('user_id',db.Integer,primary_key=True)
    username = db.Column('username',db.String(20),unique=True,index=True)
    password = db.Column('password',db.String(255))
    email = db.Column('email',db.String(50),unique=True,index=True)
    profile = db.Column('profile',db.Integer,default=0)
    registered_on = db.Column('registered_on',db.DateTime)
    admin = db.Column('admin',db.Integer,default=0)
    name = db.Column('name',db.String(255))
    description = db.Column('description',db.Text)
    image = db.Column('image',db.String(255))
    facebook = db.Column('facebook',db.String(255))
    twitter = db.Column('twitter',db.String(255))
    google = db.Column('google',db.String(255))

    def __init__(self,username,password,email):
        self.username = username
        self.password = hashlib.md5(password).hexdigest()
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

class Logs(db.Model):
    __tablename__ = 'site_logs'
    id = db.Column(db.Integer,primary_key=True)
    log_message = db.Column(db.Text)
    log_date = db.Column(db.DateTime)

    def __init__(self,content):
        self.log_message = content
        self.log_date = datetime.utcnow()

class Settings(db.Model):
    __tablename__ = 'site_settings'
    id = db.Column(db.Integer,primary_key=True)
    setting_name = db.Column(db.String(255))
    setting_value = db.Column(db.Text)

    def __init__(self,settingname,settingvalue):
        self.setting_name = settingname
        self.setting_value = settingvalue

class Roles(db.Model):
    __tablename__ = 'site_roles'
    id = db.Column('role_id',db.Integer,primary_key=True)
    rolename = db.Column('rolename',db.String(255))
    roledesc = db.Column('roledesc',db.String(255))

    def __init__(self,name,desc):
        self.rolename = name
        self.roledesc = desc

class RoleMembership(db.Model):
    __tablename__ = 'site_roles_users'
    id = db.Column('ru_id',db.Integer,primary_key=True)
    role_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

    def __init__(self,roleid,userid):
        self.role_id = roleid
        self.user_id = userid
