from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Arbeit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String)
    von = db.Column(db.String)
    bis = db.Column(db.String)
    length = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    break_user = db.Column(db.Integer)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    second_name = db.Column(db.String(150))
    user_stat = db.Column(db.String(5))
    user_dep = db.Column(db.String(20))
    work = db.relationship('Arbeit')
    note = db.relationship("Note")

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Vacation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String)
    type = db.Column(db.String)
    status = db.Column(db.Integer)
    authorized_by = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
