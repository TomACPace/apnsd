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
import utils, auth, errors
import decorators as decos
from json import json_response


def is_password_valid(self, password):
    """
    tells if a password is valid or not by doing simple checks like
    checking for length, character types and so on.
    """
    return True

class APNSAdminResource(resource.Resource):
    """
    The admin resource handler.
    Requests to /admin/ will usually be made from the webserver that is
    acting as the frontend for the admin (eg gae).  The admin does things
    like manage app specific passwords and the app's provisioning
    certificates.
    Also the admin resource manages users in the system.
    """
    def __init__(self, daemon, **kwds):
        resource.Resource.__init__(self)
        self.apns_daemon = daemon
        self.apps_resource = APNSAdminAppsResource(daemon, **kwds)
        self.users_resource = APNSAdminUsersResource(daemon, **kwds)
        self.putChild("apps", self.apps_resource)
        self.putChild("users", self.users_resource)

class APNSAdminUsersResource(resource.Resource):
    """
    The users section within in the admin resource.
    Handles requests to the following /admin/users/ urls:
        1. /create/?username=<email/username>&passwd=<password>&otherparams
            Creates a new user with the username and password.  The
            username can be an email or other wise.
            Other noteworthy parameters can also be passed here. 
        2. /delete/?username=<email/username>
            Deleting an app by the given name.
        3. /passwd/
            Changes the password for a user.  The request MUST contain the
            old and the new passwords.  Also through out the http
            connector (and listener) we need uniform password schemes.
    """
    isLeaf = True
    def __init__(self, daemon, **kwds):
        resource.Resource.__init__(self)
        self.apns_daemon = daemon

    @decos.ensure_request_authenticated(auth.basic_auth, prefix="admin")
    def render(self, request):
        # get the components in the path
        # why 3 onwards? the resource does not split the co
        parts = request.path.split("/")[3:]
        if not parts:
            return errors.no_resource_error(request)
            
        command, parts = parts[0], parts[1:]
        if command == 'create':
            return self.create_new_user(request)
        elif command == 'delete':
            return self.delete_user(request)
        elif command == 'passwd':
            return self.change_user_password(request)
        else:
            return errors.no_resource_error(request)
            

    @decos.require_parameters("username", "password")
    def create_new_user(self, request):
        username    = utils.get_reqvar(request, "username")
        password    = utils.get_reqvar(request, "password")

    @decos.require_parameters("username")
    def delete_user(self, request):
        username    = utils.get_reqvar(request, "username")
            
    @decos.require_parameters("username", "newpassword")
    def change_user_password(self, request):
        username    = utils.get_reqvar(request, "username")
        newpassword = utils.get_reqvar(request, "newpassword")

class APNSAdminAppsResource(resource.Resource):
    """
    The apps section within in the admin resource.
    Handles requests to the following /admin/apps/ urls:
        1. /create/?appname=<appname>&user=<username>&passwd=passwd
            Creates a new app with the app name.
            The username (or email) and password are mandatory fields.
        2. /delete/?appname=<appname>&username=<username>
            Deleting an app by the given name belonging to a specific user.
        3.  /certupload/?certtype=<certtype>&username=<username>&appname=<appname>
            Uploads dev/provisioning certificate files for an app.
            The certificate file will be the POST data and the certificate
            type (eg "dev" or "prod") will be specified in the GET
            parameter.
        4. /passwd/?username=<username>&appname=<appname>
            Change the password.  When doing this both the old AND the new
            passwords must be provided.
    """
    isLeaf = True
    def __init__(self, daemon, **kwds):
        resource.Resource.__init__(self)
        self.apns_daemon = daemon

    def render(self, request):
        # get the components in the path
        # why 3 onwards? the resource does not split the co
        parts = request.path.split("/")[3:]
        if not parts:
            return errors.no_resource_error(request)
            
        command, parts = parts[0], parts[1:]
        if command == 'create':
            return self.create_new_app(request)
        elif command == 'delete':
            return self.delete_app(request)
        elif command == 'password':
            return self.change_app_password(request)
        elif command == 'certupload':
            return self.upload_app_certificate(request)
        else:
            return errors.no_resource_error(request)
    
    @decos.require_parameters("username", "appname")
    def create_new_app(self, request):
        """
        Creates a new app.
        """
        username    = utils.get_reqvar(request, "username")
        appname     = utils.get_reqvar(request, "appname")

    @decos.require_parameters("username", "appname")
    def delete_app(self, request):
        """
        Deletes an app.
        """
        username = utils.get_reqvar(request, "username")
        appname = utils.get_reqvar(request, "appname")

    @decos.require_parameters("username", "appname")
    def change_app_password(self, request):
        """
        Changes the app password.
        """
        username    = utils.get_reqvar(request, "username")
        appname     = utils.get_reqvar(request, "appname")

    @decos.require_parameters("username", "appname", "certfile", "certtype")
    def upload_app_certificate(self, request):
        """
        Uploads a dev or provisioning certificate for an app.
        """
        username    = utils.get_reqvar(request, "username")
        appname     = utils.get_reqvar(request, "appname")
        certfile    = utils.get_reqvar(request, "certfile")
        certtype    = utils.get_reqvar(request, "certtype")

