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

import errors

def ensure_request_authenticated(auth_function, **auth_kwargs):
    """
    A decorator that ensures that the requests handled by render and
    render_METHOD methods in a resource handler are authenticated.
    We usually do this to check that all requests have some auth headers
    set.
    """
    def ensure_request_authenticated_decorator(func):
        def ensure_request_authenticated_method(resource, request):
            if auth_function and not auth_function(resource, request, **auth_kwargs):
                return errors.auth_required_error(request)
            else:
                return func(resource, request)
        return ensure_request_authenticated_method
    return ensure_request_authenticated_decorator

def require_parameters(*params):
    """
    A decorator to ensure that the request contains the given parameters.
    """
    def require_parameters_ecorator(func):
        def require_parameters_method(resource, request):
            for param in params:
                if param not in request.args:
                    return errors.param_missing_error(request, param)
            return func(resource, request)
        return require_parameters_method
    return require_parameters_ecorator
