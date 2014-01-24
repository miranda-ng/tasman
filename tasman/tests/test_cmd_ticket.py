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


class TicketCmdTestCase(unittest.TestCase):

    def test_not_found(self):
        environ = {'xmpp.body': 'bug 000', 'xmpp.jid': JID('tasman@xmpp.ru')}

        rv = app(environ)
        self.assertEquals(list(rv), ['Ticket 0 does not exist.'])

    def test_invalid_id(self):
        environ = {'xmpp.body': 'bug XYZ', 'xmpp.jid': JID('tasman@xmpp.ru')}

        rv = app(environ)
        self.assertEquals(list(rv), [])

    def check_resp(self, resp):
        expected = u'tasman: [new] http://trac.miranda-ng.org/ticket/155 - Indication of new messages in MUC'
        self.assertEqual(resp, expected)

    def test_hash(self):
        environ = {'xmpp.body': '#155', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}

        rv = app(environ)
        self.check_resp(rv.next())

    def test_ticket_en(self):
        environ = {'xmpp.body': 'bug 155', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}
        rv = app(environ)
        self.check_resp(rv.next())

        environ = {'xmpp.body': 'issue 155', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}
        rv = app(environ)
        self.check_resp(rv.next())

        environ = {'xmpp.body': 'ticket 155', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}
        rv = app(environ)
        self.check_resp(rv.next())

    def test_ticket_ru(self):
        environ = {'xmpp.body': u'баг 155', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}
        rv = app(environ)
        self.check_resp(rv.next())

        environ = {'xmpp.body': u'проблема 155',
                   'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}
        rv = app(environ)
        self.check_resp(rv.next())

        environ = {'xmpp.body': u'тикет 155', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}
        rv = app(environ)
        self.check_resp(rv.next())

