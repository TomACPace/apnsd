
class SerialisationException(Exception):

    def __init__(self, what):
        self.what = what

class APNSFeedback:

    END_MARKER = "END"

    def __init__(self, timestamp, length, token):
        self.timestamp = timestamp
        self.length = length
        self.token = token

    def toString(self):
        # token is ascii, so no commas will be in the data members
        return "%s,%s,%s"%(str(self.timestamp), str(self.length), str(self.token))

    @staticmethod
    def stringContainsEnd(theString):
        # NB: since 'N' is not a hex character, we don't expect to find it 
        # in the middle of the string
        return APNSFeedback.END_MARKER in theString


    @staticmethod
    def fromString(theString):
        elements = theString.split(",")
        if len(elements) != 3:
            raise SerialisationException("Provided APNSFeedback string incorrect format, provided; %s"%theString)

        ts, l, token = elements
        return APNSFeedback(ts, l, token)

    @staticmethod
    def listToString(theList):
        toReturn = ""
        for elt in theList:
            toReturn += elt.toString() + ":"

        toReturn += APNSFeedback.END_MARKER
        return toReturn

    @staticmethod
    def listFromString(theString):
        toReturn = []
        elts = theString.split(":")

        try:
            for elt in elts:

                if elt == APNSFeedback.END_MARKER:
                    break

                toReturn.append(APNSFeedback.fromString(elt))
            else:
                logging.error("Error in deserialising string %s, no end marker (%s) found. Returning results that were found..."%(theString, APNSFeedback.END_MARKER))

        except SerialisationException, e:
            logging.error("Error in deserialising string, problem was: %s. Returning results that were found.."%e.what)

        return toReturn

        
            
            

        

    
