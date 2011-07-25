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

import logging, json

class LineClient(object):
    """
    A helper class used by applications for sending messages to the line
    protocol server, instead of having to manage socket connections and
    data formatting manually.
    """
    def __init__(self, app, host = "localhost", port = 90):
        logging.debug("Creating line connector client...")
        self.app_id = app
        self.serverHost = host
        self.serverPort = port
        self.connSocket = None

    def sendLine(self, line):
        if not self.connSocket:
            import socket
            logging.debug("Connecting to daemon at: %s:%d" % (self.serverHost, self.serverPort))
            self.connSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connSocket.connect((self.serverHost, self.serverPort))
            # tell the server which app we are sending messages for
            self.connSocket.send("connect: " + self.app_id)

        # now send the line command
        return self.connSocket.send("line: " + line + "\r\n")

    def sendMessage(self, devtoken, payload, identifier = None, expiry = None):
        if type(payload) not in (str, unicode):
            payload = json.dumps(payload)
        line = "%s,%s,%s,%s,%s" % (app, devtoken, identifier, expiry, payload)
        result = self.sendLine(line)
        logging.debug("Send message Result: " + str(result))
        return 0, "Successful"

