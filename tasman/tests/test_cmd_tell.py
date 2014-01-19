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
from tasman.app import app, MESSAGE_QUEUE


class TellCmdTestCase(unittest.TestCase):
    def tearDown(self):
        MESSAGE_QUEUE.clear()

    def test_tell(self):
        environ = {'xmpp.body': 'tell foo boo!',
                   'xmpp.jid': 'tasman@xmpp.ru',
                   'xmpp.stanza_type': 'chat',
                   'xmpp.timestamp': 1234567890}

        rv = app(environ)
        self.assertEqual(list(rv), ["I'll pass that onto foo"])
        self.assertEqual(
            MESSAGE_QUEUE['foo'].get(),
            ('message',
             {'body': u'[2009-02-13 23:31:30Z] tasman@xmpp.ru: boo!',
              'to': u'foo'}))

    def test_tell_ru(self):
        environ = {'xmpp.body': u'передать foo boo!',
                   'xmpp.jid': 'tasman@xmpp.ru',
                   'xmpp.stanza_type': 'chat',
                   'xmpp.timestamp': 1234567890}

        rv = app(environ)
        self.assertEqual(list(rv),
                         [u"ок, как появится foo - обязательно передам"])
        self.assertEqual(
            MESSAGE_QUEUE['foo'].get(),
            ('message',
             {'body': u'[2009-02-13 23:31:30Z] tasman@xmpp.ru: boo!',
              'to': u'foo'}))

    def test_tell_in_muc(self):
        environ = {'xmpp.body': 'tell foo boo!',
                   'xmpp.stanza_type': 'groupchat',
                   'xmpp.jid': JID('xmppflask@conference.jabber.org/tasman'),
                   'xmpp.timestamp': 1234567890}

        rv = app(environ)
        self.assertEqual(list(rv), ["I'll pass that onto foo"])
        self.assertEqual(
            MESSAGE_QUEUE['xmppflask@conference.jabber.org/foo'].get(),
            ('message', {'body': u'[2009-02-13 23:31:30Z] tasman: boo!',
                         'to': u'xmppflask@conference.jabber.org/foo'}))


class DispatchMessageQueueTestCase(unittest.TestCase):
    def setUp(self):
        self.expected = ('message',
                         {'body': u'[2009-02-13 23:31:30Z] tasman: boo!',
                          'to': u'xmppflask@conference.jabber.org/foo'})
        MESSAGE_QUEUE['foo'].put(self.expected)

    def tearDown(self):
        MESSAGE_QUEUE.clear()

    def test_pass_message_on_available_presence(self):
        environ = {'xmpp.stanza': 'presence',
                   'xmpp.jid': 'foo',
                   'type': 'available'}

        with app.request_context(environ):
            rv = app(environ)
            self.assertEqual(list(rv), [self.expected])

    def test_pass_message_only_once(self):
        environ = {'xmpp.stanza': 'presence',
                   'xmpp.jid': 'foo',
                   'type': 'available'}

        with app.request_context(environ):
            rv = app(environ)
            self.assertEqual(list(rv), [self.expected])

            rv = app(environ)
            self.assertEqual(list(rv), [])

    def test_dont_pass_anything_for_others(self):
        environ = {'xmpp.stanza': 'presence',
                   'xmpp.jid': 'bar',
                   'type': 'available'}

        with app.request_context(environ):
            rv = app(environ)
            self.assertEqual(list(rv), [])
