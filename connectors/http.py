###############################################################################
#
# Copyright 2009, Sri Panyam
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################

from twisted.web import server, resource
import logging

class APNSResource(resource.Resource):
    isLeaf = True
    def __init__(self, daemon, **kwds):
        resource.Resource.__init__(self)
        self.apns_daemon = daemon

    def render_GET(self, request):
        parts = request.path.split("/")
        return "Please use POST requests"

    def render_POST(self, request):
        parts = request.path.split("/")
        payload = {}    # should be request body 
        if 'aps' not in payload:
            payload['aps'] = {}

        if 'badge' in request.args:
            payload['aps']['badge'] = request.args['badge'][0]
        if 'sound' in request.args:
            payload['aps']['sound'] = request.args['sound'][0]
        if 'alert' in request.args:
            payload['aps']['alert'] = request.args['alert'][0]

        content = reuqest.content.read()

        return "OK"

class APNSSite(server.Site):
    def __init__(self, daemon, **kwds):
        self.root_resource  = APNSResource(daemon, **kwds)
        self.apns_daemon    = daemon

        server.Site.__init__(self, self.root_resource)
        daemon.reactor.listenTCP(kwds['port'], self)


class Client(object):
    """
    A helper class used by applications for sending messages to the
    apns-daemon via Http protocol.
    """
    def __init__(self, host = "localhost", port = 90):
        self.serverHost = host
        self.serverPort = port

    def sendMessage(self, app, devtoken, payload):
        url = "http://%s:%d/%s/%s/" % (self.serverHost, self.serverPort, app, devtoken)

        import urllib, urllib2
        data = urllib.urlencode(payload)
        request = urllib2.Request(url, data)
        response =  urllib2.urlopen(req)
        return response.read()
