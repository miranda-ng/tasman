# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
#

import datetime
import urlparse
import xmlrpclib
from copy import copy
from Queue import Queue, Empty
from collections import defaultdict
from xmppflask import JID
from xmppflask import XmppFlask, request, render_template
from xmppflask.sessions import MemorySessionInterface


app = XmppFlask('tasman')
app.config['TRAC_URL'] = 'http://trac.miranda-ng.org/rpc'
app.session_interface = MemorySessionInterface()
MESSAGE_QUEUE = defaultdict(Queue)


@app.route(u'<any(test,тест):cmd>')
def test(cmd):
    return render_template('test.html')


@app.route(u'<any(ping,пинг):cmd>')
def ping(cmd):
    return render_template('ping.html')


@app.route(u'<any(tell,передать):cmd> <string:nick> <string:message>')
def tell(cmd, nick, message):
    if request.type == 'groupchat':
        to_jid = JID(request.jid)
        to_jid.resource = nick
        from_jid = request.username
    else:
        to_jid = nick
        from_jid = request.environ['xmpp.jid']

    ts = datetime.datetime.utcfromtimestamp(request.environ['xmpp.timestamp'])
    MESSAGE_QUEUE[to_jid].put((
        'message',
        {'to': to_jid, 'body': '[%sZ] %s: %s' % (ts, from_jid, message)}
    ))

    return render_template('tell.html')


@app.route_presence(type='available')
def dispatch_queue():
    if request.jid not in MESSAGE_QUEUE:
        return

    def flush():
        queue = MESSAGE_QUEUE[request.jid]
        while True:
            try:
                cmd, payload = queue.get(block=False)
            except Empty:
                break
            else:
                yield cmd, payload

    return flush()


@app.route(u'<any(version,версия):cmd>')
@app.route(u'<any(version,версия):cmd> <string:user>')
def version(cmd, user=None):
    info = None

    if request.type == 'groupchat':
        if user is None:
            jid = request.jid
            user = jid.user
        else:
            jid = copy(request.jid)
            jid.resource = user
    elif user:
        info = None
        user = None
    else:
        jid = request.jid
        user = jid.user

    if user:
        info = yield 'version', {'jid': jid}
        if info and not any(info.values()):
            info = None

    yield render_template('version.html', info=info, user=user)


@app.route(u'#<int:idx>', defaults={'cmd': '#'})
@app.route(u'<any(issue,ticket,bug):cmd> <int:idx>')
@app.route(u'<any(тикет,баг,проблема):cmd> <int:idx>')
def ticket(cmd, idx):
    proxy = xmlrpclib.ServerProxy(app.config['TRAC_URL'])
    info, error, url = None, None, None
    try:
        idx, created_at, changed_at, info = proxy.ticket.get(idx)
    except xmlrpclib.Fault as err:
        error = err.faultString
    else:
        items = list(urlparse.urlsplit(app.config['TRAC_URL']))
        items[1] = items[1].split('@')[-1]
        items[2] = 'ticket/%d' % idx
        url = urlparse.urlunsplit(items)
    return render_template('ticket.html', info=info, error=error, url=url)
