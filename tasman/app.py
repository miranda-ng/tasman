# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
#

import datetime
import time
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
app.config['SVN_REPO_URL'] = 'http://svn.miranda-ng.org/main'
app.config['SVN_REV_URL'] = 'http://trac.miranda-ng.org/changeset/%d'
app.session_interface = MemorySessionInterface()
MESSAGE_QUEUE = defaultdict(Queue)


@app.route(u'test', defaults={'lang': 'en'})
@app.route(u'тест', defaults={'lang': 'ru'})
def test(**kwargs):
    """Simple test command"""
    return render_template('test.html')


@app.route(u'ping', defaults={'lang': 'en'})
@app.route(u'пинг', defaults={'lang': 'ru'})
def ping(**kwargs):
    """Not implemented right yet"""
    return render_template('ping.html')


@app.route(u'tell <string:nick> <string:message>', defaults={'lang': 'en'})
@app.route(u'передать <string:nick> <string:message>', defaults={'lang': 'ru'})
def tell(nick, message, **kwargs):
    """Sends to the specified user the message when he becomes available"""
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


@app.route(u'version', defaults={'lang': 'en'})
@app.route(u'версия', defaults={'lang': 'ru'})
@app.route(u'version <string:user>', defaults={'lang': 'en'})
@app.route(u'версия <string:user>', defaults={'lang': 'ru'})
def version(user=None, **kwargs):
    """Returns the user version info (XEP-0092)"""
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


@app.route('join <room> as <nick>')
def join(room, nick=None):
    yield 'join_room', {
        'room': room,
        'nick': nick or request.app_jid.user
    }
    yield 'ok'


@app.route(u'<any(beer):cmd> <string:nick>', defaults={'lang': 'en'})
@app.route(u'<any(пива,пиво):cmd> <string:nick>', defaults={'lang': 'ru'})
def beer(cmd, nick, lang):
    return render_template('beer.html')

if __name__ == '__main__':
    app.run('pydroid@xmpp.ru', 'RobotsShallRule!', 'sleekxmpp')

