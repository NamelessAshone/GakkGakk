# -*- coding: utf-8 -*-
import datetime as dt

from sqlalchemy.orm import relationship
from flask_login import UserMixin, AnonymousUserMixin

from gakkgakk.extensions import bcrypt
from gakkgakk.database import (
    Column,
    db,
    Model,
    SurrogatePK,
    CRUDMixin,
    ForeignKey
)


class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.id = 0


class User(UserMixin, SurrogatePK, Model):
    __tablename__ = 'users'
    email = Column(db.String(80), unique=True, nullable=False)
    #: The hashed password
    password = Column(db.String(128), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    first_name = Column(db.String(30), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    study = Column(db.Text, nullable=True) #studieretning
    phone = Column(db.String(30), nullable=True)
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)

    activities = relationship('Activity', secondary='attending')
    teams = relationship('Team', secondary='team_member')

    def __init__(self, email, password=None, **kwargs):
        db.Model.__init__(self, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def __repr__(self):
        return '<User({email!r})>'.format(email=self.email)


class Activity(Model, SurrogatePK, CRUDMixin):
    # activities
    __tablename__ = 'activity'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(5000))
    contact_id = db.Column(db.Integer)  # the one who hosts the event
    location = db.Column(db.String(100))
    slots = db.Column(db.Integer)
    time = db.Column(db.Time)
    day_id = Column(db.Integer)
    reg_start = Column(db.DateTime)
    reg_stop = Column(db.DateTime)

    participants = relationship(User,
                                cascade='all,delete',
                                secondary='attending',)
    teams = relationship('Team',
                         cascade='all,delete',
                         secondary='activity_team')

    def __init__(self, name, desc, contact, loc, slots, time, day, reg_start, reg_stop):
        self.name = name
        self.description = desc
        self.contact_id = contact
        self.location = loc
        self.slots = slots
        self.time = time
        self.day_id = day
        self.reg_start = reg_start
        self.reg_stop = reg_stop

    def __repr__(self):
        return '<Activity(%r)>' % self.id


class Team(Model, SurrogatePK, CRUDMixin):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer)
    name = db.Column(db.String(60))
    contact_id = db.Column(db.Integer)

    members = relationship(User,
                           cascade='all,delete',
                           secondary='team_member')
    activities = relationship(Activity,
                              cascade='all,delete',
                              secondary='activity_team')

    def __init__(self, activity_id, name, contact):
        self.activity_id = activity_id
        self.name = name
        self.contact_id = contact

    def __repr__(self):
        return '<Team(%r)>' % self.id


class Activity_Team(Model, CRUDMixin):
    __tablename__ = 'activity_team'
    activity_id = Column(db.Integer, ForeignKey('activity.id'), primary_key=True)
    team_id = Column(db.Integer, ForeignKey('team.id'), primary_key=True)


class Team_Member(Model, CRUDMixin):
    __tablename__ = 'team_member'
    user_id = Column(db.Integer, ForeignKey('users.id'), primary_key=True)
    team_id = Column(db.Integer, ForeignKey('team.id'), primary_key=True)


class Attending(Model, CRUDMixin):
    __tablename__ = 'attending'
    activity_id = Column(db.Integer, ForeignKey('activity.id'), primary_key=True)
    user_id = Column(db.Integer, ForeignKey('users.id'), primary_key=True)

