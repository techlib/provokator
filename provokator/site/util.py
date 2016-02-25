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
        host = flask.request.headers.get('X-Forwarded-Host') or \
               flask.request.headers.get('Host', '')

        h = urlparse('http://' + host)

        origin = flask.request.headers.get('Origin') or \
                 flask.request.headers.get('Referer') or \
                 host
        o = urlparse(origin)

        if h.hostname != o.hostname:
            raise Forbidden('Cross-Site Request Forbidden')

        return fn(*args, **kwargs)
    return wrapper


# vim:set sw=4 ts=4 et:
