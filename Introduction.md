# Introduction #

apns-daemon is a simple server that acts as a daemon for projects to send notifications to iphones via [Apple's Push Notification Service](http://developer.apple.com/IPhone/library/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/ApplePushService/ApplePushService.html) (APNS) network.

apns-daemon runs on top of twisted and openssl to manage connections to APNS transparently to third party apps running on top of it.

# Requirements #

  * [Python](http://python.org) 2.4 or higher; Tested with Python 2.5.4
  * [Twisted](http://twistedmatrix.com) Tested with version 8.2.0
  * [pyOpenSSL](https://launchpad.net/pyopenssl)


# Setup and Running #
At the moment there are no setup steps.  The daemon can be run (after unarchiving the tarball ofcourse) with the command:
```
python main.py -c <config_file>
```

The configuration file is mandatory and will be explained in [Configuration](Configuration.md).