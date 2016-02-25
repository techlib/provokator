#!/usr/bin/python3 -tt
# -*- coding: utf-8 -*-

__all__ = ['make_site']

from sqlalchemy import *
from sqlalchemy.exc import *
from werkzeug.exceptions import *
from provokator.site.util import *
from functools import wraps
from datetime import datetime, timedelta

import flask
import os
import re


def make_site(db, manager, access_model, debug=False):
    app = flask.Flask('.'.join(__name__.split('.')[:-1]))
    app.secret_key = os.urandom(16)
    app.debug = debug


    @app.template_filter('format_ts')
    def format_ts(ts):
        return ts.strftime('%Y-%m-%d %H:%M:%S')

    @app.template_filter('format_phone')
    def format_phone(phone):
        phone = ''.join(re.findall('\d+', phone))
        groups = re.findall(r'.{1,3}', ''.join(reversed(phone)))
        return '+' + ''.join(reversed(' '.join(groups)))

    @app.template_filter('to_alert')
    def state_to_alert(st):
        return {
            'incoming': 'alert-warning',
            'outgoing': 'alert-info',
            'checked':  'alert-info',
            'sent':     'alert-success',
            'failed':   'alert-danger',
            'success':  'alert-success',
            'error':    'alert-danger',
        }[st]

    @app.template_filter('to_icon')
    def state_to_icon(st):
        return {
            'incoming': 'pficon-user',
            'outgoing': 'pficon-enterprise',
            'checked':  'pficon-enterprise',
            'sent':     'pficon-enterprise',
            'failed':   'pficon-enterprise',
            'error':    'pficon-error-circle-o',
            'success':  'pficon-ok',
        }[st]


    def has_privilege(privilege):
        roles = flask.request.headers.get('X-Roles', '')
        roles = re.findall(r'\w+', roles)
        return access_model.have_privilege(privilege, roles)

    def authorized_only(privilege='user'):
        def make_wrapper(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                if not has_privilege(privilege):
                    raise Forbidden('RBAC Forbidden')

                return fn(*args, **kwargs)

            return wrapper
        return make_wrapper


    @app.errorhandler(Forbidden.code)
    def unauthorized(e):
        return flask.render_template('forbidden.html', **locals())

    @app.errorhandler(BadRequest.code)
    def unauthorized(e):
        return flask.render_template('bad-request.html', **locals())


    def query_messages(state=None, year=None, month=None, day=None, days=None, limit=None):
        messages = db.dated_messages

        if year is not None:
            messages = messages.filter(db.dated_messages.c.year == year)

        if month is not None:
            messages = messages.filter(db.dated_messages.c.month == month)

        if day is not None:
            messages = messages.filter(db.dated_messages.c.day == day)

        if state is not None:
            messages = messages.filter(db.dated_messages.c.state == state)

        if days is not None:
            since = datetime.now() - timedelta(days=days)
            messages = messages.filter(db.dated_messages.c.ts >= since)

        if limit is not None:
            return messages.limit(limit).all()

        return messages.all()


    @app.route('/')
    @app.route('/<state>')
    @app.route('/monthly/<int:year>/<int:month>/')
    @app.route('/monthly/<int:year>/<int:month>/<state>')
    @authorized_only()
    def index(state=None, year=None, month=None):
        nonlocal has_privilege

        if year is None:
            days = db.daily_stats.limit(14).all()
        else:
            days = db.daily_stats \
                    .filter(db.daily_stats.c.year == year) \
                    .filter(db.daily_stats.c.month == month).all()

        total_incoming = sum(d.incoming for d in days)
        total_sent     = sum(d.sent for d in days)
        total_outgoing = sum(d.outgoing for d in days)
        total_checked  = sum(d.checked for d in days)
        total_failed   = sum(d.failed for d in days)

        if state is None and year is None:
            messages = query_messages(limit=10)
        elif year is None:
            messages = query_messages(state=state, limit=25)
        else:
            messages = query_messages(state=state, year=year, month=month)

        return flask.render_template('main.html', **locals())


    @app.route('/monthly/')
    @authorized_only()
    def monthly():
        nonlocal has_privilege
        months = db.monthly_counts.all()
        return flask.render_template('monthly.html', **locals())


    @app.route('/daily/')
    @authorized_only()
    def daily():
        nonlocal has_privilege
        return flask.render_template('daily.html', **locals())


    @app.route('/daily/view')
    @authorized_only()
    def daily_view():
        nonlocal has_privilege

        date = flask.request.args.get('day')

        try:
            year, month, day = map(int, date.split('-'))
        except:
            raise BadRequest('The date you have provided is not valid.')

        days = db.daily_stats \
                    .filter(db.daily_stats.c.year == year) \
                    .filter(db.daily_stats.c.month == month) \
                    .filter(db.daily_stats.c.day == day).all()

        total_incoming = sum(d.incoming for d in days)
        total_sent     = sum(d.sent for d in days)
        total_outgoing = sum(d.outgoing for d in days)
        total_checked  = sum(d.checked for d in days)
        total_failed   = sum(d.failed for d in days)

        messages = query_messages(year=year, month=month, day=day)

        return flask.render_template('daily-view.html', **locals())


    @app.route('/write/')
    @authorized_only('admin')
    def write():
        return flask.render_template('write.html', **locals())


    @app.route('/write/send', methods=['POST'])
    @authorized_only('admin')
    @internal_origin_only
    def write_send():
        phone = flask.request.form.get('phone', '')
        text = flask.request.form.get('text', '')

        phone = re.sub(r'\s+', '', phone)
        text = text.strip()

        if not re.match(r'^\+\d{6,15}$', phone):
            raise BadRequest('Invalid phone number!')

        if 0 == len(text):
            raise BadRequest('Cannot send a message with no text!')

        if len(text) > 400:
            raise BadRequest('Message text too long!')

        if manager.send_message(phone, text):
            flask.flash('Posted a message to %s' % phone, 'success')
        else:
            flask.flash('Failed to post a message to %s' % phone, 'error')

        return flask.redirect('/write/')


    @app.teardown_appcontext
    def shutdown_session(exception=None):
        manager.db.rollback()


    return app


# vim:set sw=4 ts=4 et:
# -*- coding: utf-8 -*-
