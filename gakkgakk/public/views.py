# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

from datetime import datetime
from sqlalchemy import func

from flask import Blueprint, request, render_template, flash, url_for, redirect, abort
from flask.ext.login import login_user, login_required, logout_user, current_user
from flask.ext.paginate import Pagination

from gakkgakk.extensions import login_manager, db
from gakkgakk.models import User, Activity, Attending, Team, Team_Member, Activity_Team
from gakkgakk.public.forms import LoginForm, SubmitTeam
from gakkgakk.user.forms import RegisterForm
from gakkgakk.utils import flash_errors, get_user_id, send_mail
from gakkgakk.msgs import (TEAM_JOINED_BODY,
                           TEAM_JOINED_TITLE,
                           TEAM_LEFT_BODY,
                           TEAM_LEFT_TITLE,
                           TEAM_REMOVED_BODY,
                           TEAM_REMOVED_TITLE,
                           ACT_JOINED_TITLE,
                           ACT_JOINED_BODY,
                           ACT_LEFT_TITLE,
                           ACT_LEFT_BODY,
                           ACT_REMOVED_TITLE,
                           ACT_REMOVED_BODY)

blueprint = Blueprint('public', __name__, static_folder="../static")


@login_manager.user_loader
def load_user(id):
    return User.get_by_id(int(id))


@blueprint.route("/", methods=["GET", "POST"])
def home():
    form = LoginForm(request.form, csrf_enabled=False)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash("Du er nå logget inn.", 'success')
            redirect_url = request.args.get("next") or url_for("public.home")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/home.html", form=form)


@blueprint.route('/user/logout/')
@login_required
def logout():
    logout_user()
    flash('Du er nå logget ut.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route("/user/register/", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        new_user = User.create(email=form.email.data,
                               first_name=form.first_name.data,
                               last_name=form.last_name.data,
                               study=form.study.data,
                               phone=form.phone.data,
                               password=form.password.data,
                               active=True)
        flash("Takk for at du registrerte deg, du kan nå logge inn.", 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)


@blueprint.route("/day/<int:day_id>")
def day(day_id):

    if day_id == 1:
        return redirect(url_for('public.dmdri'))
    elif day_id == 2:
        return redirect(url_for('public.aktivitetsdagen'))

    return abort(404)


@blueprint.route("/day/dmdri")
def dmdri():
    form = LoginForm(request.form, csrf_enabled=False)
    day_id = 1

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    per_page = 5
    offset = (page - 1) * per_page

    participating_count = db.session.query(Attending.activity_id, func.count(Attending.user_id).label('pcount'))\
        .group_by(Attending.activity_id)\
        .subquery('participating_count')

    attending_query = db.session.query(Attending.activity_id, func.IF(Attending.user_id == get_user_id(), True, False).label('is_attending'))\
        .group_by(Attending.activity_id)\
        .subquery('attending_check')

    activities = db.session.query(Activity, attending_query)\
        .select_from(Activity)\
        .outerjoin(attending_query, Activity.id == attending_query.c.activity_id)\
        .filter(Activity.day_id == day_id)\
        .limit(per_page)\
        .offset(offset)

        #.group_by(participating_count.desc())\
    all_activities = Activity.query.filter(Activity.day_id == day_id).all()

    attending = any(user.id == get_user_id() for activity in all_activities for user in activity.participants)

    pagination = Pagination(page=page,
                            total=len(all_activities),
                            per_page=per_page,
                            search=False,
                            css_framework='bootstrap3',
                            display_msg='viser aktivitet <b>{start}</b> til <b>{end}</b> av <b>{total}</b> aktiviteter')

    return render_template("public/dmdri.html",
                           activities=activities,
                           attending=attending,
                           per_page=per_page,
                           pagination=pagination,
                           day_id=day_id,
                           time_now=datetime.now(),
                           form=form)


@blueprint.route("/day/festningslekene")
def aktivitetsdagen():
    form = LoginForm(request.form, csrf_enabled=False)
    day_id = 2


    attending_query = db.session.query(Attending.activity_id, func.IF(Attending.user_id == get_user_id(), True, False).label('is_attending'))\
        .group_by(Attending.activity_id)\
        .subquery('attending_check')

    activities = db.session.query(Activity, attending_query)\
        .select_from(Activity)\
        .outerjoin(attending_query, Activity.id == attending_query.c.activity_id)\
        .filter(Activity.day_id == day_id)

    attending = any(user.id == get_user_id() for activity in activities for user in activity.Activity.participants)

    return render_template("public/festningslekene.html",
                           activities=activities,
                           attending=attending,
                           day_id=day_id,
                           time_now=datetime.now(),
                           form=form)


