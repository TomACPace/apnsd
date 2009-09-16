###############################################################################
#
# Copyright 2009, Sri Panyam
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

from twisted.web import error as twerror
import errors
import simplejson

def api_result(code, value):
    """
    Encodes a code and value in json dict.
    """
    return {'code': code, 'value': value}

def json_response(request, code, value, status = 200):
    """
    Returns an application/json content with the code and value.
    """
    result = api_result(code, value)
    request.setResponseCode(status)
    request.setHeader("Content-type", "text/html")
    # request.setHeader("Content-type", "application/json")
    return json_encode(result)

class OurJsonEncoder(simplejson.JSONEncoder):
    def default(self, o):
        if type(o) is datetime.datetime:
            return str(o)
        return super(OurJsonEncoder, self).default(o)

def json_encode(data):
    return OurJsonEncoder().encode(data)

def json_decode(data):
    if data:
        from simplejson.decoder import JSONDecoder as jdec
        return jdec().decode(data)
    else:
        return None

def get_reqvar(request, param, defaultval = None):
    """
    Returns a GET parameter in a request.
    If the parameter was not found then the defaultval is returned.
    """
    if param in request.args:
        return request.args[param][0]
    return defaultval

