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

from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory, Protocol
import logging

class LineProtocol(LineReceiver):
    """
    This is the actual receiver of payload from local applications (or
    anywhere really) and forwards the received messages to the APNS daemon
    to be sent off to APNS land.
    """
    def __init__(self, daemon):
        self.apns_daemon    = daemon

    def lineReceived(self, line):
        # each line will have 5 things:
        #   appname,deviceToken,identifier,expiry,payload
        coma1 = line.find(",")
        coma2 = line.find(",", coma1 + 1)
        coma3 = line.find(",", coma2 + 1)
        coma4 = line.find(",", coma3 + 1)

        if coma1 <= 0 or coma2 <= 0 or coma3 <= 0 or coma4 <= 0:
            logging.debug("Invalid line: " + line)
            logging.debug("Required Format: <appname>,<device token>,<identifier_or_None>,<expiry_or_None>,<payload>")
        else:
            app_name        = line[ : coma1]
            device_token    = line[coma1 + 1 : coma2]
            identifier      = line[coma2 + 1 : coma3]
            expiry          = line[coma3 + 1 : coma4]
            payload         = line[coma4 + 1 : ]
            logging.debug("Received Line: " + line)
            if identifier.lower() in ("none", "null", "nil"):
                identifier = None
            if expiry.lower() in ("none", "null", "nil"):
                expiry = None
            self.apns_daemon.sendMessage(app_name, device_token, payload, identifier, expiry)

class LineProtocolFactory(Factory):
    """
    Factory responsible for handling life cycle of LineProtocol objects.
    """
    def __init__(self, daemon, **kwds):
        self.apns_daemon = daemon
        backlog     = kwds.get("backlog", 50)
        port        = kwds.get("port")
        interface   = kwds.get("interface", None)
        if interface:
            logging.info("Listening on Line Protocol on %s:%d" % (interface, port))
        else:
            logging.info("Listening on Line Protocol on :%d" % port)

    def startedConnecting(self, connector):
        logging.info("Started LineClient connection...")

    def buildProtocol(self, addr):
        print "Self: ", dir(self)
        logging.info("Building LineProtocol Server %s:%u" % (addr.host, addr.port))
        return LineProtocol(self.apns_daemon)

    def clientConnectionLost(self, connector, reason):
        logging.info("Lost Connection, Reason: " + str(reason))

    def clientConnectionFailed(self, connector, reason):
        logging.info("Failed Connection, Reason: " + str(reason))

    def dataAvailableForClient(self, data, app_name):
        print "AppName: ", str(map(ord, data))

