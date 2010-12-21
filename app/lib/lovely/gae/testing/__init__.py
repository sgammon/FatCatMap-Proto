##############################################################################
#
# Copyright 2009 Lovely Systems AG
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
##############################################################################

import os

class DBLayer(object):

    __bases__ = ()

    def __init__(self, name, appid='lovely-gae-testing',
                 appserver_args={}):
        self.__name__ = name
        self.appid = appid
        self.appserver_args = appserver_args

    def testSetUp(self):
        """sets up a new in-memory datastore for each test"""
        # keep this import here, in order to not load
        # dev_appserver_main with restricted libs (tempfile) which fails
        from google.appengine.tools import dev_appserver_main, dev_appserver
        args = dev_appserver_main.DEFAULT_ARGS.copy()
        args['datastore_path'], args['history_path'] = None, None
        args.update(self.appserver_args)
        dev_appserver.SetupStubs(self.appid, **args)

    def tearDown(self):
        pass

dbLayer = DBLayer('DBLayer')


