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

from twisted.application import service
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

        print "=" * 80
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
            
        import configs
        configs.read_listeners_in_config(options.configfile, self.apns_daemon, self.application)
        configs.read_apps_in_config(options.configfile, self.apns_daemon)

def main():
    app = APNSApp()
    application = app.application
    application.apns_daemon.run()
    logging.info("Exiting APNSD...")

if __name__ == "__main__":
    main()

