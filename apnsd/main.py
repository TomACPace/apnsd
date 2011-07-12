#!/bin/env python
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

import os, sys

def main():
    parent_folder = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../")
    sys.path.append(parent_folder)
    print "Parent Folder: ", parent_folder

    # which reactor are we using?
    # change the type of reactor being used here
    import twisted
    import twisted.internet
    from twisted.internet import reactor

    import app
    application = app.APNSApp(reactor)
    application.apns_daemon.run()

if __name__ == "__main__":
    main()


