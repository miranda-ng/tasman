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

try:
    import pysvn
except ImportError:
    pysvn = None


app = XmppFlask('tasman')
app.config['TRAC_URL'] = 'http://trac.miranda-ng.org/rpc'
app.config['SVN_REPO_URL'] = 'http://svn.miranda-ng.org/main'
app.config['SVN_REV_URL'] = 'http://trac.miranda-ng.org/changeset/%d'
app.session_interface = MemorySessionInterface()
MESSAGE_QUEUE = defaultdict(Queue)
svn = pysvn.Client()


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


@app.route(u'r<int:rev>', defaults={'cmd': 'r'})
@app.route(u'<any(rev,revision,commit):cmd> <int:rev>')
@app.route(u'<any(рев,ревизия,коммит):cmd> <int:rev>')
def revision(cmd, rev):
    if pysvn is None:
        app.logger.error('pysvn package not found')
        return
    res, err = None, None
    try:
        log = svn.log(app.config['SVN_REPO_URL'],
                      revision_start=pysvn.Revision(
                          pysvn.opt_revision_kind.number, rev),
                      limit=1)
    except pysvn.ClientError:
        err = 'No such revision %s' % rev
    else:
        if not log:
            err = 'No such revision %s' % rev
        else:
            offset = int(time.time()) - int(time.mktime(time.gmtime()))
            res = dict(log[0].items())
            res['revision'] = res['revision'].number
            res['url'] = app.config['SVN_REV_URL'] % res['revision']
            res['date'] = datetime.datetime.fromtimestamp(
                int(res['date']) - offset).isoformat(sep=' ') + 'Z'

    return render_template('revision.html', info=res, error=err)
