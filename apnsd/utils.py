
import struct

# Notification Message Format 1:
# <1 byte command> <2 bytes token length> <token> <2 bytes payload length> <payload>
CMD_FORMAT_0    =   "!h32dsh%ds"

# Notification Message Format 2:
# <1 byte command> <identifier> <expiry> 
# <2 bytes token length> <token>
# <2 bytes payload length> <payload>
CMD_FORMAT_1    =   "!hII32sh%ds"

def formatMessage(deviceToken, payload, identifier = None, expiry = None):
    if len(deviceToken) == 64:
        # decode it then
        deviceToken = "".join([ chr(int(deviceToken[2*i] + deviceToken[1 + 2*i], 16)) 
                                                                for i in xrange(0, 32) ])
    tokenLength = len(deviceToken)

    if identifier is None:
        fmt = CMD_FORMAT_0 % len(payload)
        return '\x00' + struct.pack(fmt, tokenLength, deviceToken, len(payload), payload)
    else:
        fmt = CMD_FORMAT_1 % len(payload)
        return '\x01' + struct.pack(fmt, identifier, expiry, tokenLength, deviceToken, len(payload), payload)

