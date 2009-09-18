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

class APNSRootResource(resource.Resource):
    """
    The root apns resource.
    """
    def __init__(self, daemon, **kwds):
        import admin, apps
        resource.Resource.__init__(self)
        self.apns_daemon = daemon
        self.admin_resource = admin.APNSAdminResource(daemon, **kwds)
        self.apps_resource  = apps.APNSAppsResource(daemon, **kwds)
        self.putChild("admin", self.admin_resource)
        self.putChild("apps", self.apps_resource)

class APNSSite(server.Site):
    def __init__(self, daemon, **kwds):
        self.apns_daemon    = daemon
        self.root_resource  = APNSRootResource(daemon, **kwds)

        server.Site.__init__(self, self.root_resource)

        # we are changing the default interface from "all" to
        # localhost for security reasons...  if you really really mean to
        # make it all hosts then specify as all in the config file
        interface   = kwds.get("interface", "localhost")
        backlog     = kwds.get("backlog", 50)
        secure      = kwds.get("secure", False)
        port        = kwds.get("port", 443 if secure else 80)

        if 'cert_folder' in kwds:
            import os
            try:
                os.makedirs(os.path.abspath(kwds['cert_folder']))
            except OSError, e:
                if e.errno != 17: raise

        # check other things like whether we want to do SSL 
        # and which host/port we want to listen and so on...
        print "Listening on APNSSite on %s:%d" % (interface, port)
        daemon.reactor.listenTCP(port, self, backlog = backlog, interface = interface)

