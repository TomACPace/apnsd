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
# SRI: my knowledge of good python packaging & structuring is rusty
# I tested by starting python from the level below, and the line below
# worked, but I'm not sure how, where it would work in general
# eg if you were importing this module from Django, would the import below
# work?
from apnsd.feedback import APNSFeedback

class LineClient(object):
    """
    A helper class used by applications for sending messages to the line
    protocol server, instead of having to manage socket connections and
    data formatting manually.
    """
    def __init__(self, app, app_mode, port = 90, host = "localhost", readTimeout = 1.0, readBufSize=2048):
        logging.debug("Creating line connector client...")
        self.app_id = app
        self.app_mode = app_mode
        self.serverPort = port
        self.serverHost = host
        self.connSocket = None
        self.readTimeout = readTimeout
        self.readBufSize = readBufSize

    def _connectIfRequired(self):
        if not self.connSocket:
            import socket
            logging.debug("Connecting to daemon at: %s:%d" % (self.serverHost, self.serverPort))
            self.connSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connSocket.connect((self.serverHost, self.serverPort))
            # tell the server which app we are sending messages for
            self.connSocket.send("connect: " + self.app_id + ":" + self.app_mode + "\r\n")

    def sendLine(self, line):
        self._connectIfRequired()
        return self.connSocket.send("line: " + line + "\r\n")

    def getFeedback(self):
        self._connectIfRequired()
        logging.debug("requesting feedback...")
        oldTimeout = self.connSocket.gettimeout()
        self.connSocket.send("feedback:\r\n")

        self.connSocket.settimeout(self.readTimeout)
        totalString = ""
        try:
            receivedChunk = "XXX" # just make this non empty so the while loop doesn't exit straight away - we throw it away anyway
            # nb: we can't check for the end marker in the chunk because the end
            # marker might be split up amongst chunks
            # SRI: note that this means if for some reason this
            # call is somehow reading the data from another call, then
            # we will lose this data.. not sure if this is possible with how it's used
            # atm though
            # ie: consider receiving: TIMESTAMP:LENGTH:TOKEN:ENDTIMESTAMP2:LE
            # not sure if it's easy to get around because you've already
            # read read the start of the next feedback item list from the socket
            # you'd have to somehow share it, or make sure that only
            # one read can ever be queued up
            # ALSO: There might be soemthign on the web.. a pattern.. which
            # already solves this problem.. I might have a look later
            while receivedChunk and not APNSFeedback.stringContainsEnd(totalString):

                receivedChunk = self.connSocket.recv(self.readBufSize)
                totalString += receivedChunk

        except exception.timeout, e:
            logging.warning("Timed out reading on socket.. will attempt to process received data")

        logging.debug("Received: " + totalString)
        self.connSocket.settimeout(oldTimeout)
        # SRI: note that this itself might error...
        return APNSFeedback.listFromString(totalString)
        
    def sendMessage(self, devtoken, payload, identifier = None, expiry = None):
        if type(payload) not in (str, unicode):
            payload = json.dumps(payload)
        line = "%s,%s,%s,%s" % (devtoken, str(identifier), str(expiry), payload)
        result = self.sendLine(line)
        logging.debug("=" * 80)
        logging.debug("Send message Result: " + str(result))
        if identifier is not None:
            # since an identifier was specified we must be seding an
            # extended notification. So read a response from the server
            # response regarding the status of the notification
            # Response is binary of the format: <count><payload>
            pass
        return 0, "Successful"
