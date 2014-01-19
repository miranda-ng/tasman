# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
#

import unittest
from tasman.app import app
from xmppflask import JID


class TestCmdTestCase(unittest.TestCase):

    def test_passed(self):
        environ = {'xmpp.body': 'test', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}

        rv = app(environ)
        self.assertEquals(list(rv), ['passed'])

    def test_passed_ru(self):
        environ = {'xmpp.body': u'тест', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}

        rv = app(environ)
        self.assertEquals(list(rv), [u'пассед'])

    def test_strict(self):
        environ = {'xmpp.body': 'test test test',
                   'xmpp.jid': JID('tasman@xmpp.ru')}

        rv = app(environ)
        self.assertEquals(list(rv), [])

    def test_passed_groupchat(self):
        environ = {'xmpp.body': 'test', 'xmpp.jid': JID('chat@xmpp.ru/tasman'),
                   'xmpp.stanza_type': 'groupchat'}

        rv = app(environ)
        self.assertEquals(list(rv), ['tasman: passed'])

    def test_passed_groupchat_ru(self):
        environ = {'xmpp.body': u'тест', 'xmpp.jid': JID('chat@xmpp.ru/tasman'),
                   'xmpp.stanza_type': 'groupchat'}

        rv = app(environ)
        self.assertEquals(list(rv), [u'tasman: пассед'])
