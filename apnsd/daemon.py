
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

import threading, Queue, optparse, os, logging, copy
from twisted.internet.protocol import ReconnectingClientFactory, ClientFactory, Protocol, ClientCreator
from twisted.internet.ssl import DefaultOpenSSLContextFactory as SSLContextFactory
import constants, errors, utils

####################################################################################################
##                                      APNS Connectivity
####################################################################################################

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
        self.feedback_services = {}
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
            factory[app_name].closeConnection()
            del factory[app_name]

        if app_name in self.feedback_services:
            del self.feedback_services[app_name]


    def registerApp(self, app_name, app_mode, app_factory, feedbackService):
        """
        Initialises a new app's connection with the APNS server so when
        time comes for requests it can be used.
        """
        real_app_name = APNSDaemon._getRealAppName(app_mode, app_name)

        if real_app_name in self.conn_factories:
            raise errors.AppRegistrationError(real_app_name, "Application already registered for APNS")

        logging.info("Registering Application for APNS: %s..."%real_app_name)
        self.conn_factories[real_app_name] = app_factory

        if feedbackService:
            if real_app_name in self.feedback_services:
                raise errors.AppRegistrationError(real_app_name, "Application already registered for feedback service")

            logging.info("Registering Application for feedback service: %s..." % (real_app_name))
            self.feedback_services[real_app_name] = feedbackService




    def dataReceived(self, data, app_name, app_mode, *args, **kwargs):
        # tell all listeners that data was received for an app
        logging.debug("%s:%s -> Sending response to listeners..." % (app_mode, app_name))
        for listener in self.listeners.values():
            listener.dataAvailableForClient(data, app_name, app_mode)

    @staticmethod
    def _getRealAppName(app_mode, app_name):
        return app_mode + ":" + app_name

    def sendMessage(self, app_name, app_mode, device_token, payload, identifier = None, expiry = None):
        """
        Sends a message/payload from a given app to a target device.
        """
        real_app_name = APNSDaemon._getRealAppName(app_mode, app_name)
        if real_app_name not in self.conn_factories:
            raise errors.AppRegistrationError(app_name, "Application not registered for APNS")

        if len(payload) > constants.MAX_PAYLOAD_LENGTH:
            raise errors.PayloadLengthError()

        self.conn_factories[real_app_name].sendMessage(device_token, payload, identifier, expiry)

    def getFeedback(self, app_name, app_mode, deferred):
        """
        Retrieves feedback
        """
        real_app_name = APNSDaemon._getRealAppName(app_mode, app_name)
        if real_app_name not in self.feedback_services:
            raise errors.AppRegistrationError(app_name, "Application not registered for feedback")

        self.feedback_services[real_app_name].getFeedback(deferred)

    def run(self):
        # start the reactor
        # note we are not connecting to APN server here.  We will do this
        # the first time a notification needs to be sent.  But instead we
        # listen to connection on the local network as we are the
        # standalone daemon.
        logging.info("APNS Daemon Started...")
        self.reactor.run()

