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

from twisted.web import server, resource
from twisted.web import error as twerror

# to do errors do this:
# page = error.NoResource(message  "Resource %s not found" % request.URLPath())
# return page.render(request)

def ensure_request_authenticated(auth_function):
    """
    A decorator that ensures that the requests handled by render and
    render_METHOD methods in a resource handler are authenticated.
    We usually do this to check that all requests have some auth headers
    set.
    """
    def ensure_request_authenticated_decorator(func):
        def ensure_request_authenticated_method(resource, request):
            if auth_function and not auth_function(resource, request):
                return "Not Authenticated Error"
            else:
                return func(resource, request)
        return ensure_request_authenticated_method
    return ensure_request_authenticated_decorator
