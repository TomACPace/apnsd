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
        self.curr_app_id    = None
        self.curr_app_mode  = None

    def logUsage(self, line):
        logging.debug("Invalid line: " + line)
        logging.debug("Usage: ")
        logging.debug("     connect: <app_id>:<app_mode = 'rel' or 'dev'>")
        logging.debug("     line: <device token>,<identifier_or_None>,<expiry_or_None>,<payload>")

    def lineReceived(self, line):
        # each line will have:
        #   <command> : <command_data>
        #
        #   The following commands are supported now:
        #   "connect"   -   Sets the "app" the client is responsible for
        #                   now now onwards.
        #   "line"      -   Sends a line of data to apple and has the format: 
        #                       deviceToken,identifier,expiry,payload
        line = line.strip()
        if line.startswith("connect:"):
            line = line[8:]
            self.curr_app_id, self.curr_app_mode = [l.strip() for l in line.split(":")]
            logging.debug("Current App changed to '%s:%s'" % (self.curr_app_mode, self.curr_app_id))
        elif line.startswith("line:"):
            line = line[5:]
            if not self.curr_app_id:
                logging.warning("App ID has not yet been set.  Expecting 'connect' command first")
            else:
                coma1 = line.find(",")
                coma2 = line.find(",", coma1 + 1)
                coma3 = line.find(",", coma2 + 1)
                if coma3 <= 0:
                    return self.logUsage(line)
                device_token    = line[ : coma1]
                identifier      = line[coma1 + 1 : coma2].strip()
                expiry          = line[coma2 + 1 : coma3].strip()
                payload         = line[coma3 + 1 : ]
                logging.debug("Received Line: " + line)
                if identifier.lower() in ("none", "null", "nil",""):
                    identifier = None
                if expiry.lower() in ("none", "null", "nil",""):
                    expiry = None
                self.apns_daemon.sendMessage(self.curr_app_id, self.curr_app_mode,
                                             device_token, payload, identifier, expiry)
        else:
            return self.logUsage(line)

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
        logging.info("Building LineProtocol Server %s:%u" % (addr.host, addr.port))
        return LineProtocol(self.apns_daemon)

    def clientConnectionLost(self, connector, reason):
        logging.info("Connection to Client Lost, Reason: " + str(reason))

    def clientConnectionFailed(self, connector, reason):
        logging.info("Connection to Client Failed, Reason: " + str(reason))

    def dataAvailableForClient(self, data, app_name, app_mode):
        """
        Called by the daemon when data from Apple has arrived for clients.
        """
        print "%s:%s - Data Received: " % (app_mode, app_name), str(map(ord, data))

