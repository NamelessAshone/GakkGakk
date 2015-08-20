# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
import functools
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import flash, redirect

from flask.ext.login import current_user


def flash_errors(form, category="warning"):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash("{0} - {1}"
                  .format(getattr(form, field).label.text, error), category)


def admin_required(view):
    @functools.wraps(view)
    def inner(*args, **kwargs):
        if current_user.is_admin:
            return view(*args, **kwargs)
        else:
            return redirect("/")
    return inner


def get_user_id():
    try:
        return current_user.id
    except:
        return 0


def send_mail(receiver, subject, body):
    smtp_usr = 'ikke-svar@quak.no'
    smtp_pwd = 'ikkesvarmeg'
    sender = 'ikke-svar@quak.no'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject.encode('UTF-8')
    msg['From'] = sender
    msg['To'] = receiver.decode('UTF-8')
    msg.attach(MIMEText(body.encode('UTF-8'), 'plain'))

    s = smtplib.SMTP('balthazar.tihlde.org', 587)
    try:
        s.ehlo()
        s.starttls()
        s.login(smtp_usr, smtp_pwd)
        s.sendmail(sender, receiver, msg.as_string())
        s.quit()
    except:
        pass
