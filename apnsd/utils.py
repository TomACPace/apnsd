
import struct, os, sys, re, constants, binascii, logging
import feedback

# Notification Message Format 1:
# <1 byte command> <2 bytes token length> <token> <2 bytes payload length> <payload>
CMD_FORMAT_0    =   "!h32sh%ds"

# Notification Message Format 2:
# <1 byte command> <identifier> <expiry> 
# <2 bytes token length> <token>
# <2 bytes payload length> <payload>
CMD_FORMAT_1    =   "!IIh32sh%ds"

# APNS feedback format
# <4 byte timestamp>
# <2 byte length field>
# <32 byte device token>
# timestamp & length are unsigned
APNS_FEEDBACK_FORMAT = "!LH%ds"%(constants.APNS_DEVICE_TOKEN_LENGTH)

def formatMessage(deviceToken, payload, identifier = None, expiry = None):
    if len(deviceToken) == 64:
        # decode it then
        deviceToken = binascii.unhexlify(deviceToken)

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


def getFeedbackItems(buff):
    toReturn = []
    remainder = buff
    while len(remainder) >= constants.APNS_TOTAL_FEEDBACK_LENGTH:
        timestamp, tokenLength, token = struct.unpack_from(APNS_FEEDBACK_FORMAT, remainder, 0)
        token = binascii.hexlify(token)
        logging.debug("Found feedback item [%s:%s:%s]"%(str(timestamp), str(tokenLength), str(token)))
        toReturn.append(feedback.APNSFeedback(timestamp, tokenLength, token))
        remainder = remainder[constants.APNS_TOTAL_FEEDBACK_LENGTH:]

    if len(remainder):
        logging.warning("Discarding remnant data in getting feedback items (len: %d), data was:%s:"%(len(remainder), str(remainder)))

    return toReturn
