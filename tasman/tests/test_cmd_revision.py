# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
#

import unittest
from xmppflask import JID
from tasman.app import app


class RevisionCmdTestCase(unittest.TestCase):

    def test_not_found(self):
        environ = {'xmpp.body': 'rev 000', 'xmpp.jid': JID('tasman@xmpp.ru')}

        rv = app(environ)
        self.assertEquals(list(rv), ['No such revision 0'])

    def test_invalid_id(self):
        environ = {'xmpp.body': 'rev XYZ', 'xmpp.jid': JID('tasman@xmpp.ru')}

        rv = app(environ)
        self.assertEquals(list(rv), [])

    def check_resp(self, resp):
        expected = u'tasman: [2012-02-11 18:58:26Z] http://trac.miranda-ng.org/changeset/1 - Create defaults dir'
        self.assertEqual(resp, expected)

    def test_shortcut(self):
        environ = {'xmpp.body': 'r1', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}

        rv = app(environ)
        self.check_resp(rv.next())

    def test_revision_en(self):
        environ = {'xmpp.body': 'rev 1', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}
        rv = app(environ)
        self.check_resp(rv.next())

        environ = {'xmpp.body': 'revision 1', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}
        rv = app(environ)
        self.check_resp(rv.next())

        environ = {'xmpp.body': 'commit 1', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}
        rv = app(environ)
        self.check_resp(rv.next())

    def test_ticket_ru(self):
        environ = {'xmpp.body': u'рев 1', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}
        rv = app(environ)
        self.check_resp(rv.next())

        environ = {'xmpp.body': u'ревизия 1',
                   'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}
        rv = app(environ)
        self.check_resp(rv.next())

        environ = {'xmpp.body': u'коммит 1', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}
        rv = app(environ)
        self.check_resp(rv.next())
