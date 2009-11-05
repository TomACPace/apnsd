
from zope.interface import implements
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet

from apnsd import 

class APNSDMaker(object):
    implements (IServiceMaker, IPlugin)
    tapname = "apnsd"
    description = "This is the plugin that runs the APNS Daemon in twistd mode"
