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
import logging, struct, constants
import OpenSSL, OpenSSL.crypto
import pyrant, datetime, os, shutil, urllib2
from json import json_response, json_decode, json_encode, api_result

def get_user_key(username):
    return 'user$' + username

def get_app_key(username, appname):
    return "app$" + username + "$" + appname

def get_app_folder(username, appname):
    return "%s/%s" % (username.lower()[0], appname)

def get_app_cert_folder(username, appname):
    return "%s/%s/certs" % (username.lower()[0], appname)

def is_password_valid(password):
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
        self.apns_daemon    = daemon
        self.apps_resource  = APNSAdminAppsResource(daemon, **kwds)
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
        self.apns_daemon    = daemon
        self.cert_folder    = kwds.get("cert_folder")
        self.tyrant_host    = kwds.get("tyrant_host", "localhost")
        self.tyrant_port    = kwds.get("tyrant_port", 1978)
        self.tyrant         = pyrant.Tyrant(host = self.tyrant_host,
                                            port = self.tyrant_port)

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

        userkey     = get_user_key(username)
        if userkey in self.tyrant:
            return errors.json_error_page(request, errors.USER_ALREADY_EXISTS)
        
        if not is_password_valid(password):
            return errors.json_error_page(request, errors.PASSWORD_INVALID)

        self.tyrant[userkey] = json_encode({'username': username,
                                            'pwdreset': False,
                                            'password': password,
                                            'created': datetime.datetime.now()})

        return json_response(request, 0, "OK")

    @decos.require_parameters("username")
    def delete_user(self, request):
        username    = utils.get_reqvar(request, "username")

        userkey     = 'user_' + username
        if userkey not in self.tyrant:
            return errors.json_error_page(request, errors.USER_DOES_NOT_EXIST)

        del self.tyrant[userkey]

        return json_response(request, 0, "OK")
            
    @decos.require_parameters("username", "newpassword")
    def change_user_password(self, request):
        username    = utils.get_reqvar(request, "username")
        newpassword = utils.get_reqvar(request, "newpassword")

        userkey     = get_user_key(username)
        if userkey not in self.tyrant:
            return errors.json_error_page(request, errors.USER_DOES_NOT_EXIST)
        
        if not is_password_valid(newpassword):
            return errors.json_error_page(request, errors.PASSWORD_INVALID)

        userdata                = json_decode(self.tyrant[userkey])
        userdata['pwdreset']    = False
        userdata['password']    = newpassword
        self.tyrant[userkey]    = json_encode(userdata)

        return json_response(request, 0, "OK")

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
        self.apns_daemon    = daemon
        self.cert_folder    = kwds.get("cert_folder")
        self.tyrant_host    = kwds.get("tyrant_host", "localhost")
        self.tyrant_port    = kwds.get("tyrant_port", 1978)
        self.tyrant         = pyrant.Tyrant(host = self.tyrant_host,
                                            port = self.tyrant_port)

    def create_app_cert_folder(self, username, appname):
        certfolder = "%s/%s" % (self.cert_folder, get_app_cert_folder(username, appname))
        try:
            os.makedirs(os.path.abspath(certfolder))
        except OSError, e:
            if e.errno != 17: raise
        return certfolder

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
        elif command == 'certupload':
            return self.upload_app_certificate(request)

        return errors.no_resource_error(request)
    
    @decos.require_parameters("username", "appname")
    def create_new_app(self, request):
        """
        Creates a new app.
        """
        username    = utils.get_reqvar(request, "username")
        appname     = utils.get_reqvar(request, "appname")

        userkey     = get_user_key(username)
        if userkey not in self.tyrant:
            return errors.json_error_page(request, errors.USER_DOES_NOT_EXIST)
        
        appkey      = get_app_key(username, appname)
        if appkey in self.tyrant:
            return errors.json_error_page(request, errors.APP_ALREADY_EXISTS)

        self.tyrant[appkey] = json_encode({'username': username,
                                           'appname': appname,
                                           'dev_pkeyfile': "",
                                           'dev_certfile': "",
                                           'prod_pkeyfile': "",
                                           'prod_certfile': "",
                                           'dev_pkeypasswd': "",
                                           'dev_certpasswd': "",
                                           'prod_pkeypasswd': "",
                                           'prod_certpasswd': "",
                                           'created': datetime.datetime.now()})

        # create the folder for the app so we have 
        # certificates and other things in there
        # <cert_folder>/<alphabet>/<appkey>/
        try:
            self.create_app_cert_folder(username, appname)
        except OSError, e:
            return errors.json_error_page(request, errors.OS_ERROR, str(e))

        return json_response(request, 0, "OK")

    @decos.require_parameters("username", "appname")
    def delete_app(self, request):
        """
        Deletes an app.
        """
        username = utils.get_reqvar(request, "username")
        appname = utils.get_reqvar(request, "appname")
        
        appkey      = get_app_key(username, appname)
        if appkey not in self.tyrant:
            return errors.json_error_page(request, errors.APP_DOES_NOT_EXIST)

        del self.tyrant[appkey]

        try:
            shutil.rmtree(self.get_app_folder(username, appname))
        except OSError, e:
            pass

        return json_response(request, 0, "OK")

    @decos.require_parameters("username", "appname", "certtype", "certfile")
    def upload_app_certificate(self, request):
        """
        Uploads a dev or provisioning certificate for an app.
        """
        username    = utils.get_reqvar(request, "username")
        appname     = utils.get_reqvar(request, "appname")
        certtype    = utils.get_reqvar(request, "certtype")
        certfile    = utils.get_reqvar(request, "certfile")
        certpasswd  = urllib2.unquote(utils.get_reqvar(request, "certpasswd"))
        pkeypasswd  = urllib2.unquote(utils.get_reqvar(request, "pkeypasswd"))
        certcontlen = int(utils.get_reqvar(request, "certcontlen"))
        pkeycontlen = int(utils.get_reqvar(request, "pkeycontlen"))
        
        appkey      = get_app_key(username, appname)
        if appkey not in self.tyrant:
            return errors.json_error_page(request, errors.APP_DOES_NOT_EXIST)

        contlength  = request.getHeader("content-length")
        logging.debug("Headers: " + str(request.getAllHeaders()))
        content     = request.content.read()
        logging.debug("Encoded Contents: " + str(type(content)) + ", " + str(len(content)))
        content     = content.decode("zlib")
        logging.debug("Decoded Contents: " + str(type(content)) + ", " + str(len(content)))
        logging.debug("Passwords: %s, %s" % (certpasswd, pkeypasswd))

        # strip the certfile and the pkeyfile
        fmt = "%ds%ds" % (certcontlen, pkeycontlen)
        cert_contents, pkey_contents = struct.unpack(fmt, content)

        logging.debug("Cert Content Length: " + str(len(cert_contents)))
        logging.debug("Pkey Content Length: " + str(len(pkey_contents)))

        # so how should the files be saved?
        # for now our certfolder will be 
        cert_folder = self.create_app_cert_folder(username, appname)

        try:
            cert_pem_file = self.p12_to_pem(cert_contents, certpasswd,
                                "%s/%s_certificate" % (cert_folder, certtype), True)
            pkey_pem_file = self.p12_to_pem(pkey_contents, pkeypasswd, 
                                "%s/%s_privatekey" % (cert_folder, certtype), False)
        except IOError, e:
            return errors.json_error_page(request, errors.IO_ERROR, str(e))
        except OpenSSL.crypto.Error, e:
            logging.error("SSL Error: " + e.message)
            return errors.json_error_page(request, errors.PKCS12_ERROR, "Incorrect password")

        # save the updated passwords
        app                 = json_decode(self.tyrant[appkey])
        app['certpasswd']   = certpasswd
        app['pkeypasswd']   = pkeypasswd
        self.tyrant[appkey] = json_encode(app)

        # finally unregister the app and register it again with the new
        # certificates
        if certtype == "production":
            self.apns_daemon.unregisterApp("prod_" + appkey)
            self.apns_daemon.registerApp("prod_" + appkey, cert_pem_file, pkey_pem_file,
                                         constants.DEFAULT_APNS_PROD_HOST,
                                         constants.DEFAULT_APNS_PROD_PORT,
                                         constants.DEFAULT_FEEDBACK_PROD_HOST,
                                         constants.DEFAULT_FEEDBACK_PROD_PORT)
        else:
            self.apns_daemon.unregisterApp("dev_" + appkey)
            self.apns_daemon.registerApp("dev_" + appkey, cert_pem_file, pkey_pem_file)

        return json_response(request, 0, "OK")

    def p12_to_pem(self, contents, password = "", outfilename = "output",
                   doingCertificate = True, save_p12_to_file = False):
        """
        Saves p12 data into pem files.
        Whether the p12 represents certificate data or private key data is
        specified in boolean parameter doingCertificate

        The filename (without the .pem) is specified in outfile.
        """

        if save_p12_to_file:
            # save the certificate .p12 file
            outfile = open("%s.p12" % outfilename, "w")
            outfile.write(contents)
            outfile.close()

        if doingCertificate:
            pkcs12_obj  = OpenSSL.crypto.load_pkcs12(contents, password)
            certif      = pkcs12_obj.get_certificate()
            out_obj     = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, certif)
        else:
            pkcs12_obj  = OpenSSL.crypto.load_pkcs12(contents, password)
            pkey        = pkcs12_obj.get_privatekey()
            out_obj     = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, pkey)

        logging.debug("Writing pem file: %s.pem, Size: %d" % (outfilename, len(out_obj)))
        outfile = open("%s.pem" % outfilename, "w")
        outfile.write(out_obj)
        outfile.close()

        # return the name of the output file
        return outfilename + ".pem"

