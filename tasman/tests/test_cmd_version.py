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

    def test_version(self):
        environ = {'xmpp.body': 'version', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}
        info = {'os': 'Linux', 'name': 'xmppflask', 'version': '1.0'}

        with app.request_context(environ):
            rv = app(environ)
            cmd, payload = rv.next()
            self.assertEqual(cmd, 'version')
            rv = rv.send(info)
            self.assertEquals(rv,
                              u'{name} {version} @ {os}'.format(**info))

    def test_version_ru(self):
        environ = {'xmpp.body': u'версия', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}
        info = {'os': 'Linux', 'name': 'xmppflask', 'version': '1.0'}

        with app.request_context(environ):
            rv = app(environ)
            cmd, payload = rv.next()
            self.assertEqual(cmd, 'version')
            rv = rv.send(info)
            self.assertEquals(rv,
                              u'{name} {version} @ {os}'.format(**info))

    def test_version_hidden(self):
        environ = {'xmpp.body': u'version', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}

        with app.request_context(environ):
            rv = app(environ)
            cmd, payload = rv.next()
            self.assertEqual(cmd, 'version')
            rv = rv.send(None)
            self.assertEquals(rv, u"seems he's hiding from NSA")

    def test_version_hidden_ru(self):
        environ = {'xmpp.body': u'версия', 'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}

        with app.request_context(environ):
            rv = app(environ)
            cmd, payload = rv.next()
            self.assertEqual(cmd, 'version')
            rv = rv.send(None)
            self.assertEquals(rv, u"он зашифровался")

    def test_version_user(self):
        environ = {'xmpp.body': 'version that@guy',
                   'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}

        with app.request_context(environ):
            rv = app(environ)
            self.assertEqual(list(rv), [u"who's that?"])

    def test_version_user_ru(self):
        environ = {'xmpp.body': u'версия that@guy',
                   'xmpp.jid': JID('tasman@xmpp.ru'),
                   'xmpp.stanza_type': 'chat'}

        with app.request_context(environ):
            rv = app(environ)
            self.assertEqual(list(rv), [u"а это еще кто?"])

    def test_version_user_in_muc(self):
        environ = {'xmpp.body': 'version tasman',
                   'xmpp.jid': JID('chat@xmpp.ru/somebody'),
                   'xmpp.stanza_type': 'groupchat'}

        with app.request_context(environ):
            rv = app(environ)
            cmd, payload = rv.next()
            self.assertEqual(cmd, 'version')
            self.assertEqual(payload['jid'], 'chat@xmpp.ru/tasman')
