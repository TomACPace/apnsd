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
from twisted.internet.ssl import DefaultOpenSSLContextFactory as SSLContextFactory
import constants, errors, utils

class APNSDaemon(threading.Thread):
    """ 
    Maintains a list of connections to the Apple and also serves to
    maintain the credentials of each of the Apps registered in our list.
    """
    def __init__(self, reactor):
        """
        Initialises the daemon, with its reactor and the connection queue.
        """
        self.reactor = reactor
        self.conn_factories = {}
        self.listeners = {}

    def unregisterListener(self, listener_name):
        """
        DeRegisters a listener when it is no longer interested in being
        notified by the daemon on connection events, like connection
        closed, data received etc.
        """
        if listener_name in self.listeners:
            del self.listeners[listener_name]

    def registerListener(self, listener_name, listener):
        """
        Registers a listener when it is interested in being notified by the
        daemon on connection events, like connection closed, data received
        etc.
        """
        if listener_name in self.listeners:
            raise errors.ListenerRegistrationError(listener_name, "Listener already registered")

        self.listeners[listener_name] = listener

    def unregisterApp(self, app_name):
        """
        Unregisters an app from the list of apps.
        """
        if app_name in self.conn_factories:
            self.conn_factories[app_name].closeConnection()
            del self.conn_factories[app_name]

    def registerApp(self,
                    app_name, certificate_file, privatekey_file,
                    apns_host       = constants.DEFAULT_APNS_DEV_HOST,
                    apns_port       = constants.DEFAULT_APNS_DEV_PORT,
                    feedback_host   = constants.DEFAULT_FEEDBACK_DEV_HOST,
                    feedback_port   = constants.DEFAULT_FEEDBACK_DEV_PORT):
        """
        Initialises a new app's connection with the APNS server so when
        time comes for requests it can be used.
        """
        if app_name in self.conn_factories:
            raise errors.AppRegistrationError(app_name, "Application already registered")

        if certificate_file:
            certificate_file = os.path.abspath(certificate_file)

        if privatekey_file:
            privatekey_file = os.path.abspath(privatekey_file)

        logging.info("Registering Application: %s..." % (app_name))

        self.conn_factories[app_name] = APNSFactory(app_name, self.reactor,
                                                    apns_host, apns_port,
                                                    feedback_host, feedback_port,
                                                    certificate_file, privatekey_file,
                                                    self, app_name)

    def dataReceived(self, data, app_name, *args, **kwargs):
        # tell all listeners that data was received for an app
        for listener in self.listeners.values():
            listener.dataAvailableForClient(data, app_name)

    def sendMessage(self, app, device_token, payload, identifier = None, expiry = None):
        """ 
        Sends a message/payload from a given app to a target device.
        """
        if app not in self.conn_factories:
            raise errors.AppRegistrationError(app, "Application not registered")
        
        if len(payload) > constants.MAX_PAYLOAD_LENGTH:
            raise errors.PayloadLengthError()

        self.conn_factories[app].sendMessage(device_token, payload, identifier, expiry)

    def run(self):
        # start the reactor
        # note we are not connecting to APN server here.  We will do this
        # the first time a notification needs to be sent.  But instead we
        # listen to connection on the local network as we are the
        # standalone daemon.  
        logging.info("APNS Daemon Started...")
        self.reactor.run()

class APNSFactory(ReconnectingClientFactory):
    def __init__(self, app_name, reactor,
                 apns_host, apns_port,
                 feedback_host, feedback_port,
                 certificate_file, privatekey_file,
                 connListener = None,
                 connListenerArgs = [],
                 connListenerKWArgs = {}):
        self.initialDelay = 3
        self.factor = 1
        self.jitter = .10

        self.currProtocol = None
        self.messageQueue = Queue.Queue()

        self.app_name = app_name
        self.reactor = reactor
        self.apns_host = apns_host
        self.apns_port = apns_port
        self.feedback_host = feedback_host
        self.feedback_port = feedback_port
        self.certificate_file = certificate_file
        self.privatekey_file = privatekey_file
        self.client_context_factory = SSLContextFactory(privatekey_file, certificate_file)

        self.connListener = connListener
        self.connListenerArgs = connListenerArgs
        self.connListenerKWArgs = connListenerKWArgs

        logging.info("Connecting to APNS Server, App: %s" % app_name)
        self.reactor.connectSSL(self.apns_host, self.apns_port, self, self.client_context_factory)

    def closeConnection(self):
        if self.currProtocol:
            self.currProtocol.closeConnection()
            self.currProtocol = null;

    def clientConnectionLost(self, connector, reason):
        logging.info("Lost connection, Reason: " + str(reason))
        self.currProtocol = None
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        logging.info("Connection Failed, Reason: " + str(reason))
        self.currProtocol = None
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def startedConnecting(self, connector):
        logging.info("Started connecting to APNS connector....")
        self.resetDelay()

    def buildProtocol(self, addr):
        logging.info("Building APNS Protocol to APNS Server %s:%u..." % (addr.host, addr.port))
        if not (self.currProtocol and self.currProtocol.connected):
            self.currProtocol = APNSProtocol(self.messageQueue,
                                             self.connListener,
                                             self.connListenerArgs,
                                             self.connListenerKWArgs)
        else:
            logging.warning("Protocol already exists, returning existing protocol...")
        return self.currProtocol

    def sendMessage(self, deviceToken, payload, identifier = None, expiry = None):
        if self.currProtocol and self.currProtocol.connected:
            self.currProtocol.sendMessage(deviceToken, payload, identifier, expiry)
        else:
            # queue it so when the protocol is built we can dispatch the
            # message
            logging.warning("Protocol not yet created.  Messaged queued...")
            self.messageQueue.put((deviceToken, payload, identifier, expiry))

class APNSProtocol(Protocol):
    def __init__(self, messageQueue, connListener, connListenerArgs = [], connListenerKWArgs = {}):
        """ Initialises the protocol with the message queue. """
        self.messageQueue = messageQueue
        self.connListener = connListener
        self.connListenerArgs = connListenerArgs
        self.connListenerKWArgs = connListenerKWArgs

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

    def connectionLost(self, reason):
        logging.debug("Connection to APNS Lost.  Reason: " + str(reason))

    def dataReceived(self, data):
        """
        Called when server has sent us some data.  For now we just 
        print out the data.
        """
        logging.debug("APNS Data [(%d) bytes] Received: %s" % (len(data), str(map(ord, data))))
        if self.connListener:
            self.connListener.dataReceived(data, *self.connListenerArgs, **self.connListenerKWArgs)

    def sendMessage(self, deviceToken, payload, identifier = None, expiry = None):
        msg = utils.formatMessage(deviceToken, payload, identifier, expiry)
        self.transport.write(msg)
        logging.debug("Sent Message: %s" % str(map(ord, msg)))

