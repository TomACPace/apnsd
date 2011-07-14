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

import threading, Queue, optparse, os, logging
from twisted.internet.protocol import ReconnectingClientFactory, Protocol
import constants, errors, utils

class APNSProtocol(Protocol):
    def __init__(self, messageQueue):
        """ Initialises the protocol with the message queue. """
        self.messageQueue = messageQueue

    def closeConnection(self):
        """
        Closes the transport.
        """
        self.transport.loseConnection()

    def connectionMade(self):
        """
        After a connection is made we send out messages in our queue
        """
        while not self.messageQueue.empty():
            deviceToken, payload, identifier, expiry = self.messageQueue.get()
            self.sendMessage(deviceToken, payload, identifier, expiry)

    def dataReceived(self, data):
        """
        Called when server has sent us some data.  For now we just 
        print out the data.
        """
        logging.debug("APNS Data [(%d) bytes] Received: %s" % (len(data), str(map(ord, data))))

    def sendMessage(self, deviceToken, payload, identifier = None, expiry = None):
        msg = utils.formatMessage(deviceToken, payload, identifier, expiry)
        self.transport.write(msg)
        logging.debug("Sent Message: %s" % str(map(ord, msg)))

class APNSFactory(ReconnectingClientFactory):
    def __init__(self):
        self.currProtocol = None
        self.messageQueue = Queue.Queue()

    def closeConnection(self):
        if self.currProtocol:
            self.currProtocol.closeConnection()
            self.currProtocol = null;

    def clientConnectionLost(self, connector, reason):
        logging.info("Lost connection, Reason: " + str(reason))
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        #self.currProtocol = None
        #super(APNSFactory, self).clientConnectionLost(connector, reason)

    def clientConnectionFailed(self, connector, reason):
        logging.info("Connection Failed, Reason: " + str(reason))
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
        #self.currProtocol = None
        #super(APNSFactory, self).clientConnectionFailed(connector, reason)

    def startedConnecting(self, connector):
        logging.info("Started connecting to APNS connector....")

    def buildProtocol(self, addr):
        logging.info("Building APNS Protocol to APNS Server %s:%u..." % (addr.host, addr.port))
        if not self.currProtocol:
            self.currProtocol = APNSProtocol(self.messageQueue)
        else:
            logging.warning("Protocol already exists, returning existing protocol...")
        return self.currProtocol

    def getProtocol(self):
        """ Get the current protocol. """
        return self.currProtocol

    def sendMessage(self, deviceToken, payload, identifier = None, expiry = None):
        if self.currProtocol:
            self.currProtocol.sendMessage(deviceToken, payload, identifier, expiry)
        else:
            # queue it so when the protocol is built we can dispatch the
            # message
            logging.warning("Protocol not yet created.  Messaged queued...")
            self.messageQueue.put((deviceToken, payload, identifier, expiry))

class APNSDaemon(threading.Thread):
    """ 
    Maintains a list of connections to the main APNS server.
    """

    def __init__(self, reactor):
        """
        Initialises the daemon, with its reactor and the connection queue.
        """
        self.reactor        = reactor
        self.connections    = {}

    def unregisterApp(self, app_name):
        """
        Unregisters an app from the list of apps.
        """
        if app_name not in self.connections:
            return

        conn = self.connections[app_name]
        del self.connections[app_name]
        conn['client_factory'].closeConnection()

    def registerApp(self, app_name, certificate_file, privatekey_file,
                    apns_host       = constants.DEFAULT_APNS_DEV_HOST,
                    apns_port       = constants.DEFAULT_APNS_DEV_PORT,
                    feedback_host   = constants.DEFAULT_FEEDBACK_DEV_HOST,
                    feedback_port   = constants.DEFAULT_FEEDBACK_DEV_PORT):
        """
        Initialises a new app's connection with the APNS server so when
        time comes for requests it can be used.
        """

        if app_name in self.connections:
            raise errors.AppRegistrationError(app_name, "Application already registered")

        if certificate_file:
            certificate_file = os.path.abspath(certificate_file)

        if privatekey_file:
            privatekey_file = os.path.abspath(privatekey_file)

        logging.info("Registering Application: %s..." % (app_name))
        from twisted.internet.ssl import DefaultOpenSSLContextFactory as SSLContextFactory
        from OpenSSL import SSL
        self.connections[app_name] = {
            'num_connections':          0,
            'apns_host':                apns_host,
            'apns_port':                apns_port,
            'feedback_host':            feedback_host,
            'feedback_port':            feedback_port,
            'certificate_file':         certificate_file,
            'privatekey_file':          privatekey_file,
            'client_factory':           APNSFactory(),
            'client_context_factory':   SSLContextFactory(privatekey_file,
                                                          certificate_file)
                                                          # ,SSL.SSLv3_METHOD)
        }

    def sendMessage(self, app, device_token, payload, identifier = None, expiry = None):
        """ 
        Sends a message/payload from a given app to a target device.
        """
        if app not in self.connections:
            raise errors.AppRegistrationError(app, "Application not registered")
        
        if len(payload) > constants.MAX_PAYLOAD_LENGTH:
            raise errors.PayloadLengthError()

        connection  = self.connections[app]
        factory     = connection['client_factory']
        if connection['num_connections'] == 0:
            logging.info("Connecting to APNS Server, App: %s" % app)
            context_factory = connection['client_context_factory']
            self.reactor.connectSSL(connection['apns_host'],
                                    connection['apns_port'],
                                    factory, context_factory)
            connection['num_connections'] = connection['num_connections'] + 1

        factory.sendMessage(device_token, payload, identifier, expiry)

    def run(self):
        # start the reactor
        # note we are not connecting to APN server here.  We will do this
        # the first time a notification needs to be sent.  But instead we
        # listen to connection on the local network as we are the
        # standalone daemon.  
        logging.info("APNS Daemon Started...")
        self.reactor.run()

