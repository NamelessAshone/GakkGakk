# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

from datetime import datetime
from time import strftime
from sqlalchemy.sql.expression import or_

from flask import Blueprint, render_template, redirect, request, url_for, flash, abort
from flask.ext.login import login_required, current_user
from flask.ext.paginate import Pagination

from gakkgakk.models import User, Team_Member, Team
from gakkgakk.models import Activity, Attending
from gakkgakk.utils import admin_required
from gakkgakk.database import db
from gakkgakk.utils import flash_errors, send_mail
from gakkgakk.msgs import ACT_REMOVED_TITLE, ACT_REMOVED_BODY
from .forms import SubmitActivity, EditActivity, SearchMember

blueprint = Blueprint('admin', __name__, url_prefix='/admin', static_folder="../static")


@blueprint.route('/home/')
@login_required
def home():
    return render_template("admin/home.html")


@blueprint.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def members():
    form = SearchMember(request.form, csrf_enabled=False)
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    search = False
    per_page = 25
    offset = (page - 1) * per_page

    if form.validate_on_submit():
        search = True
        q = form.search.data
        users = User.query.filter(or_(User.first_name.like(q),
                                      User.last_name.like(q),
                                      User.phone.like(q)))\
            .offset(offset)\
            .limit(per_page)

        count = users.count()
    else:
        count = len(User.query.all())
        users = User.query.limit(per_page).offset(offset)
    ##
    pagination = Pagination(page=page,
                            total=count,
                            per_page=per_page,
                            search=search,
                            record_name='users',
                            css_framework='bootstrap3')

    return render_template("admin/members.html",
                           users=users,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           form=form)


@blueprint.route('/user/<type>/<int:uid>')
@login_required
@admin_required
def user(type, uid):
    user = User.query.filter_by(id=uid).first_or_404()

    if user:
        if type == 'state':
            if user.active:
                user.active = False
            else:
                user.active = True
        elif type == 'admin':
            if user.is_admin:
                user.is_admin = False
            else:
                user.is_admin = True

        user.study = 'QUAK!2015'
        db.session.commit()

    msg = "Bruker %s (ID: %s) er oppdatert." % (user.full_name, user.id)
    flash(msg, 'success')
    return redirect(request.args.get("next") or url_for('admin.members'))


@login_required
@admin_required
@blueprint.route('/activity/add/', methods=['GET', 'POST'])
def add_activity():
    form = SubmitActivity(request.form, csrf_enabled=False)
    print datetime.now()
    if form.validate_on_submit():
        print datetime.now()
        new_activity = Activity.create(name=form.name.data,
                                       desc=form.description.data,
                                       contact=current_user.id,
                                       loc=form.location.data,
                                       slots=form.slots.data,
                                       time=form.time.data,
                                       day=form.day.data,
                                       reg_start=form.reg_start.data,
                                       reg_stop=form.reg_stop.data)

        msg = "%s er lagt til." % new_activity.name
        flash(msg, 'success')
        return redirect(url_for('public.day', day_id=form.day.data))
    else:
        flash_errors(form)
    return render_template('admin/add_activity.html', form=form)


@login_required
@admin_required
@blueprint.route('/activity/edit/<int:activity_id>', methods=['GET', 'POST'])
def edit_activity(activity_id):
    form = EditActivity(request.form, csrf_enabled=False)
    activity = Activity.query.filter(Activity.id == activity_id).first_or_404()

    print form.location.data
    if form.validate_on_submit():
        edit_activity = Activity.update(activity,
                                        name=form.name.data,
                                        description=form.description.data,
                                        contact=current_user.id,
                                        loc=form.location.data,
                                        slots=form.slots.data,
                                        time=form.time.data,
                                        day=form.day.data,
                                        reg_start=form.reg_start.data,
                                        reg_stop=form.reg_stop.data)

        msg = "%s er endret." % activity.name
        flash(msg, 'info')
        return redirect(url_for('public.day', day_id=form.day.data))
    else:
        if form.errors:
            flash_errors(form)

        form.name.data = activity.name
        form.description.data = activity.description
        form.location.data = activity.location
        form.slots.data = activity.slots
        form.time.data = activity.time
        form.day.data = activity.day_id
        form.reg_start.data = activity.reg_start
        form.reg_stop.data = activity.reg_stop

    return render_template('admin/edit_activity.html', form=form)


@blueprint.route('/activity/delete/<int:id>/<int:backid>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_activity(id, backid):
    activity = Activity.query.filter(Activity.id == id).first_or_404()
    try:
        Attending.query.filter(Attending.activity_id == id).delete()
        Activity.query.filter(Activity.id == id).delete()
        db.session.commit()

        subject = ACT_REMOVED_TITLE % activity.name
        body = ACT_REMOVED_BODY % activity.name

        for p in activity.participants:
            send_mail(p.email, subject, body)
    except:
        pass

    msg = "Aktiviteten %s er fjernet." % activity.name
    flash(msg, 'info')
    return redirect(url_for('public.day', day_id=backid))



@blueprint.route('/activity/show/<int:day_id>')
@login_required
@admin_required
def show_activity(day_id):
    activities = Activity.query.filter(Activity.day_id == day_id).all()
    return render_template('admin/all_activities.html', activities=activities, day_id=day_id)

