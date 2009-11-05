#!/bin/env python2.5
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

from twisted.application import service, internet
from twisted.python import log
from twisted.python.log import ILogObserver, FileLogObserver
from twisted.python.logfile import DailyLogFile
import constants, errors, daemon, logging, os

class APNSApp(object):
    def __init__(self, reactor = None):
        self.application = service.Application("APNS Daemon")
        self.apns_daemon = daemon.APNSDaemon(reactor)
        self.parse_options()

    def parse_options(self):
        from optparse import OptionParser

        parser = OptionParser(version = "%prog 0.1")
        parser.add_option("-c", "--config", dest = "configfile",
                          help="Config file to read application info from.", metavar = "CONFIG-FILE")
        parser.add_option("-l", "--logfile", dest = "logfile",
                          help="Path of the logfile.", metavar = "LOG-FILE")

        (options, args) = parser.parse_args()

        if not options.configfile:
            parser.error("Please specify a valid config filename with the -c option")

        if options.logfile:
            use_twisted_logging = False
            if use_twisted_logging:
                logfile_base = os.path.basename(options.logfile)
                logfile_parent = os.path.dirname(options.logfile)
                logfile = DailyLogFile(logfile_base, logfile_parent)
                self.application.setComponent(ILogObserver, FileLogObserver(logfile).emit)
            else:
                # logging.basicConfig(level = logging.DEBUG)
                logging.basicConfig(filename = options.logfile, level = logging.DEBUG)
        else:
            logging.basicConfig(level = logging.DEBUG)
            
        self.read_config_file(options.configfile)

    def read_config_file(self, config_file):
        """
        Reads the config file and loads config data about all the apps we want
        to support.
        """
        import os
        if not os.path.isfile(config_file):
            raise errors.ConfigFileError(config_file, "File not found")

        configs = eval(open(config_file).read())
        if 'listeners' not in configs:
            raise errors.ConfigFileError(config_file, "'listeners' section not found")

        if 'apps' not in configs:
            raise errors.ConfigFileError(config_file, "'apps' section not found")

        listeners = configs['listeners']
        for listener_name in listeners:
            listener_data     = listeners[listener_name]
            listener_class    = listener_data['class']
            parts = listener_class.split(".")
            if len(parts) > 1:
                listener_pkg      = ".".join(parts[:-1])
                listener_module   = __import__(listener_pkg, {}, {}, [''])
                listener_class    = getattr(listener_module, parts[-1])
            else:
                listener_class    = eval(parts[-1])

            logging.debug("Creating listener: " + str(listener_class))
            log.msg("Creating listener: " + str(listener_class), logLevel = logging.DEBUG)
            listener = listener_class(self.apns_daemon, **listener_data)
            if listener_data.get("secure", False):
                server = internet.SSLServer(listener_data["port"], listener)
            else:
                server = internet.TCPServer(listener_data["port"], listener)
            server.setServiceParent(self.application)

            logging.debug("Listener Created: " + str(listener))
            logging.debug("----------------------------------")
            
        apps = configs['apps']
        for app_key in apps:
            app         = apps[app_key]
            app_id      = app['app_id']
            cert_file   = app['certificate_file']
            pkey_file   = app.get("privatekey_file", None)
            self.apns_daemon.registerApp(app_id, cert_file, pkey_file)

def main():
    app = APNSApp()
    application = app.application
    application.apns_daemon.run()
    logging.info("Exiting APNSD...")

if __name__ == "__main__":
    main()

