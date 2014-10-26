from datetime import datetime
from app import db

class Sample(db.Model):
    __tablename__ = 'sample'
    id = db.Column(db.Integer, primary_key=True)
    tagtext = db.Column(db.String(255))
    tagbody = db.Column(db.Text)

