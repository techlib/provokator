#!/usr/bin/python3 -tt
# -*- coding: utf-8 -*-

__all__ = ['internal_origin_only']

from urllib.parse import urlparse
from functools import wraps
from werkzeug.exceptions import Forbidden

import flask
import re


def internal_origin_only(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        h = urlparse('http://' + flask.request.headers.get('Host', ''))
        host = '%s:%i' % (h.hostname, h.port or 80)

        if 'Origin' in flask.request.headers:
            o = urlparse(flask.request.headers.get('Origin'))
            origin = '%s:%i' % (o.hostname, o.port or 80)
        elif 'Referer' in flask.request.headers:
            r = urlparse(flask.request.headers.get('Referer'))
            origin = '%s:%i' % (r.hostname, r.port or 80)
        else:
            origin = host

        if host != origin:
            raise Forbidden('Cross-Site Request Forbidden')

        return fn(*args, **kwargs)
    return wrapper


# vim:set sw=4 ts=4 et:
