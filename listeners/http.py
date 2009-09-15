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
from twisted.web import error as twerror

# to do errors do this:
# page = error.NoResource(message  "Resource %s not found" % request.URLPath())
# return page.render(request)

def ensure_request_authenticated(auth_function):
    """
    A decorator that ensures that the requests handled by render and
    render_METHOD methods in a resource handler are authenticated.
    We usually do this to check that all requests have some auth headers
    set.
    """
    def ensure_request_authenticated_decorator(func):
        def ensure_request_authenticated_method(resource, request):
            if auth_function and not auth_function(resource, request):
                return "Not Authenticated Error"
            else:
                return func(resource, request)
        return ensure_request_authenticated_method
    return ensure_request_authenticated_decorator

class APNSRootResource(resource.Resource):
    """
    The root apns resource.
    """
    def __init__(self, daemon, **kwds):
        resource.Resource.__init__(self)
        self.apns_daemon = daemon
        self.admin_resource = APNSAdminResource(daemon, **kwds)
        self.apps_resource  = APNSAppsResource(daemon, **kwds)
        self.putChild("admin", self.admin_resource)
        self.putChild("apps", self.apps_resource)

class APNSAdminResource(resource.Resource):
    """
    The admin resource handler.
    Requests to /admin/ will usually be made from the webserver that is
    acting as the frontend for the admin (eg gae).  The admin does things
    like manage app specific passwords and the app's provisioning
    certificates.
    Also the admin resource manages users in the system.
    """
    def __init__(self, daemon, **kwds):
        resource.Resource.__init__(self)
        self.apns_daemon = daemon
        self.apps_resource = APNSAdminAppsResource(daemon, **kwds)
        self.users_resource = APNSAdminUsersResource(daemon, **kwds)
        self.putChild("apps", self.apps_resource)
        self.putChild("users", self.users_resource)

class APNSAdminUsersResource(resource.Resource):
    """
    The users section within in the admin resource.
    Handles requests to the following /admin/users/ urls:
        1. /create/?username=<email/username>&passwd=<password>&otherparams
            Creates a new user with the username and password.  The
            username can be an email or other wise.
            Other noteworthy parameters can also be passed here. 
        2. /delete/?username=<email/username>
            Deleting an app by the given name.
        3. /password/
            Changes the password for a user.  The request MUST contain the
            old and the new passwords.  Also through out the http
            connector (and listener) we need uniform password schemes.
    """
    isLeaf = True
    def __init__(self, daemon, **kwds):
        resource.Resource.__init__(self)
        self.apns_daemon = daemon

    def render(self, request):
        parts = request.path.split("/")

class APNSAdminAppsResource(resource.Resource):
    """
    The apps section within in the admin resource.
    Handles requests to the following /admin/apps/ urls:
        1. /create/?appname=<appname>&user=<username>&passwd=passwd
            Creates a new app with the app name.
            The username (or email) and password are mandatory fields.
        2. /delete/?appname=<appname>&username=<username>
            Deleting an app by the given name belonging to a specific user.
        3.  /certupload/?certtype=<certtype>&username=<username>&appname=<appname>
            Uploads dev/provisioning certificate files for an app.
            The certificate file will be the POST data and the certificate
            type (eg "dev" or "prod") will be specified in the GET
            parameter.
        4. /passwd/?username=<username>&appname=<appname>
            Change the password.  When doing this both the old AND the new
            passwords must be provided.
    """
    isLeaf = True
    def __init__(self, daemon, **kwds):
        resource.Resource.__init__(self)
        self.apns_daemon = daemon

    def render(self, request):
        parts = request.path.split("/")

class APNSAppsResource(resource.Resource):
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

        server.Site.__init__(self, self.root_resource)

        # check other things like whether we want to do SSL 
        # and which host/port we want to listen and so on...
        daemon.reactor.listenTCP(kwds['port'], self)

