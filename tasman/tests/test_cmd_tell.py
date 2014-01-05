# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
#

import unittest
from tasman.app import app, MESSAGE_QUEUE


class TellCmdTestCase(unittest.TestCase):

    def tearDown(self):
        MESSAGE_QUEUE.clear()

    def test_tell(self):
        environ = {'MESSAGE': 'tell foo boo!',
                   'XMPP_JID': 'k.bx@ya.ru',
                   'XMPP_TIMESTAMP': 1234567890}

        rv = app(environ)
        self.assertEqual(list(rv), ["I'll pass that onto foo"])
        self.assertEqual(
            MESSAGE_QUEUE['foo'].get(),
            ('message', {'body': u'[2009-02-13 23:31:30Z] k.bx@ya.ru: boo!',
                         'to': u'foo'}))

    def test_tell_ru(self):
        environ = {'MESSAGE': u'передать foo boo!',
                   'XMPP_JID': 'k.bx@ya.ru',
                   'XMPP_TIMESTAMP': 1234567890}

        rv = app(environ)
        self.assertEqual(list(rv), [u"ок, передам"])
        self.assertEqual(
            MESSAGE_QUEUE['foo'].get(),
            ('message', {'body': u'[2009-02-13 23:31:30Z] k.bx@ya.ru: boo!',
                         'to': u'foo'}))

    def test_tell_in_muc(self):
        environ = {'MESSAGE': 'tell foo boo!',
                   'mucnick': 'k.bx',
                   'mucroom': 'xmppflask@conference.jabber.org',
                   'XMPP_JID': 'xmppflask@conference.jabber.org/k.bx',
                   'XMPP_TIMESTAMP': 1234567890}

        rv = app(environ)
        self.assertEqual(list(rv), ["I'll pass that onto foo"])
        self.assertEqual(
            MESSAGE_QUEUE['xmppflask@conference.jabber.org/foo'].get(),
            ('message', {'body': u'[2009-02-13 23:31:30Z] k.bx: boo!',
                         'to': u'xmppflask@conference.jabber.org/foo'}))


class DispatchMessageQueueTestCase(unittest.TestCase):

    def setUp(self):
        self.expected = ('message',
                         {'body': u'[2009-02-13 23:31:30Z] k.bx: boo!',
                          'to': u'xmppflask@conference.jabber.org/foo'})
        MESSAGE_QUEUE['foo'].put(self.expected)

    def tearDown(self):
        MESSAGE_QUEUE.clear()

    def test_pass_message_on_available_presence(self):
        environ = {'XMPP_EVENT': 'presence',
                   'XMPP_JID': 'foo',
                   'type': 'available'}

        rv = app(environ)
        self.assertEqual(list(rv), [self.expected])

    def test_pass_message_only_once(self):
        environ = {'XMPP_EVENT': 'presence',
                   'XMPP_JID': 'foo',
                   'type': 'available'}

        rv = app(environ)
        self.assertEqual(list(rv), [self.expected])

        rv = app(environ)
        self.assertEqual(list(rv), [])

    def test_dont_pass_anything_for_others(self):
        environ = {'XMPP_EVENT': 'presence',
                   'XMPP_JID': 'bar',
                   'type': 'available'}

        rv = app(environ)
        self.assertEqual(list(rv), [])
