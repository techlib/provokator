#!/usr/bin/python3 -tt
# -*- coding: utf-8 -*-

__all__ = ['Manager']

from twisted.internet import task, reactor
from twisted.python import log
from urllib.parse import urljoin
from datetime import datetime

import requests

class Manager(object):
    KINDS = ['incoming', 'outgoing', 'checked', 'failed', 'sent']

    def __init__(self, db, peer_url):
        self.db = db
        self.peer_url = peer_url

    def fetch_messages(self):
        log.msg('Starting message download...')

        for kind in self.KINDS:
            try:
                r = requests.get(urljoin(self.peer_url, '%s/' % kind)).json()
            except:
                log.msg('Failed to fetch %s messages', kind)
                log.err()
                continue

            for mid in r['message_id']:
                m = self.db.message.filter_by(id=mid).first()

                if m is not None and m.state == kind:
                    # Message is up-to-date in the database.
                    continue

                try:
                    info = requests.get(urljoin(self.peer_url, '%s/%s' % (kind, mid))).json()
                except:
                    log.msg('Failed to fetch %s/%s message', kind, mid)
                    log.err()
                    continue

                if info.get('From') is None and info.get('To') is None:
                    # Discard when neither sender nor recipient is present.
                    continue

                if 'text' not in info:
                    # Info is broken; we are not allowed to see the message or
                    # something like that. Ignore.
                    continue

                # Identify the time when the message was received/sent.
                # If the respective header is not present, use current time.
                try:
                    ts = datetime.now()

                    if info.get('Received') is not None:
                        ts = datetime.strptime(info['Received'], '%y-%m-%d %H:%M:%S')
                    elif info.get('Sent') is not None:
                        ts = datetime.strptime(info['Sent'], '%y-%m-%d %H:%M:%S')

                except ValueError:
                    pass

                if m is None:
                    # Message was never seen before.
                    m = self.db.message(id=mid, msg=info, state=kind, ts=ts)
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
