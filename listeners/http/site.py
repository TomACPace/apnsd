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
        import admin
        resource.Resource.__init__(self)
        self.apns_daemon = daemon
        self.admin_resource = admin.APNSAdminResource(daemon, **kwds)
        self.apps_resource  = admin.APNSAppsResource(daemon, **kwds)
        self.putChild("admin", self.admin_resource)
        self.putChild("apps", self.apps_resource)

class APNSSite(server.Site):
    def __init__(self, daemon, **kwds):
        self.apns_daemon    = daemon
        self.root_resource  = APNSRootResource(daemon, **kwds)

        server.Site.__init__(self, self.root_resource)

        # check other things like whether we want to do SSL 
        # and which host/port we want to listen and so on...
        daemon.reactor.listenTCP(kwds['port'], self)

