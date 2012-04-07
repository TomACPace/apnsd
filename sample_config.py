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

{
    'listeners': {
        'line': {
            'class': 'apnsd.listeners.line.LineProtocolFactory',
            'interface': "localhost",  #default: all interface
            'port': 9999,
        },
        'http': {
            'class': 'apnsd.listeners.http.site.APNSSite',
            'interface': "localhost",  #default: all interface
            'secure': False,
            'port': 99,

            # where is the tyrant server running?
            # why do we need a tyrant server?  the http interface allows
            # one to register users and apps dynamically at runtime
            'tyrant_host': "localhost",     #   default - localhost
            'tyrant_port': 1978,            #   default - 1978
            'cert_folder': "/tmp/apnsd.certificates",
        },
    },

    'apps': {
        'AppName1': {
            'apns_dev': {
                'app_class':        "apnsd.daemon.APNSFactory",
                'app_id':           "App1 ID",
                'certificate_file': "path_to_dev_certificate_file_1.pem",
                'privatekey_file':  "path_to_dev_privatekey_file_1.pem"
            },
            'apns_rel': {
                'app_class':        "apnsd.daemon.APNSFactory",
                'app_id':           "App1 ID",
                'certificate_file': "path_to_release_certificate_file_1.pem",
                'privatekey_file':  "path_to_release_privatekey_file_1.pem"
            },
            # Optional
            # 'c2dm': {
            #    'app_class':        'apnsd.daemon.C2DMFactory',
            #    'email':            "your gmail id for sending C2DM messages as",
            #    'password':         "your gmail password for sending C2DM messages as",
            #}
        },
    }
}

