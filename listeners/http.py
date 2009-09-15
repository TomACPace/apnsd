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

class APNSRootResource(resource.Resource):
    """
    The root apns resource.
    """
    def __init__(self, daemon, **kwds):
        resource.Resource.__init__(self)
        self.apns_daemon = daemon

class APNSAdminResource(resource.Resource):
    """
    The admin resource handler.
    Requests to /admin/ will usually be made from the webserver that is
    acting as the frontend for the admin (eg gae).  The admin does things
    like manage app specific passwords and the app's provisioning
    certificates.
    """
    isLeaf = True
    def __init__(self, daemon, **kwds):
        resource.Resource.__init__(self)
        self.apns_daemon = daemon

    def render_GET(self, request):
        """
        Handle's GET requests.
        Only an app's provisioning certificate file names are allowed and
        nothing else for now.
        In most cases, the adming front end (not the resource) will be
        pushed with information we want to be viewed and monitored.  So
        logs and usage data will be pushed.
        """
        parts = request.path.split("/")
        return "Please use POST requests"

    def render_POST(self, request):
        """ 
        Handle's POST requests to the admin interface.
        POST requests can only be:
        1. /apps/create/?appname=<appname>&passwd=passwd
            Creating a new app with the app name and the password of the
            app as GET parameters.
        2. /apps/<appname>/delete
            Deleting an app by the given name.
        3. /apps/<appname>/certupload/?certtype=<certtype>
            Uploads dev/provisioning certificate files for an app.
            The certificate file will be the POST data and the certificate
            type (eg "dev" or "prod") will be specified in the GET
            parameter.
        4. /apps/<appname>/passwd/
            Change the password.  When doing this both the old AND the new
            passwords must be provided.
        """

class APNSAppResource(resource.Resource):
    """
    A resource which handles all calls to /apps/.
    Requests to /apps/.../ are treated as messages to be forwarded to APNS.
    """
    isLeaf = True
    def __init__(self, daemon, **kwds):
        resource.Resource.__init__(self)
        self.apns_daemon = daemon

    def render_GET(self, request):
        parts = request.path.split("/")
        print "Rendering GET Request: ", parts
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

        print "request headers: ", request.args
        print "request path: ", parts
        print "request content: ", request.content.read()
        print "Rendering POST Request: ", parts, dir(request)
        return "OK"

class APNSSite(server.Site):
    def __init__(self, daemon, **kwds):
        self.apns_daemon    = daemon
        self.root_resource  = APNSRootResource(daemon, **kwds)
        self.admin_resource = APNSAdminResource(daemon, **kwds)
        self.apps_resource  = APNSAppsResource(daemon, **kwds)
        self.root_resource.putChild("admin", self.admin_resource)
        self.root_resource.putChild("apps", self.apps_resource)

        server.Site.__init__(self, self.root_resource)

        # check other things like whether we want to do SSL 
        # and which host/port we want to listen and so on...
        daemon.reactor.listenTCP(kwds['port'], self)

