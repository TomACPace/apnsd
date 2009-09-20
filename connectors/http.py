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

import logging

class HttpClient(object):
    """
    A helper class used by applications for sending messages to the
    apns-daemon via Http protocol.
    """
    def __init__(self, password, host = "localhost", port = 80):
        self.serverPassword = pasword
        self.serverHost     = host
        self.serverPort     = port

    def sendMessage(self, app, devtoken, payload):
        url = "http://%s:%d/%s/%s/" % (self.serverHost, self.serverPort, app, devtoken)

        import urllib, urllib2
        data = urllib.urlencode(payload)
        request = urllib2.Request(url, data)
        response =  urllib2.urlopen(req)
        return response.read()
