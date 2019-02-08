"""
.. module: cloudaux.tests.openstack.test-conn
    :platform: Unix
    :copyright: Copyright (c) 2018 AT&T Intellectual Property. All rights reserved. See AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Michael Stair <mstair@att.com>
"""
import os
import unittest
import mock

from cloudaux.openstack.decorators import _connect, get_regions

class TestConn(unittest.TestCase):

    def setUp(self):
        self.base_dir = os.getcwd()
        self.fixtures_dir = 'cloudaux/tests/openstack/fixtures'

    def _get_fixture(self, file_name):
        return os.path.join(self.base_dir,
                            self.fixtures_dir,
                            file_name)
    def test_connect(self):
        conn = _connect("mycloud", "RegionOne", self._get_fixture("test-clouds.yaml") )
        self.assertEqual(conn.name, "mycloud")
    
    def test_get_regions(self):
        regions = [{'name': u'RegionOne', 'values': {}}, {'name': u'RegionTwo', 'values': {}}]
        self.assertEqual(regions, get_regions("mycloud", self._get_fixture("test-clouds.yaml") ) )

if __name__ == '__main__':
    unittest.main()
