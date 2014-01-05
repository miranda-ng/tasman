# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
#

import datetime
from Queue import Queue, Empty
from collections import defaultdict
from xmppflask import XmppFlask, request
from xmppflask.sessions import MemorySessionInterface


app = XmppFlask('tasman')
app.session_interface = MemorySessionInterface()
MESSAGE_QUEUE = defaultdict(Queue)


@app.route(u'<any(test,тест):msg>')
def test(msg):
    return 'passed' if msg == 'test' else u'пассед'


@app.route(u'<any(ping,пинг):msg>')
def ping(msg):
    return 'pong' if msg == 'ping' else u'понг'


@app.route(u'<any(tell,передать):cmd> <string:nick> <string:message>')
def tell(cmd, nick, message):
    if 'mucnick' in request.environ:
        to_jid = u'%s/%s' % (request.environ['mucroom'], nick)
        from_jid = request.environ['mucnick']
    else:
        to_jid = nick
        from_jid = request.environ['XMPP_JID']

    ts = datetime.datetime.utcfromtimestamp(request.environ['XMPP_TIMESTAMP'])
    MESSAGE_QUEUE[to_jid].put((
        'message',
        {'to': to_jid, 'body': '[%sZ] %s: %s' % (ts, from_jid, message)}
    ))

    if cmd == 'tell':
        return "I'll pass that onto %s" % nick
    elif cmd == u'передать':
        return u'ок, передам'


@app.route_presence(type='available')
def dispatch_queue():
    environ = request.environ
    if environ['XMPP_JID'] not in MESSAGE_QUEUE:
        return

    def flush():
        queue = MESSAGE_QUEUE[environ['XMPP_JID']]
        while True:
            try:
                cmd, payload = queue.get(block=False)
            except Empty:
                break
            else:
                yield cmd, payload

    return flush()
