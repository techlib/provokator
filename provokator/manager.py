#!/usr/bin/python3 -tt
# -*- coding: utf-8 -*-

__all__ = ['Manager']

from twisted.internet import task, reactor
from twisted.python import log
from urllib.parse import urljoin

import requests

class Manager(object):
    KINDS = ['incoming', 'outgoing', 'checked', 'failed', 'sent']

    def __init__(self, db, peer_url):
        self.db = db
        self.peer_url = peer_url

    def fetch_messages(self):
        log.msg('Starting message download...')

        for kind in self.KINDS:
            r = requests.get(urljoin(self.peer_url, '%s/' % kind)).json()

            for mid in r['message_id']:
                m = self.db.message.filter_by(id=mid).first()

                if m is not None and m.state == kind:
                    # Message is up-to-date in the database.
                    continue

                info = requests.get(urljoin(self.peer_url, '%s/%s' % (kind, mid))).json()

                if info.get('From') is None and info.get('To') is None:
                    # Discard when neither sender nor recipient is present.
                    continue

                if 'text' not in info:
                    # Info is broken; we are not allowed to see the message or
                    # something like that. Ignore.
                    continue

                if m is None:
                    # Message was never seen before.
                    m = self.db.message(id=mid, msg=info, state=kind)
                else:
                    # Message changed state.
                    m.state = kind

                log.msg('Message %r %s' % (mid, kind))
                self.db.flush()

        self.db.commit()
        log.msg('Message download complete.')


    def send_message(self, phone, text):
        log.msg('Sending %r to %r' % (text, phone))

        r = requests.post(urljoin(self.peer_url, 'outgoing'), json={
            'mobiles': [phone],
            'text': text,
        }).json()

        reactor.callLater(0, self.fetch_messages)

        return 'Ok' == r['mobiles'][phone]['response']


    def start(self):
        task.LoopingCall(self.fetch_messages).start(60)


# vim:set sw=4 ts=4 et:
