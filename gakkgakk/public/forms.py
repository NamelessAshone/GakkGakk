# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length

from gakkgakk.models import User


class SubmitTeam(Form):
    name = StringField('Lag navn', validators=[DataRequired(), Length(min=1, max=50)])


class LoginForm(Form):
    email = StringField('E-mail', validators=[DataRequired()])
    password = PasswordField('Passord', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(email=self.email.data).first()
        if not self.user:
            self.email.errors.append('Feil e-mail eller passord.')
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append('Feil e-mail ellr passord.')
            return False

        if not self.user.active:
            self.email.errors.append('Brukern er deaktivert.')
            return False
        return True
