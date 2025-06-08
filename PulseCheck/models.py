from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import uuid
from datetime import datetime
from utils import generate_invite

db = SQLAlchemy()


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    invite_code = db.Column(db.String(10), unique=True, default=generate_invite)
    creator_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', use_alter=True, name='fk_creator_id'),
        nullable=False
    )

    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_teams')
    members = db.relationship('User', backref='team', lazy=True, foreign_keys='User.team_id')




class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50))  # e.g., 'Commit', 'Message', 'Blocker'
    description = db.Column(db.Text)

    user = db.relationship('User', backref='activities')
    team = db.relationship('Team', backref='activities')


class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    mood_value = db.Column(db.Integer, nullable=False)  # Expect value between 1 and 5
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='mood_entries')
    team = db.relationship('Team', backref='mood_entries')
