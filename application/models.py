from .database import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    username=db.Column(db.String, nullable=False, unique=True)
    password=db.Column(db.String, nullable=False)
    trackers=db.relationship("Tracker", cascade='all', backref="parent")

class Tracker(db.Model):
    __tablename__ = 'tracker'
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tracker_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    name=db.Column(db.String(30), nullable=False)
    desc=db.Column(db.String)
    type=db.Column(db.String, nullable=False)
    settings=db.Column(db.String)
    lastupdate=db.Column(db.DateTime)
    logs=db.relationship("TrackerLogs", cascade='all', backref="parent")

class TrackerLogs(db.Model):
    __tablename__ = 'trackerlogs'
    tracker_id=db.Column(db.Integer, db.ForeignKey("tracker.tracker_id"), nullable=False)
    log_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    log_datetime=db.Column(db.DateTime,nullable=False)
    note=db.Column(db.String)
    log_value=db.Column(db.String, nullable=False)
    



