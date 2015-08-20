# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import PasswordField, StringField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from gakkgakk.models import User


class RegisterForm(Form):
    study_choices = [("Fakultet for Teknologi (FT)", "Fakultet for Teknologi (FT)"),
                     ("Fakultet for Lærer- og Tolkeutdanning (FLT)", "Fakultet for Lærer- og Tolkeutdanning (FLT)"),
                     ("Institutt for Informatikk og e-læring (IIE)", "Institutt for Informatikk og e-læring (IIE)"),
                     ("Fakultet for Helse- og Sosialvitenskap (FHS)", "Fakultet for Helse- og Sosialvitenskap (FHS)"),
                     ("Institutt for Sykepleievitenskap (ISV)", "Institutt for Sykepleievitenskap (ISV)"),
                     ("Helsevitenskap og Anvendt Sosialvitenskap (IHV+IAS)", "Helsevitenskap og Anvendt Sosialvitenskap (IHV+IAS)"),
                     ("Handelshøyskolen (HHiT)", "Handelshøyskolen (HHiT)"),
                     ("Dronning Mauds Minne Høgskole (DMMH)", "Dronning Mauds Minne Høgskole (DMMH)"),
                     ("Norges Kreative Høyskole (NKH)", "Norges Kreative Høyskole (NKH)")]

    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(min=6, max=40)])
    first_name = StringField('Fornavn', validators=[DataRequired(), Length(min=1, max=50)])
    last_name = StringField('Etternavn', validators=[DataRequired(), Length(min=1, max=50)])
    study = SelectField("Studieretning ", choices=study_choices, default=0)
    phone = StringField('Mobil telefon', validators=[DataRequired(), Length(min=8, max=8)])
    password = PasswordField('Passord', validators=[DataRequired(), Length(min=6, max=40)])
    confirm = PasswordField('Verifisere passord', [DataRequired(), EqualTo('password',
                                                                           message='Passorden må være like.')])

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email adressen er allerede registrert.")
            return False
        return True
