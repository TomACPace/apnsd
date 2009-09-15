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

class LineProtocol(LineReceiver):
    """
    This is the actual receiver of payload from local applications (or
    anywhere really) and forwards the received messages to the APNS daemon
    to be sent off to APNS land.
    """
    def __init__(self, daemon):
        self.apns_daemon    = daemon

    def lineReceived(self, line):
        print "Received Line: ", line
        # each line will have 3 thinsgs - appname,deviceToken,payload
        coma1 = line.find(",")
        coma2 = line.find(",", coma1 + 1)

        if coma1 <= 0 or coma2 <= 0:
            print "Disconnecting.  Invalid line: ", line
            self.transport.loseConnection()
            return 

        app_name        = line[ : coma1]
        device_token    = line[coma1 + 1 : coma2]
        payload         = line[coma2 + 1 : ]
        self.apns_daemon.sendMessage(app_name, device_token, payload)

class LineProtocolFactory(Factory):
    """
    Factory responsible for handling life cycle of LineProtocol objects.
    """
    def __init__(self, daemon, **kwds):
        self.apns_daemon = daemon
        # we change the interface from "all" to
        # localhost for security reasons...  if you really really mean to
        # make it all hosts then specify as all in the config file
        interface   = kwds.get("interface", "localhost")
        backlog     = kwds.get("backlog", 50)
        port        = kwds.get("port")
        print "Listening on Line Protocol on %s:%d" % (interface, port)
        daemon.reactor.listenTCP(port, self, backlog = backlog, interface = interface)

    def startedConnecting(self, connector):
        print "Started LineClient connection..."

    def buildProtocol(self, addr):
        print "Building LineProtocol Server %s:%u" % (addr.host, addr.port)
        return LineProtocol(self.apns_daemon)

    def clientConnectionLost(self, connector, reason):
        print "Lost Connection, Reason: ", reason

    def clientConnectionFailed(self, connector, reason):
        print "Failed Connection, Reason: ", reason

