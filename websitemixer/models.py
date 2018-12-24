# -*- coding: utf-8 -*-
from datetime import datetime
import hashlib
import passlib.hash

from websitemixer import db

user_roles = db.Table(
    'user_roles',
    db.Column(
        'id',
        db.Integer,
        primary_key=True,
        autoincrement=True),
    db.Column(
        'user_id',
        db.Integer,
        db.ForeignKey('user.id', ondelete='cascade')),
    db.Column(
        'role_id',
        db.Integer,
        db.ForeignKey('role.id', ondelete='cascade'))
)

user_posts = db.Table(
    'user_posts',
    db.Column(
        'id',
        db.Integer,
        primary_key=True,
        autoincrement=True),
    db.Column(
        'user_id',
        db.Integer,
        db.ForeignKey('user.id')),
    db.Column(
        'post_id',
        db.Integer,
        db.ForeignKey('post.id'))
)

user_comments = db.Table(
    'user_comments',
    db.Column(
        'id',
        db.Integer,
        primary_key=True,
        autoincrement=True),
    db.Column(
        'user_id',
        db.Integer,
        db.ForeignKey('user.id')),
    db.Column(
        'comment_id',
        db.Integer,
        db.ForeignKey('comment.id'))
)

user_preferences = db.Table(
    'user_preferences',
    db.Column(
        'id',
        db.Integer,
        primary_key=True,
        autoincrement=True),
    db.Column(
        'user_id',
        db.Integer,
        db.ForeignKey('user.id', ondelete='cascade')),
    db.Column(
        'preference_id',
        db.Integer,
        db.ForeignKey('preference.id', ondelete='cascade'))
)

post_categories = db.Table(
    'post_categories',
    db.Column(
        'id',
        db.Integer,
        primary_key=True,
        autoincrement=True),
    db.Column(
        'post_id',
        db.Integer,
        db.ForeignKey('post.id', ondelete='cascade')),
    db.Column(
        'category_id',
        db.Integer,
        db.ForeignKey('category.id', ondelete='cascade'))
)

post_comments = db.Table(
    'post_comments',
    db.Column(
        'id',
        db.Integer,
        primary_key=True,
        autoincrement=True),
    db.Column(
        'post_id',
        db.Integer,
        db.ForeignKey('post.id', ondelete='cascade')),
    db.Column(
        'comment_id',
        db.Integer,
        db.ForeignKey('comment.id', ondelete='cascade'))
)

page_posts = db.Table(
    'page_posts',
    db.Column(
        'id',
        db.Integer,
        primary_key=True,
        autoincrement=True),
    db.Column(
        'page_id',
        db.Integer,
        db.ForeignKey('page.id', ondelete='cascade')),
    db.Column(
        'post_id',
        db.Integer,
        db.ForeignKey('post.id', ondelete='cascade'))
)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(
        'id',
        db.Integer,
        primary_key=True,
        autoincrement=True, index=True)
    username = db.Column(
        'username',
        db.String(255),
        unique=True,
        nullable=False,
        index=True)
    password = db.Column('password', db.String(255), nullable=False)
    email = db.Column('email', db.String(50), nullable=False)
    registered_on = db.Column('registered_on', db.DateTime)
    admin = db.Column('admin', db.Integer, default=0)
    name = db.Column('name', db.String(255))
    image = db.Column('image', db.String(255))
    facebook = db.Column('facebook', db.String(255))
    twitter = db.Column('twitter', db.String(255))
    google = db.Column('google', db.String(255))

    #roles = relationship(
    #    'Role',
    #    secondary=user_roles,
    #    backref=backref('user', lazy='dynamic'),
    #)

    #posts = relationship(
    #    'Post',
    #    secondary=user_posts,
    #    backref=backref('user', lazy='dynamic')
    #)

    #comments = relationship(
    #    'Comment',
    #    secondary=user_comments,
    #    backref=backref('user', lazy='dynamic')
    #)

    #preferences = relationship(
    #    'Preference',
    #    secondary=user_preferences,
    #    backref=backref('user', lazy='dynamic')
    #)

    def __init__(self, username, password, email):
        self.username = username
        self.password = self.set_password(password)
        self.email = email
        self.registered_on = datetime.utcnow()
        self.is_admin = 0

    @classmethod
    def get(kls, username):
        """Returns User object by email.

        :param email: User's email address.
        :type email: str
        :returns: User() object of the corresponding
        :user if found, otherwise None.
        :rtype: instance or None
        """
        return kls.query.filter(kls.username == username.lower()).first()

    def delete_by_email(kls, email):
        """Delete artifacts of a user account then the user account itself.

        :param email: User's email address.
        :type email: str
        """
        user = kls.query.filter(kls.email == email.lower()).first()
        if user:
            kls.query.filter(kls.email == email.lower()).first()

    @classmethod
    def validate(kls, username, password):
        """Validates user without returning a User() object.

        :param email: User's email address.
        :type email: str
        :param password: User's password.
        :type password: str
        :returns: True if email/password combo is valid, False if not.
        :rtype: bool
        """
        user = kls.get(username)
        if user is None:
            return False
        else:
            return user.check_password(str(password))

    def set_password(self, password):
        """Sets an encrypted password.

        :param password: User's password.
        :type password: str
        :returns: Password hash.
        :rtype: str
        """
        return passlib.hash.sha512_crypt.encrypt(password)

    def check_password(self, password):
        """Checks password against stored password for the User() instance.

        :param password: User's password.
        :type password: str
        :returns: True if supplied password matches instance
        :password, False if not.
        :rtype: bool
        """
        return passlib.hash.sha512_crypt.verify(password, self.password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def is_admin(self):
        if self.admin == 1:
            return True
        else:
            return False

    def __repr__(self):
        return "<User email={0}>".format(self.email)


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(
        'id',
        db.Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    author = db.Column('author', db.String(255))
    title = db.Column('title', db.String(255), index=True)
    subheading = db.Column('subheading', db.String(255))
    slug = db.Column('slug', db.String(255))
    content = db.Column('content', db.Text)
    image = db.Column('image', db.Text)
    status = db.Column('status', db.Integer, default=1)
    date = db.Column(
        'date',
        db.DateTime,
        default=datetime.utcnow(),
        index=True)
    modified = db.Column(
        'modified',
        db.DateTime,
        default=datetime.utcnow(),
        index=True)
    tags = db.Column('tags', db.Text)

    #comments = relationship(
    #    'Comment',
    #    secondary=post_comments,
    #    backref=backref('post', lazy='dynamic')
    #)

    #categories = relationship(
    #    'Category',
    #    secondary=post_categories,
    #    backref=backref('post', lazy='dynamic')
    #)

    def __init__(self, author, title, slug, content, subheading, image, tags):
        self.author = author
        self.title = title
        self.subheading = subheading
        self.slug = slug
        self.content = content
        self.image = image
        self.date = datetime.utcnow()
        self.modified = datetime.utcnow()
        self.tags = tags

    def __repr__(self):
        return "<Post {0}>".format(self.title)

    @classmethod
    def get(kls, id):
        """Returns Post() object by ID.

        :param id: Post ID.
        :type id: str or int
        :returns: Page() object of the corresponding
        :ID if found, otherwise None.
        :rtype: instance or None
        """
        return kls.query.filter(kls.id == id.lower()).first()


class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(
        'id',
        db.Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    name = db.Column('name', db.String(255))
    post_id = db.Column(
        'post_id',
        db.Integer,
        db.ForeignKey('post.id'), index=True)

    def __init__(self, name, post_id):
        self.name = name
        self.post_id = post_id

    def __repr__(self):
        return "<Category name={0}>".format(self.name)


class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(
        'id',
        db.Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    author = db.Column('author', db.String(255))
    title = db.Column('title', db.String(255), index=True)
    content = db.Column('content', db.Text)
    status = db.Column('status', db.Integer, default=1)
    date = db.Column(
        'date',
        db.DateTime,
        default=datetime.utcnow(),
        index=True)
    modified = db.Column(
        'modified',
        db.DateTime,
        default=datetime.utcnow(),
        index=True)
    post_id = db.Column(
        'post_id',
        db.Integer,
        db.ForeignKey('post.id'), nullable=True, index=True)
    page_id = db.Column(
        'page_id',
        db.Integer,
        db.ForeignKey('page.id'), nullable=True, index=True)

    def __init__(self, author, title, content, post_id):
        self.author = author
        self.title = title
        self.content = content
        self.date = datetime.utcnow()
        self.modified = datetime.utcnow()
        self.post_id = post_id

    def __repr__(self):
        return "<Comment post_id={0}, author={1}, title={2}>".format(
            self.post_id, self.author, self.title)

    @classmethod
    def get(kls, id):
        """Returns Comment() object by id.

        :param id: Comment ID.
        :type id: str or int
        :returns: Comment() object of the corresponding
        :ID if found, otherwise None.
        :rtype: instance or None
        """
        return kls.query.filter(kls.id == id.lower()).first()


class Page(db.Model):
    __tablename__ = 'page'

    id = db.Column(
        'id',
        db.Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    title = db.Column('title', db.String(255), index=True)
    subheading = db.Column('subheading', db.String(255))
    slug = db.Column('slug', db.String(255))
    content = db.Column('content', db.Text)
    image = db.Column('image', db.Text)
    status = db.Column('status', db.Integer, default=1)
    modified = db.Column(
        'modified',
        db.DateTime,
        default=datetime.utcnow(),
        index=True)
    parent = db.Column('parent', db.Integer, default=0, index=True)

    #posts = relationship(
    #    'Post',
    #    secondary=page_posts,
    #    backref=backref('page', lazy='dynamic')
    #)

    def __init__(self, title, slug, content, subheading, image):
        self.title = title
        self.subheading = subheading
        self.slug = slug
        self.content = content
        self.image = image

    def __repr__(self):
        return "<Page title={0}>".format(self.title)

    @classmethod
    def get(kls, id):
        """Returns Page() object by id.

        :param id: Page ID.
        :type id: str or int
        :returns: Page() object of the corresponding
        :ID if found, otherwise None.
        :rtype: instance or None
        """
        return kls.query.filter(kls.id == id.lower()).first()


class Logs(db.Model):
    __tablename__ = 'site_logs'

    id = db.Column('id', db.Integer, primary_key=True)
    log_message = db.Column('log_message', db.Text)
    log_date = db.Column('log_date', db.DateTime)

    def __init__(self, content):
        self.log_message = content
        self.log_date = datetime.utcnow()


class Setting(db.Model):
    __tablename__ = 'setting'

    id = db.Column(
        'id',
        db.Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    name = db.Column('name', db.String(255))
    value = db.Column('value', db.Text)

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return "<Setting name={0}, value={1}>".format(self.name, self.value)


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(
        'id',
        db.Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    name = db.Column('rolename', db.String(255), index=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Role {0}>".format(self.name)


class Preference(db.Model):
    __tablename__ = 'preference'

    id = db.Column(
        'id',
        db.Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    option = db.Column('option', db.String(256))
    value = db.Column('value', db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, user_id, option, value):
        self.user_id = user_id
        self.option = option
        self.value = value

    def __repr__(self):
        return "<Preference user_id={0}, option={1}, value={2}>".format(
            self.user_id, self.option, self.value)

