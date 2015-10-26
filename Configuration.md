# Configuration #

The apns-daemon is started with the command:

```
python main.py -c <configuration_file>
```

The configuration file, passed in to main.py via the -c flag, is mandatory.  A sample configuration file (sample\_config.py) is provided in the main project root.

This config file is a plain python text file with a single json struct as its data that contains two sections - "clients" and "apps", describing the client connectors and the registered applications respectively.  Please look at the [Design](Design.md) page for more information on clients.

The sample configuration file contains:

```
{
    'clients': {
        'line': {
            'class': 'clients.line.LineProtocolFactory',
            'port': 90
        },
        'http': {
            'class': 'clients.http.APNSSite',
            'port': 99
        },
    },

    'apps': {
        'app1': {
            'bundle_id':        "App1 BundleID",
            'certificate_file': "path_to_certificate_file_1.pem",
            'privatekey_file':  "path_to_privatekey_file_1.pem"
        },
        'app2': {
            'bundle_id':        "App2 BundleID",
            'certificate_file': "path_to_certificate_file_2.pem",
            'privatekey_file':  "path_to_privatekey_file_2.pem"
        },
    }
}
```

First, in the clients section, all the client classes that allow communication between the applications and the apns daemon are provided.  In this case only two clients are configured - A LineClient and a HttpClient (to allow access via a simple line protocol and http protocols respectively).

Note that the clients section refers to the server side (apns daemon side) configuration of communications objects and NOT the application side configuration.  So in the above example, the apns daemon starts two servers to listen to requests from applications - a line server on port 90 and a http server on port 99.

In the subsequent section, the applications that are allowed to communicate with the apns daemon are registered.  For each application, its bundle id, certificate file and private key file are required.  Note that in some instances the privatekey file and the certificate file can be within the same file.  Please refer to the <a href='http://developer.apple.com/library/ios/#documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/ProvisioningDevelopment/ProvisioningDevelopment.html#//apple_ref/doc/uid/TP40008194-CH104-SW1'>APNS Provisioning and Development</a> section in the APNS documentation for further details.

Note that only the applications registered in the apps section can send messages via the apns daemon to the APNS network.

## Application Usage ##
Once the apns daemon is running, applications can connect to the clients specified in the "clients" section of the configuration file.  Two of the client types are described below.

## Line Client ##
Applications talk to the apns-daemon via client protocols.  The most basic and lightweight client protocol is the line-protocol (clients.line.LineClient).  Using this apps would send messages to the apns-daemon using the following two steps:

1. Create the line client.  Once created, this instance can be used for ever (thanks to twisted's protocol factory magic).

```
from clients.line import LineClient
lineClient = LineClient()
```

Note that the line-client handler in the apns-daemon listens on port 90 by default.  However this can be changed in the configuration file.  In this case, the LineClient's port can be changed with a parameter to the constructor as:

```
from clients.line import LineClient
lineClient = LineClient(port_where_apns_line_server_is_running)
```

2. Send the message:
```
lineClient.sendMessage(app_name, device_token, payload)
```

All parameters are mandatory:
  * **app\_name**: The application provider sending the message.  This is mandatory as an apns-daemon instance can service multiple clients.
  * **device\_token**: The device\_token of the iPhone client device to which the payload/message is targeted.  Please read the iphone push notification documentation on how this is obtained by the phone.  However, when sent to the line client, this must be a 64 byte ascii representation of the real (32 byte) binary device token obtained by the client device (the iphone).
  * **payload**: The actual payload sent.  This must be a json dictionary with the "aps" parameter set as described in the APNS documentation.

As it can be seen the clients are the lowest possible objects that send raw data as is.  It is upto the application to format the object as a json-ified string as described in the APNS documentation.  This is a trivial matter and in the future a layer to simply this further (if necessary) will be added to wrap this layer.

## Http Client ##

As described above applications have freedom to choose how they communicate with the apns daemon.  In the situation where the daemon and the apps are running in the same server/environment, a line client would be safe, secure and the easiest way to access the daemon.

However there may be situations where applications are managed in environments where arbitrary ports cannot be opened due to security restrictions.  In these cases applications may have no choice but to use safer protocols such as http or https to send messages to APNS.

As of now the http client is under development.  However a mode of operation of the Http client is described below.

Messages are sent as POST requests to `<apns_host>/app_name/device_token/` with the payload in the POST body (assuming the apns daemon is running on apns\_host).

The app\_name and device\_token are identical as in the LineClient.  As with the line client the device\_token is a 64 byte ascii representation of the real (32 byte) binary device token obtained by the client device (the iphone).

There is however a simpler wrapper for this.  Like with the LineClient, the http client package comes with its own client wrapper.  Again this is a two step creation/usage process.

1. Create the client

```
from clients.http import Client
httpClient = Client(host, port)
```

This creates a client that will connect to a http server running within the apns daemon.  By default the host and port are "localhost" and "99".  However these can be customised.

2. Use the client.

Again as with the line client, the sendMessage method can be used to simplify matters as follows:

```
httpClient.sendMessage(app_name, device_token, payload)
```

One difference is that the payload here refers to a dictionary that is sent as is to the APNS instead of a stringified json as was the case with the LineClient.