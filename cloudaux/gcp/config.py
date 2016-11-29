"""
.. module: cloudaux.gcp.config
    :platform: Unix
    :copyright: (c) 2016 by Google Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Tom Melendez (@supertom) <supertom@google.com>
"""

USE_GAX=False
# TODO(supertom): Change: this is not a good default scope.
DEFAULT_SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

"""
There are currently two distinct client types for working with Google APIs.
We use the 'client_type' to distinguish between the two:
- cloud: gcloud-python.  This is recommended, but not available for all services yet.
- general: google-python-api-client.  This is available for many services, but is deprecated.
"""
GOOGLE_CLIENT_MAP = {
    'gcs':
    {'client_type': 'cloud', 'module_name': 'storage'},
    'gce':
    {'client_type': 'general', 'module_name': 'compute'},
    'iam':
    {'client_type': 'general', 'module_name': 'iam'}
}