class APNSFactory(ReconnectingClientFactory):
    def __init__(self, reactor, app_name, app_mode,
                 # NB 'connListener': currently this is the daemon
                 connListener = None,
                 connListenerArgs = [],
                 connListenerKWArgs = {},
                 **kwargs):

        self.initialDelay = kwargs.get("initialDelay", 3)
        self.factor = kwargs.get("factor", 1)
        self.jitter = kwargs.get("jitter", .10)
        self.currProtocol = None
        self.messageQueue = Queue.Queue()
        self.reactor = reactor
        self.app_name = app_name
        self.app_mode = app_mode
        self.connListener = connListener
        self.connListenerArgs = connListenerArgs
        self.connListenerKWArgs = connListenerKWArgs

        self.app_id = kwargs["app_id"]
        self.apns_host = kwargs.get("apns_host")
        self.apns_port = kwargs.get("apns_port")
        # see if we need defaults
        self.apns_host = self.apns_host or    \
                        (self.app_mode == "apns_dev" and constants.DEFAULT_APNS_DEV_HOST) or  \
                        (self.app_mode == "apns_prod" and constants.DEFAULT_APNS_PROD_HOST)
        self.apns_port = self.apns_port or    \
                    (self.app_mode == "apns_dev" and constants.DEFAULT_APNS_DEV_PORT) or  \
                    (self.app_mode == "apns_prod" and constants.DEFAULT_APNS_PROD_PORT)

        self.certificate_file = utils.resolve_env_vars(kwargs["certificate_file"])
        self.privatekey_file = utils.resolve_env_vars(kwargs["privatekey_file"])
        logging.info("Certificate File: %s" % self.certificate_file)
        logging.info("PrivateKey File: %s" % self.privatekey_file)
        self.client_context_factory = SSLContextFactory(self.privatekey_file, self.certificate_file)

        logging.info("Connecting to APNS Server, App: %s:%s" % (self.app_mode, self.app_id))
        self.reactor.connectSSL(self.apns_host, self.apns_port, self, self.client_context_factory)

    def __str__(self):
        return "%s - %s - %s" % (self.app_mode, self.app_name, super(APNSFactory, self).__str__())

    def closeConnection(self):
        if self.currProtocol:
            self.currProtocol.closeConnection()
            self.currProtocol = null;

    def clientConnectionLost(self, connector, reason):
        logging.info("%s:%s -> Lost connection, Reason: %s" % (self.app_mode, self.app_id, str(reason)))
        self.currProtocol = None
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        logging.info("%s:%s -> Connection Failed, Reason: %s" % (self.app_mode, self.app_id, str(reason)))
        self.currProtocol = None
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def startedConnecting(self, connector):
        logging.info("%s:%s -> Started connecting to APNS connector..." % (self.app_mode, self.app_id))
        self.resetDelay()

    def buildProtocol(self, addr):
        logging.info("%s:%s -> Building APNS Protocol to APNS Server %s:%u..." %
                                (self.app_mode, self.app_id, addr.host, addr.port))
        if not (self.currProtocol and self.currProtocol.connected):
            self.currProtocol = APNSProtocol(self.app_id, self.app_mode,
                                             self.messageQueue,
                                             self.connListener,
                                             self.connListenerArgs,
                                             self.connListenerKWArgs)
        else:
            logging.info("%s:%s -> Protocol already exists, returning existing protocol..." %
                                                                (self.app_mode, self.app_id))
        return self.currProtocol

    def sendMessage(self, deviceToken, payload, identifier = None, expiry = None):
        if self.currProtocol and self.currProtocol.connected:
            self.currProtocol.sendMessage(deviceToken, payload, identifier, expiry)
        else:
            # queue it so when the protocol is built we can dispatch the
            # message
            logging.warning("%s:%s -> Protocol not yet created.  Message queued..." %
                                    (self.app_mode, self.app_id))
            self.messageQueue.put((deviceToken, payload, identifier, expiry))

class APNSProtocol(Protocol):
    def __init__(self, app_id, app_mode,
                 messageQueue, connListener, connListenerArgs = [], connListenerKWArgs = {}):
        """ Initialises the protocol with the message queue. """
        self.app_id = app_id
        self.app_mode = app_mode
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
        logging.info("%s:%s -> Connection to APNS Lost: %s" % (self.app_mode, self.app_id, str(reason)))

    def dataReceived(self, data):
        """
        Called when server has sent us some data.  For now we just
        print out the data.
        """
        logging.debug("%s:%s -> APNS Data [(%d) bytes] Received: %s" %
                    (self.app_mode, self.app_id, len(data), str(map(ord, data))))
        if self.connListener:
            self.connListener.dataReceived(data, self.app_id, self.app_mode,
                                           *self.connListenerArgs, **self.connListenerKWArgs)

    def sendMessage(self, deviceToken, payload, identifier = None, expiry = None):
        msg = utils.formatMessage(deviceToken, payload, identifier, expiry)
        self.transport.write(msg)
        logging.debug("%s:%s -> Sent Message: %s" % (self.app_mode, self.app_id, str(map(ord, msg))))

class FeedbackProtocol(Protocol):

    data = ''

    def __init__(self, deferredResult):
        self.deferredResult = deferredResult

    def dataReceived(self, data):
        """
        Called when server has sent us some data.  For now we just
        print out the data.
        """
        logging.debug("Feedback Data [(%d) bytes] Received"%(len(data)))
        self.data += data

    def connectionLost(self, reason):
        buff = copy.deepcopy(self.data)
        items = utils.getFeedbackItems(buff)
        self.deferredResult.callback(items)
        self.deferredResult = None


class FeedbackApplication:

    def __init__(self, reactor, app_name, app_mode, **kwargs):
        self.reactor = reactor
        self.app_name = app_name
        self.app_mode = app_mode
        self.app_id = kwargs["app_id"]
        self.feedback_host = kwargs.get("feedback_host")
        self.feedback_port = kwargs.get("feedback_port")

        # see if we need defaults
        self.feedback_host = self.feedback_host or    \
                            (self.app_mode == "apns_dev" and constants.DEFAULT_FEEDBACK_DEV_HOST) or  \
                            (self.app_mode == "apns_prod" and constants.DEFAULT_FEEDBACK_PROD_HOST)
        self.feedback_port = self.feedback_port or    \
                            (self.app_mode == "apns_dev" and constants.DEFAULT_FEEDBACK_DEV_PORT) or  \
                            (self.app_mode == "apns_prod" and constants.DEFAULT_FEEDBACK_PROD_PORT)

        self.certificate_file = utils.resolve_env_vars(kwargs["certificate_file"])
        self.privatekey_file = utils.resolve_env_vars(kwargs["privatekey_file"])
        self.client_context_factory = SSLContextFactory(self.privatekey_file, self.certificate_file)

    def getFeedback(self, deferred):
        logging.info("Connecting to Feedback Server, App: %s:%s" % (self.app_mode, self.app_id))
        cc = ClientCreator(self.reactor, FeedbackProtocol, deferred)
        # SRI: not sure what the client_context_factory is for.. is it ok to reuse like this?
        cc.connectSSL(self.feedback_host, self.feedback_port, self.client_context_factory)


