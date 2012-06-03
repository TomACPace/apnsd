
from twisted.application.service import ServiceMaker

APNSD_Plugin = ServiceMaker(
    "APNS Daemon",
    "apnsd.tap",
    """A daemon for relaying requests to the Apple Push Notification Server in a simple and easy way.""",
    "apnsd"
)

