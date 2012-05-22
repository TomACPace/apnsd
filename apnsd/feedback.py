###############################################################################
#
# Copyright 2012, Sri Panyam
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################

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

        
            
            

        

    
