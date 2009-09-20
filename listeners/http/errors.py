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

import json

PARAMETER_MISSING           = -1
PASSWORD_INVALID            = -2
PASSWORD_INCORRECT          = -3
USERNAME_INVALID            = -4
USER_ALREADY_EXISTS         = -5
USER_DOES_NOT_EXIST         = -6
APP_ALREADY_EXISTS          = -7
APP_DOES_NOT_EXIST          = -8
OS_ERROR                    = -9
IO_ERROR                    = -10
PKCS12_ERROR                = -11

ERROR_STRINGS   = [
    "",
    "Parameter missing",
    "Invalid password",
    "incorrect password",
    "Username invalid.",
    "User already exists.",
    "User does not exist.",
    "App already exists for user.",
    "App does not exist for user.",
    "OS Error",
    "IO Error",
    "PKCS12 Error",
]

def json_error_page(request, error_code, result = None, status = 200):
    if not result:
        result = ERROR_STRINGS[-error_code]
    return json.json_response(request, error_code, result, status)

def no_resource_error(request, status = 501):
    """
    Returns a 404 No Resource error for a request.
    """
    request.setResponseCode(401)
    request.setHeader("content-type", "text/html")
    return (""" <html><title>No Such Resource</title><body><h1>No Such Resource</h1><p>Resource Not Found: %s.</p></body></html>""" % request.URLPath())

def auth_required_error(request):
    """
    Returns an auth-required page for requires that need but fail
    authentication.
    """
    request.setResponseCode(401)
    request.setHeader("content-type", "text/html")
    return ("""
    <html><title>Unauthenticated</title><body><h1>Unauthenticated</h1><p>Please
    authenticate yourself.</p></body></html>""")

def param_missing_error(request, param, status = 501):
    """
    An error indicating missing parameters.
    """
    return json_error_page(request, PARAMETER_MISSING, param, status)

