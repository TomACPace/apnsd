# Introduction #

Add your content here.


# Details #

Initial thoughts:

  * Have a separate FBClient (analagous to LineClient) which allows application to receive feedback... ie: don't tie it in with LineClient
    * How would an 'end client' (eg: django instance) use a FBClient? Would it periodically create  FBClient, which then connects to the long running apnsd server, which then kicks off a request to the afs (apple feedback service) to receive streamed data?
  * Have separate Protocol/ProtocolFactory to receive feedback data
    * Like what you have.. can have a LineFBProtocol, HttpFBProtocol...
  * Need to do the reverse of constructing a message - given bytes, construct a python representation
    * Opposite to what you do in utils.py
  * Haven't read up about twisted & 'daemon' modes.. ie: what the role of the daemon is. Would the actual communication with the apple fb server go through to daemon onto the FBProtocol classes, or would you have separate daemons? Don't know enough about this yet

---

Thought:
From the documentation " to determine if the application on the device re-registered with your service since the moment the device token was recorded on the feedback service."

=> You should be storing a 'registration timestamp' in Django somewhere (I don't at the moment). Do you ?