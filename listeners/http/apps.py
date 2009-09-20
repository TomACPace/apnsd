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
import pyrant

class APNSAppsResource(resource.Resource):
    """
    A resource which handles all calls to /apps/.
    Requests to /apps/.../ are treated as messages to be forwarded to APNS.
    """
    isLeaf = True
    def __init__(self, daemon, **kwds):
        resource.Resource.__init__(self)
        self.apns_daemon    = daemon
        self.cert_folder    = kwds.get("cert_folder")
        self.tyrant_host    = kwds.get("tyrant_host", "localhost")
        self.tyrant_port    = kwds.get("tyrant_port", 1978)
        self.tyrant         = pyrant.Tyrant(host = self.tyrant_host,
                                            port = self.tyrant_port)

    def render_GET(self, request):
        parts = request.path.split("/")
        logging.debug("Rendering GET Request: " + str(parts))
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

        content = request.content.read()

        logging.debug("Request Headers: " + str(request.args))
        logging.debug("Request Path: " + str(parts))
        return "OK"
