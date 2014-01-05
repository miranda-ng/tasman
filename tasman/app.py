# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
#

from xmppflask import XmppFlask

app = XmppFlask('tasman')


@app.route(u'<any(test,тест):msg>')
def test(msg):
    return 'passed' if msg == 'test' else u'пассед'


@app.route(u'<any(ping,пинг):msg>')
def ping(msg):
    return 'pong' if msg == 'ping' else u'понг'
