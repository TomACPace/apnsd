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

"""
Support for creating a service which runs the APNS Daemon
"""

import os, sys, configs

from twisted.cred import checkers
from twisted.application import service, internet
from twisted.python import log, usage
from twisted.python.log import ILogObserver, FileLogObserver
from twisted.python.logfile import DailyLogFile
import constants, errors, daemon, logging, os

class Options(usage.Options):
    synopsis = "[apnsd options]"

    optParameters = [
        ["config", "c", None, "Config file to read application info from."],
        ["logfile", "l", None, "Path of the logfile"]
    ]

    longdesc = "Runs the APNS daemon as a twistd plugin."

    def __init__(self):
        usage.Options.__init__(self)
        self.service = service.MultiService()
        self['logfile'] = None
        self['loglevel'] = logging.DEBUG
        self['config'] = None

def makeService(config):
    if config['logfile']:
        use_twisted_logging = False
        if use_twisted_logging:
            logfile_base = os.path.basename(config['logfile'])
            logfile_parent = os.path.dirname(config['logfile'])
            logfile = DailyLogFile(logfile_base, logfile_parent)
            self.application.setComponent(ILogObserver, FileLogObserver(logfile).emit)
        else:
            # logging.basicConfig(level = logging.DEBUG)
            logging.basicConfig(filename = config['logfile'], level = config['loglevel'])
    else:
        logging.basicConfig(level = config['loglevel'])
    
    if not config['config']:
        logging.error("Please specify a config file with the -c option.")
        config.opt_help()


    # which reactor are we using?  does this change with the --poll
    # parameter?
    from twisted.internet import reactor
    logging.info("Reactor Type: " + str(reactor))
    apns_daemon = daemon.APNSDaemon(reactor)
    configs.read_listeners_in_config(config['config'], apns_daemon, config.service)
    configs.read_apps_in_config(config['config'], apns_daemon)
    return config.service

