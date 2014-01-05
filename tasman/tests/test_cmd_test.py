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


class TestCmdTestCase(unittest.TestCase):

    def test_passed(self):
        environ = {'MESSAGE': 'test', 'XMPP_JID': 'k.bx@ya.ru'}

        rv = app(environ)
        self.assertEquals(list(rv), ['passed'])

    def test_passed_ru(self):
        environ = {'MESSAGE': u'тест', 'XMPP_JID': 'k.bx@ya.ru'}

        rv = app(environ)
        self.assertEquals(list(rv), [u'пассед'])

    def test_strict(self):
        environ = {'MESSAGE': 'test test test', 'XMPP_JID': 'k.bx@ya.ru'}

        rv = app(environ)
        self.assertEquals(list(rv), [])
