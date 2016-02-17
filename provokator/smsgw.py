#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, \
                       print_function, unicode_literals

from requests import Session
from collections import Mapping
from urlparse import urljoin

KINDS = ['incoming', 'outgoing', 'checked', 'failed', 'sent']

class Gateway(Mapping):
    def __init__(self, baseurl, login, password):
        self.baseurl = baseurl
        self.login = login
        self.password = password
        self.session = Session()

    def __iter__(self):
        return iter(KINDS)

    def __getitem__(self, key):
        if not key in self:
            raise KeyError(key)

        return Spooler(key, self)

    def __contains__(self, key):
        return key in iter(self)

    def __len__(self):
        return len(iter(self))

    def request(self, method, url, **kw):
        url = urljoin(self.baseurl, url)
        r = self.session.request(method, url, auth=(self.login, self.password), **kw)
        return r.json()

    def to_dict(self):
        return {k: dict(v) for k, v in self.iteritems()}

    def send(self, number, text):
        return self.request('POST', 'outgoing', json={
            'text': text,
            'mobiles': [number],
        })


class Spooler(Mapping):
    def __init__(self, name, gateway):
        self.name = name
        self.gateway = gateway

    def __iter__(self):
        r = self.gateway.request('GET', self.name + '/')
        return iter(r['message_id'])

    def __getitem__(self, key):
        return self.gateway.request('GET', urljoin(self.name + '/', key))

    def __contains__(self, key):
        return key in iter(self)

    def __len__(self):
        return len(iter(self))


# vim:set sw=4 ts=4 et:
