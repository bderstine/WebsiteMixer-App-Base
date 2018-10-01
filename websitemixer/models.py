# -*- coding: utf-8 -*-
from datetime import datetime
import hashlib
import passlib.hash

from sqlalchemy import Column, Integer, String, Table, ForeignKey, DateTime, Text
from websitemixer.database import Base

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column(
        'id',
        Integer,
        primary_key=True,
        autoincrement=True),
    Column(
        'user_id',
        Integer,
        ForeignKey('user.id', ondelete='cascade')),
    Column(
        'role_id',
        Integer,
        ForeignKey('role.id', ondelete='cascade'))
)

user_posts = Table(
    'user_posts',
    Base.metadata,
    Column(
        'id',
        Integer,
        primary_key=True,
        autoincrement=True),
    Column(
        'user_id',
        Integer,
        ForeignKey('user.id')),
    Column(
        'post_id',
        Integer,
        ForeignKey('post.id'))
)

user_comments = Table(
    'user_comments',
    Base.metadata,
    Column(
        'id',
        Integer,
        primary_key=True,
        autoincrement=True),
    Column(
        'user_id',
        Integer,
        ForeignKey('user.id')),
    Column(
        'comment_id',
        Integer,
        ForeignKey('comment.id'))
)

user_preferences = Table(
    'user_preferences',
    Base.metadata,
    Column(
        'id',
        Integer,
        primary_key=True,
        autoincrement=True),
    Column(
        'user_id',
        Integer,
        ForeignKey('user.id', ondelete='cascade')),
    Column(
        'preference_id',
        Integer,
        ForeignKey('preference.id', ondelete='cascade'))
)

post_categories = Table(
    'post_categories',
    Base.metadata,
    Column(
        'id',
        Integer,
        primary_key=True,
        autoincrement=True),
    Column(
        'post_id',
        Integer,
        ForeignKey('post.id', ondelete='cascade')),
    Column(
        'category_id',
        Integer,
        ForeignKey('category.id', ondelete='cascade'))
)

post_comments = Table(
    'post_comments',
    Base.metadata,
    Column(
        'id',
        Integer,
        primary_key=True,
        autoincrement=True),
    Column(
        'post_id',
        Integer,
        ForeignKey('post.id', ondelete='cascade')),
    Column(
        'comment_id',
        Integer,
        ForeignKey('comment.id', ondelete='cascade'))
)

page_posts = Table(
    'page_posts',
    Base.metadata,
    Column(
        'id',
        Integer,
        primary_key=True,
        autoincrement=True),
    Column(
        'page_id',
        Integer,
        ForeignKey('page.id', ondelete='cascade')),
    Column(
        'post_id',
        Integer,
        ForeignKey('post.id', ondelete='cascade'))
)


class User(Base):
    __tablename__ = 'user'
    id = Column(
        'id',
        Integer,
        primary_key=True,
        autoincrement=True, index=True)
    username = Column(
        'username',
        String(255),
        unique=True,
        nullable=False,
        index=True)
    password = Column('password', String(255), nullable=False)
    email = Column('email', String(50), nullable=False)
    registered_on = Column('registered_on', DateTime)
    admin = Column('admin', Integer, default=0)
    name = Column('name', String(255))
    image = Column('image', String(255))
    facebook = Column('facebook', String(255))
    twitter = Column('twitter', String(255))
    google = Column('google', String(255))

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


class Post(Base):
    __tablename__ = 'post'

    id = Column(
        'id',
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    author = Column('author', String(255))
    title = Column('title', String(255), index=True)
    subheading = Column('subheading', String(255))
    slug = Column('slug', String(255))
    content = Column('content', Text)
    image = Column('image', Text)
    status = Column('status', Integer, default=1)
    date = Column(
        'date',
        DateTime,
        default=datetime.utcnow(),
        index=True)
    modified = Column(
        'modified',
        DateTime,
        default=datetime.utcnow(),
        index=True)
    tags = Column('tags', Text)

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


class Category(Base):
    __tablename__ = 'category'

    id = Column(
        'id',
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    name = Column('name', String(255))
    post_id = Column(
        'post_id',
        Integer,
        ForeignKey('post.id'), index=True)

    def __init__(self, name, post_id):
        self.name = name
        self.post_id = post_id

    def __repr__(self):
        return "<Category name={0}>".format(self.name)


class Comment(Base):
    __tablename__ = 'comment'

    id = Column(
        'id',
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    author = Column('author', String(255))
    title = Column('title', String(255), index=True)
    content = Column('content', Text)
    status = Column('status', Integer, default=1)
    date = Column(
        'date',
        DateTime,
        default=datetime.utcnow(),
        index=True)
    modified = Column(
        'modified',
        DateTime,
        default=datetime.utcnow(),
        index=True)
    post_id = Column(
        'post_id',
        Integer,
        ForeignKey('post.id'), nullable=True, index=True)
    page_id = Column(
        'page_id',
        Integer,
        ForeignKey('page.id'), nullable=True, index=True)

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


class Page(Base):
    __tablename__ = 'page'

    id = Column(
        'id',
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    title = Column('title', String(255), index=True)
    subheading = Column('subheading', String(255))
    slug = Column('slug', String(255))
    content = Column('content', Text)
    image = Column('image', Text)
    status = Column('status', Integer, default=1)
    modified = Column(
        'modified',
        DateTime,
        default=datetime.utcnow(),
        index=True)
    parent = Column('parent', Integer, default=0, index=True)

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


class Logs(Base):
    __tablename__ = 'site_logs'

    id = Column('id', Integer, primary_key=True)
    log_message = Column('log_message', Text)
    log_date = Column('log_date', DateTime)

    def __init__(self, content):
        self.log_message = content
        self.log_date = datetime.utcnow()


class Setting(Base):
    __tablename__ = 'setting'

    id = Column(
        'id',
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    name = Column('name', String(255))
    value = Column('value', Text)

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return "<Setting name={0}, value={1}>".format(self.name, self.value)


class Role(Base):
    __tablename__ = 'role'

    id = Column(
        'id',
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    name = Column('rolename', String(255), index=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Role {0}>".format(self.name)


class Preference(Base):
    __tablename__ = 'preference'

    id = Column(
        'id',
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    option = Column('option', String(256))
    value = Column('value', String(256))
    user_id = Column(Integer, ForeignKey('user.id'))

    def __init__(self, user_id, option, value):
        self.user_id = user_id
        self.option = option
        self.value = value

    def __repr__(self):
        return "<Preference user_id={0}, option={1}, value={2}>".format(
            self.user_id, self.option, self.value)

