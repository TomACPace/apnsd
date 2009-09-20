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

class LineClient(object):
    """
    A helper class used by applications for sending messages to the line
    protocol server, instead of having to manage socket connections and
    data formatting manually.
    """
    def __init__(self, port = 90):
        logging.debug("Creating line connector client...")
        self.serverPort = port
        self.servers = {}

    def sendMessage(self, app, devtoken, payload):
        if app not in self.servers:
            logging.debug("Adding app to list: " + app)
            self.servers[app] = {'socket': None}

        if not self.servers[app]['socket']:
            import socket
            logging.debug("Connecting to daemon for app: " + app)
            newsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newsocket.connect(("localhost", self.serverPort))
            self.servers[app]['socket'] = newsocket

        line = str(app) + "," + devtoken + "," + payload.replace("\n", " ")
        result = self.servers[app]['socket'].send(line + "\r\n")
        logging.debug("Send message Result: " + result)
        return 0, "Successful"
