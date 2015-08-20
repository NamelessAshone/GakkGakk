# -*- coding: utf-8 -*-

from datetime import datetime

from flask_wtf import Form
from wtforms import StringField, SelectField, IntegerField, TextAreaField, ValidationError
from wtforms.fields.html5 import DateTimeLocalField
from wtforms_components import TimeField
from wtforms.validators import DataRequired, Length

days = [(1, "DMDRI"),
        (2, "Festningslekene")]


def validate_date_range(reg_start, reg_stop):
    if not reg_start or not reg_stop:
        raise ValidationError('Start dato eller start dato er ikke fyllt ut.')
    elif reg_stop > reg_start:
        raise ValidationError('Start dato kan ikke vare større enn stop dato')
    elif reg_start < reg_stop:
        raise ValidationError('Start dato kan ikke vare større enn stop dato')


class SubmitActivity(Form):
    name = StringField('Aktivitets navn', validators=[DataRequired(), Length(min=1, max=50)])
    description = TextAreaField('Beskrivelse', validators=[DataRequired(), Length(min=1, max=5000)])
    location = StringField('Lokasjon', validators=[DataRequired(), Length(min=1, max=100)])
    day = SelectField('Dag', choices=days, coerce=int, default=0)
    slots = IntegerField('Plasser', validators=[DataRequired()])
    time = TimeField('Tidspunkt', validators=[DataRequired()])
    reg_start = DateTimeLocalField('Påmld. åpner', default=datetime.now(), format="%Y-%m-%dT%H:%M")
    reg_stop = DateTimeLocalField('Påmld. stenger', default=datetime.now(), format="%Y-%m-%dT%H:%M")


class EditActivity(Form):
    name = StringField('Aktivitets navn', validators=[DataRequired(), Length(min=1, max=50)])
    description = TextAreaField('Beskrivelse', validators=[DataRequired(), Length(min=1, max=5000)])
    location = StringField('Lokasjon', validators=[DataRequired(), Length(min=1, max=100)])
    day = SelectField('Dag', choices=days, coerce=int, default=0)
    slots = IntegerField('Plasser', validators=[DataRequired()])
    time = TimeField('Tidspunkt', validators=[DataRequired()])
    reg_start = DateTimeLocalField('Påmld. åpner', format="%Y-%m-%dT%H:%M")
    reg_stop = DateTimeLocalField('Påmld. stenger', format="%Y-%m-%dT%H:%M")


class SearchMember(Form):
    search = StringField(description="Sok etter en bruker ved hjelp av før-/etternavn navn", validators=[DataRequired(), Length(min=1, max=50)])
