#!/bin/env python2.5
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

def get_application():
    import os, sys
    # add the apnsd folder to the path so all other modules can be found by
    # twistd
    file_path = os.path.abspath(__file__)
    apnsd_folder = os.path.dirname(os.path.abspath(__file__ + "/../"))
    sys.path.append(apnsd_folder)
    from apnsd import app
    the_app = app.APNSApp()
    return the_app

application = get_application()

