"""
.. module: cloudaux.tests.gcp.test-utils
    :platform: Unix
    :copyright: (c) 2016 by Google Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Tom Melendez (@supertom) <supertom@google.com>
"""
import unittest

from cloudaux.gcp import utils

class TestUtils(unittest.TestCase):

    def test_get_creds_from_kwargs(self):
        data = { 'project': 'my-project', 'key_file': '/path/to/myfile.json', 'foo': 'bar'}
        expected_creds = {
            'project': 'my-project', 'key_file': '/path/to/myfile.json', 'http_auth': None
        }
        expected_kwargs = { 'project': 'my-project', 'foo': 'bar'}
        actual_creds, actual_kwargs = utils.get_creds_from_kwargs(data)
        self.assertEqual(expected_creds, actual_creds)
        self.assertEqual(expected_kwargs, actual_kwargs)

    def test_rewrite_kwargs(self):
        data = { 'project': 'my-project', 'key_file': '/path/to/myfile.json', 'foo': 'bar'}
        expected_general = {
            'name': 'projects/my-project', 'key_file': '/path/to/myfile.json', 'foo': 'bar'
        }
        actual_general = utils.rewrite_kwargs('general', data)
        self.assertEqual(expected_general, actual_general)
    
if __name__ == '__main__':
    unittest.main()
