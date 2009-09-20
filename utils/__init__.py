

def formatMessage(deviceToken, payload):
    # notification messages are binary messages in network order 
    # using the following format: 
    # <1 byte command> <2 bytes length><token> <2 bytes length><payload>
    import struct
    fmt = "!h32sh%ds" % len(payload) 
    command     = 0
    if len(deviceToken) == 64:
        # decode it then
        deviceToken = "".join([ chr(int(deviceToken[2*i] + deviceToken[1 + 2*i], 16)) 
                                                                for i in xrange(0, 32) ])
    tokenLength = len(deviceToken)
    return '\x00' + struct.pack(fmt, tokenLength, deviceToken, len(payload), payload)
