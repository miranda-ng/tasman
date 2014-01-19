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


class PingCmdTestCase(unittest.TestCase):

    def test_ping(self):
        environ = {'xmpp.body': 'ping', 'xmpp.jid': 'tasman@xmpp.ru'}

        rv = app(environ)
        self.assertEquals(list(rv), ['pong'])

    def test_ping_ru(self):
        environ = {'xmpp.body': u'пинг', 'xmpp.jid': 'tasman@xmpp.ru'}

        rv = app(environ)
        self.assertEquals(list(rv), [u'понг'])
