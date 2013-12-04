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

import logging, urllib2

class HttpClient(object):
    """
    A helper class used by applications for sending messages to the
    apns-daemon via Http protocol.
    """
    def __init__(self, username, password, appname, 
                 envType = "development", host = "http://localhost", port = 80):
        self.serverUsername = username
        self.serverPassword = password
        self.appName        = appname
        self.envType        = envType
        self.serverHost     = host
        self.serverPort     = port
        self.baseUrl        = "%s:%d/apps/%s" % (self.serverHost, self.serverPort, self.appName)

    def sendSimpleMessage(self, devtoken, badge = "", sound = "", alert = ""):
        url = "%s/%s/?username=%s&env=%s" % (self.baseUrl, devtoken, self.serverUsername, self.envType)
        if badge:
            url += ("&badge=%d" % int(badge))
        if sound:
            url += ("&sound=%s" % urllib2.quote(sound))
        if alert:
            url += ("&alert=%s" % urllib2.quote(alert))

        request = urllib2.Request(url)
        try:
            response =  urllib2.urlopen(request)
            return 0, response.read()
        except urllib2.HTTPError, he:
            return -1, he.read()

    def sendRawMessage(self, devtoken, payload):
        url = "%s/%s/?username=%s&env=%s" % (self.baseUrl, devtoken, self.serverUsername, self.envType)
        data = urllib2.quote(payload)
        request = urllib2.Request(url, data)
        try:
            response =  urllib2.urlopen(request)
            return 0, response.read()
        except urllib2.HTTPError, he:
            return -1, he.read()
