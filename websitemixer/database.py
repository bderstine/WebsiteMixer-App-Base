from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from flask import current_app

#from flask import current_app
#print(current_app.config['SQLALCHEMY_DATABASE_URI'])

engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'], 
    convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
    autoflush=False,
    bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def create_tables():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import websitemixer.models
    Base.metadata.create_all(bind=engine)
