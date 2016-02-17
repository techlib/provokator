#!/usr/bin/python3 -tt
# -*- coding: utf-8 -*-

from fnmatch import fnmatch

import re

__all__ = ['AccessModel', 'AccessModelError']


class AccessModel(object):
    def __init__(self, items):
        """Initialize the access model with `(privilege, pattern)` pairs."""

        self.patterns = []

        for priv, pats in items:
            for pat in re.split(r'[ \t,]+', pats):
                if not fnmatch(pat, '[+-]*'):
                    raise AccessModelError('invalid pattern: %r' % (pat,))

                self.patterns.append((pat, priv))


    def privileges(self, role):
        """Resolve a role to a set of application specific privileges."""

        privs = set()

        for pat, priv in self.patterns:
            if fnmatch(pat, '+*') and fnmatch(role, pat[1:]):
                privs.add(priv)
            elif fnmatch(pat, '-*') and fnmatch(role, pat[1:]):
                privs.discard(priv)

        return privs

    def have_privilege(self, priv, roles):
        """Determine whether specified roles have given privilege."""

        for role in roles or ['impotent']:
            if priv in self.privileges(role):
                return True

        return False


class AccessModelError(Exception):
    """An error in the access model."""


# vim:set sw=4 ts=4 et:
