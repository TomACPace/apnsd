
import struct, os, sys, re

# Notification Message Format 1:
# <1 byte command> <2 bytes token length> <token> <2 bytes payload length> <payload>
CMD_FORMAT_0    =   "!h32sh%ds"

# Notification Message Format 2:
# <1 byte command> <identifier> <expiry> 
# <2 bytes token length> <token>
# <2 bytes payload length> <payload>
CMD_FORMAT_1    =   "!IIh32sh%ds"

def formatMessage(deviceToken, payload, identifier = None, expiry = None):
    if len(deviceToken) == 64:
        # decode it then
        deviceToken = "".join([ chr(int(deviceToken[2*i] + deviceToken[1 + 2*i], 16)) 
                                                                for i in xrange(0, 32) ])
    tokenLength = len(deviceToken)

    payload_length = len(payload)
    if identifier is None:
        fmt = CMD_FORMAT_0 % payload_length
        return '\x00' + struct.pack(fmt, tokenLength, deviceToken, payload_length, payload)
    else:
        fmt = CMD_FORMAT_1 % payload_length
        return '\x01' + struct.pack(fmt, long(identifier), long(expiry), tokenLength, deviceToken, payload_length, payload)

def resolve_env_vars(input):
    """
    Resolves any environment variables in a given input string.
    """
    return os.path.expandvars(input)

