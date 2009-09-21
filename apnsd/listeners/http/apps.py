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
from json import json_response, json_decode, json_encode, api_result
import decorators as decos
import utils, auth, errors, logging
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

    @decos.require_parameters("username")
    @decos.ensure_request_authenticated(auth.basic_auth, prefix="user")
    def render(self, request):
        """
        We handle GET or POST requests to this handler.  This will be of
        the form:
        /apps/<appname>/<device_token>/?args
        """
        parts = request.path.split("/")[2:]
        if len(parts) < 2:
            return errors.no_resource_error(request)

        appname     = parts[0]
        dev_token   = parts[1]
        username    = utils.get_reqvar(request, "username")
        content     = request.content.read()
        badge       = utils.get_reqvar(request, "badge")
        sound       = utils.get_reqvar(request, "sound")
        alert       = utils.get_reqvar(request, "alert")
        env         = utils.get_reqvar(request, "env")

        if content:
            payload = json_decode(content)
            if 'aps' not in payload:
                payload['aps'] = {}
        else:
            payload = {'aps': {}}

        if badge:
            payload['aps']['badge'] = badge
        if sound:
            payload['aps']['sound'] = sound
        if alert:
            payload['aps']['alert'] = alert

        logging.debug("Payload: " + json_encode(payload))

        appkey = "%s$%s$%s" % (env, username, appname)
        self.apns_daemon.sendMessage(appname, dev_token, json_encode(payload))

        return json_response(request, 0, "OK")