@blueprint.route("/activity/join/<int:activity_id>/<int:day_id>")
@login_required
def join_activity(activity_id, day_id):
    activity = Activity.query.filter(Activity.id == activity_id).first_or_404()
    activities = Activity.query.filter(Activity.day_id == day_id).all()
    attending = any(user.id == get_user_id() for activity in activities for user in activity.participants)

    if len(activity.participants) >= activity.slots:
        msg = "%s kan kun ha %s deltakere." % (activity.name, activity.slots)
        flash(msg, 'warning')
        return redirect(url_for('public.day', day_id=day_id))

    elif attending:
        flash("Du kan ikke meld deg på flere aktiviteter.", 'warning')
        return redirect(url_for('public.day', day_id=day_id))

    else:

        join_ac = Attending.create(activity_id=activity_id,
                                   user_id=current_user.id)
        join_ac.save()

        title = ACT_JOINED_TITLE % activity.name
        body = ACT_JOINED_BODY % activity.name

        send_mail(current_user.email, title, body)

        msg = "Du er nå med i aktiviteten %s." % activity.name
        flash(msg, 'info')

        return redirect(url_for('public.day', day_id=day_id))


@blueprint.route("/activity/leave/<int:activity_id>/<int:day_id>/")
@blueprint.route("/activity/leave/<int:activity_id>/<int:day_id>/<int:user_id>")
@login_required
def leave_activity(activity_id, day_id, user_id=None):
    if not user_id:
        user_id = current_user.id

    activity = Activity.query.filter(Activity.id == activity_id).first_or_404()

    leave_ac = Attending.query.filter(Attending.user_id == user_id)\
        .filter(Attending.activity_id == activity_id)\
        .first_or_404()
    leave_ac.delete()

    title = ACT_LEFT_TITLE % activity.name
    body = ACT_LEFT_BODY % activity.name

    send_mail(current_user.email, title, body)

    msg = "Du er ikke lenger med i aktiviteten %s." % activity.name
    flash(msg, 'info')

    return redirect(url_for('public.day', day_id=day_id))


@blueprint.route("/team/create/<int:activity_id>", methods=['GET', 'POST'])
@login_required
def team_create(activity_id):
    form = SubmitTeam(request.form, csrf_enabled=False)
    activity = Activity.query.filter(Activity.id == activity_id).first_or_404()

    if len(activity.teams) >= activity.slots:
        msg = "%s kan maksimalt ha %s lag." % (activity.name, activity.slots)
        flash(msg, 'warning')
        return redirect(url_for('public.aktivitetsdagen'))

    if form.validate_on_submit():
        new_team = Team.create(activity_id=activity_id,
                               name=form.name.data,
                               contact=current_user.id)

        add = Activity_Team.create(activity_id=activity_id, team_id=new_team.id)
        join = Team_Member.create(user_id=current_user.id, team_id=new_team.id)

        msg = "Laget %s er nå registrert." % new_team.name
        flash(msg, 'success')
        return redirect(url_for('public.aktivitetsdagen'))

    return render_template('public/create_team.html', form=form)


@blueprint.route("/team/show/<int:team_id>")
def team_show(team_id):
    form = LoginForm(request.form, csrf_enabled=False)

    team = Team.query.filter(Team.id == team_id).first_or_404()
    is_member = any(user.id == get_user_id() for user in team.members)

    return render_template('public/show_team.html', team=team, is_member=is_member, form=form)


@blueprint.route("/team/join/<int:team_id>")
@login_required
def team_join(team_id):
    team = Team.query.filter(Team.id == team_id).first()

    if len(team.members) >= 8:
        msg = "%s har %s av maksimalt 8 medlemmer." % (team.name, len(team.members))
        flash(msg, 'warning')
        return redirect(url_for('public.team_show', team_id=team_id))

    else:
        tm = Team_Member.create(user_id=get_user_id(), team_id=team_id)

        title = TEAM_JOINED_TITLE % team.name
        body = TEAM_JOINED_BODY % team.name

        send_mail(current_user.email, title, body)

        msg = "Du har blitt med laget %s." % team.name
        flash(msg, 'success')
        return redirect(url_for('public.team_show', team_id=team_id))


@blueprint.route("/team/leave/<int:team_id>/")
@blueprint.route("/team/leave/<int:team_id>/<int:user_id>")
@login_required
def team_leave(team_id, user_id=None):
    if not user_id:
        user_id = current_user.id

    team = Team.query.filter(Team.id == team_id).first()
    tm = Team_Member.query.filter(Team_Member.user_id == user_id)\
        .filter(Team_Member.team_id == team_id)\
        .first()
    tm.delete()

    db.session.commit()

    title = TEAM_LEFT_TITLE % team.name
    body = TEAM_LEFT_BODY % team.name

    send_mail(current_user.email, title, body)

    msg = "Du har nå forlatt laget %s." % team.name
    flash(msg, 'info')

    return redirect(url_for('public.team_show', team_id=team_id))


@blueprint.route("/team/delete/<int:team_id>")
@login_required
def team_delete(team_id):
    team = Team.query.filter(Team.id == team_id).first_or_404()
    if team.contact_id == get_user_id() or current_user.is_admin:
        msg = "Laget %s er nå fjernet." % team.name

        Team_Member.query.filter(Team_Member.team_id == team_id).delete()
        Activity_Team.query.filter(Activity_Team.team_id == team_id).delete()

        team.delete()

        db.session.commit()

        title = TEAM_REMOVED_TITLE % team.name
        body = TEAM_REMOVED_BODY % team.name
        for member in team.members:
            send_mail(member.email, title, body)

        flash(msg, 'info')

    return redirect(url_for('public.aktivitetsdagen'))