####################################################################################################
##                                      C2DM Connectivity
####################################################################################################
from   twisted.web._newclient       import HTTP11ClientProtocol
from   twisted.web._newclient       import Request
from   twisted.web.client           import _parse

class C2DMFactory(ReconnectingClientFactory):
    def __init__(self, reactor, app_name, app_mode,
                 connListener = None,
                 connListenerArgs = [],
                 connListenerKWArgs = {},
                 **kwargs):
        self.initialDelay = kwargs.get("initialDelay", 3)
        self.factor = kwargs.get("factor", 1)
        self.jitter = kwargs.get("jitter", .10)
        self.currProtocol = None
        self.messageQueue = Queue.Queue()
        self.reactor = reactor
        self.app_name = app_name
        self.app_mode = app_mode
        self.connListener = connListener
        self.connListenerArgs = connListenerArgs
        self.connListenerKWArgs = connListenerKWArgs

        self.email = kwargs["email"]
        self.password = kwargs["password"]
        self.login_host = kwargs.get("login_host")
        # see if we need defaults
        self.login_url = self.login_host or constants.DEFAULT_C2DM_LOGIN_URL

        # self.client_context_factory = SSLContextFactory(self.privatekey_file, self.certificate_file)
        logging.info("Connecting to C2DM Server, App: %s:%s" % (self.app_mode, self.email))
        # self.reactor.connectSSL(self.apns_host, self.apns_port, self, self.client_context_factory)

    def closeConnection(self):
        if self.currProtocol:
            self.currProtocol.closeConnection()
            self.currProtocol = null;

    def clientConnectionLost(self, connector, reason):
        logging.info("%s:%s -> Lost connection, Reason: %s" % (self.app_mode, self.email, str(reason)))
        self.currProtocol = None
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        logging.info("%s:%s -> Connection Failed, Reason: %s" % (self.app_mode, self.email, str(reason)))
        self.currProtocol = None
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def startedConnecting(self, connector):
        logging.info("%s:%s -> Started connecting to C2DM connector..." % (self.app_mode, self.email))
        self.resetDelay()

    def buildProtocol(self, addr):
        logging.info("%s:%s -> Building C2DM Protocol to C2DM Server %s:%u..." %
                                (self.app_mode, self.email, addr.host, addr.port))
        if not (self.currProtocol and self.currProtocol.connected):
            self.currProtocol = C2DMProtocol(self.email, self.password, self.login_url,
                                             self.app_mode,
                                             self.messageQueue,
                                             self.connListener,
                                             self.connListenerArgs,
                                             self.connListenerKWArgs)
        else:
            logging.info("%s:%s -> Protocol already exists, returning existing protocol..." %
                                                                (self.app_mode, self.email))
        return self.currProtocol

    def sendMessage(self, deviceToken, payload, identifier = None, expiry = None):
        if self.currProtocol and self.currProtocol.connected:
            self.currProtocol.sendMessage(deviceToken, payload, identifier, expiry)
        else:
            # queue it so when the protocol is built we can dispatch the
            # message
            logging.warning("%s:%s -> Protocol not yet created.  Message queued..." %
                                    (self.app_mode, self.email))
            self.messageQueue.put((deviceToken, payload, identifier, expiry))

class C2DMProtocol(Protocol):
    def __init__(self, email, password, login_url, app_mode,
                 messageQueue, connListener, connListenerArgs = [], connListenerKWArgs = {}):
        """ Initialises the protocol with the message queue. """
        self.email = email
        self.password = password
        self.login_url = login_url
        self.app_mode = app_mode
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
        logging.info("%s:%s -> Connection to C2DM Lost: %s" % (self.app_mode, self.email, str(reason)))

    def dataReceived(self, data):
        """
        Called when server has sent us some data.  For now we just
        print out the data.
        """
        logging.debug("%s:%s -> C2DM Data [(%d) bytes] Received: %s" %
                    (self.app_mode, self.email, len(data), str(map(ord, data))))
        if self.connListener:
            self.connListener.dataReceived(data, self.email, self.app_mode,
                                           *self.connListenerArgs, **self.connListenerKWArgs)

    def sendMessage(self, deviceToken, payload, identifier = None, expiry = None):
        msg = utils.formatMessage(deviceToken, payload, identifier, expiry)
        self.transport.write(msg)
        logging.debug("%s:%s -> Sent Message: %s" % (self.app_mode, self.email, str(map(ord, msg))))

