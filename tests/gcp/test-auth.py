"""
.. module: cloudaux.tests.gcp.test-auth
    :platform: Unix
    :copyright: (c) 2016 by Google Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Tom Melendez (@supertom) <supertom@google.com>
"""
import unittest
import mock

from apiclient.discovery import build, Resource
from apiclient.http import HttpMock
#from oauth2client.client import GoogleCredentials
import os

from cloudaux.gcp import auth


class TestAuth(unittest.TestCase):

    def setUp(self):
        self.base_dir = os.getcwd()
        self.fixtures_dir = 'tests/gcp/fixtures'

    def _get_fixture(self, file_name):
        return os.path.join(self.base_dir,
                            self.fixtures_dir,
                            file_name)
    def _make_http():
        import httplib2
        return mock.Mock(spec=httplib2.Http)

    def _make_credentials():
        import google.auth.credentials
        return mock.Mock(spec=google.auth.credentials.Credentials)
    
    def test_get_available_clients(self):
        actual = auth.get_available_clients('foobaradfadfdfadf332343')
        self.assertFalse(actual)

        actual = auth.get_available_clients('gce')
        self.assertTrue(isinstance(actual, list))
        self.assertTrue(isinstance(actual[0], dict))
        self.assertTrue('client_type' in actual[0])
        self.assertTrue('module_name' in actual[0])
        
    def test_choose_client(self):
        actual = auth.choose_client('foobaradfadfdfadf332343')
        self.assertFalse(actual)

        actual = auth.choose_client('gce')
        self.assertTrue(isinstance(actual, dict))
        self.assertTrue('client_type' in actual)
        self.assertTrue('module_name' in actual)

    def test__build_google_client(self):
        http_auth = HttpMock(self._get_fixture('compute.json'), {'status': '200'})
        client = auth._build_google_client('compute', 'v1', http_auth=http_auth)
        self.assertTrue(hasattr(client, '__class__'))
        self.assertTrue(isinstance(client, Resource))

    def test__googleauth(self):
        """
        TODO(supertom): add mocking, make more robust, etc.
        This test make a lot of assumptions:
        1. Running on GCE
        3. Doesn't truly verify the Http object is authorized.
        However, this function is critical for valid GCP operation
        so it is good to have a sanity check that we have an Http object.
        """
        from httplib2 import Http
        # default creds
        http_auth = auth._googleauth()
        self.assertTrue(isinstance(http_auth, Http))

        # service account key
        test_key_file = self._get_fixture('testkey.json')
        http_auth = auth._googleauth(key_file=test_key_file)
        self.assertTrue(isinstance(http_auth, Http))

if __name__ == '__main__':
    unittest.main()
