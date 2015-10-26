# Design #

The apns-daemon is a dedicated server that connects to the Apple Push Notification Service (APNS) on demand and forwards notification messages from multiple (registered) applications to the iphones.

The traditional way of achieving this is for each application provider to directly liaise with the APNS network in sending the notifications to the APP as shown below:

<img src='http://apns-daemon.googlecode.com/hg/docs/images/apns.jpg' />

The disadvantage of the traditional method is that each application would have to develop and maintain its own framework for communicating with APNS.  An application should not have to deal with this if it does not have to!

apns-daemon acts as a central component for multiple apps for communicating with the APNS  hiding all the plumbing details of the raw binary interface as shown below:

<img width='500' src='http://apns-daemon.googlecode.com/hg/docs/images/apns2.png' />

Not only does apns-daemon eliminate the need to develop custom APNS communication libraries, it also makes it easy for applications to structure their messages.  As shown below, the applications can communicate with apns-daemon in a variety of client protocols.  For instance App A uses a plain line protocol (described later on), while Apps B and C use http and https to send the messages to APNS respectively.  So far only the line protocol has been provided but http and https support will soon be added for use in managed and secure environments (appengine for instance).

Please refer to the Application Usage section in the [Configuration](Configuration.md) page for details on how to use the clients.