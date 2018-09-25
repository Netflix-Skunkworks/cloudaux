"""
.. module: cloudaux.gcp.auth
    :platform: Unix
    :copyright: (c) 2016 by Google Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Tom Melendez (@supertom) <supertom@google.com>
"""
import importlib

from httplib2 import Http
from apiclient.discovery import build
from googleapiclient.http import set_user_agent
from oauth2client.client import GoogleCredentials
from oauth2client.service_account import ServiceAccountCredentials

from cloudaux.gcp.config import USE_GAX, GOOGLE_CLIENT_MAP, DEFAULT_SCOPES
from cloudaux.gcp.decorators import gcp_cache, gcp_stats
from cloudaux.gcp.utils import get_user_agent


@gcp_stats()
@gcp_cache(future_expiration_minutes=15)
def get_client(service, service_type='client', **conn_args):
    """
    User function to get the correct client.

    Based on the GOOGLE_CLIENT_MAP dictionary, the return will be a cloud or general
    client that can interact with the desired service.

    :param service: GCP service to connect to. E.g. 'gce', 'iam'
    :type service: ``str``

    :param conn_args: Dictionary of connection arguments.  'project' is required.
                      'user_agent' can be specified and will be set in the client
                       returned.
    :type conn_args: ``dict``

    :return: client_details, client
    :rtype: ``tuple`` of ``dict``, ``object``
    """
    client_details = choose_client(service)
    user_agent = get_user_agent(**conn_args)
    if client_details:
        if client_details['client_type'] == 'cloud':
            client = get_gcp_client(
                mod_name=client_details['module_name'],
                pkg_name=conn_args.get('pkg_name', 'google.cloud'),
                key_file=conn_args.get('key_file', None),
                project=conn_args['project'], user_agent=user_agent)
        else:
            client = get_google_client(
                mod_name=client_details['module_name'],
                key_file=conn_args.get('key_file', None),
                user_agent=user_agent, api_version=conn_args.get('api_version', 'v1'))
    else:
        # There is no client known for this service. We can try the standard API.
        try:
            client = get_google_client(
                mod_name=service, key_file=conn_args.get('key_file', None),
                user_agent=user_agent, api_version=conn_args.get('api_version', 'v1'))
        except Exception as e:
            raise e

    return client_details, client


def choose_client(service):
    """
    Logic to choose the appropriate client.

    :param service: Google Cloud service name. Examples: 'iam', 'gce'.
    :type service: ``str``

    :return: specific dictionary recommended for a particular service.
    :rtype: ``dict``
    """
    client_options = get_available_clients(service)
    if client_options:
        # For now, choose the first one available
        return client_options[0]
    return None


def get_available_clients(service):
    """
    Return clients available for this service.

    :param service: Google Cloud service name. Examples: 'iam', 'gce'.
    :type service: ``str``

    :return: list of dictionaries describing the clients available.
    :rtype: ``list``
    """
    details = GOOGLE_CLIENT_MAP.get(service, None)
    if details:
        return [details]
    else:
        return None


def get_gcp_client(**kwargs):
    """Public GCP client builder."""
    return _gcp_client(project=kwargs['project'], mod_name=kwargs['mod_name'],
                       pkg_name=kwargs.get('pkg_name', 'google.cloud'),
                       key_file=kwargs.get('key_file', None),
                       http_auth=kwargs.get('http', None),
                       user_agent=kwargs.get('user_agent', None))


def _gcp_client(project, mod_name, pkg_name, key_file=None, http_auth=None,
                user_agent=None):
    """
    Private GCP client builder.

    :param project: Google Cloud project string.
    :type project: ``str``

    :param mod_name: Module name to load.  Should be found in sys.path.
    :type mod_name: ``str``

    :param pkg_name: package name that mod_name is part of.  Default is 'google.cloud' .
    :type pkg_name: ``str``

    :param key_file: Default is None.
    :type key_file: ``str`` or None

    :param http_auth: httplib2 authorized client. Default is None.
    :type http_auth: :class: `HTTPLib2`

    :param user_agent: User Agent string to use in requests. Default is None.
    :type http_auth: ``str`` or None

    :return: GCP client
    :rtype: ``object``
    """
    client = None
    if http_auth is None:
        http_auth = _googleauth(key_file=key_file, user_agent=user_agent)
    try:
        # Using a relative path, so we prefix with a dot (.)
        google_module = importlib.import_module('.' + mod_name,
                                                package=pkg_name)
        client = google_module.Client(use_GAX=USE_GAX, project=project,
                                      http=http_auth)
    except ImportError as ie:
        import_err = 'Unable to import %s.%s' % (pkg_name, mod_name)
        raise ImportError(import_err)
    except TypeError:
        # Not all clients use gRPC
        client = google_module.Client(project=project, http=http_auth)
    if user_agent and hasattr(client, 'user_agent'):
        client.user_agent = user_agent
    return client


def get_google_client(**kwargs):
    return _google_client(kwargs['mod_name'], key_file=kwargs['key_file'],
                          scopes=kwargs.get('scopes', []),
                          http_auth=kwargs.get('http_auth', None),
                          api_version=kwargs.get('api_version', 'v1'),
                          user_agent=kwargs.get('user_agent', None))


def _google_client(mod_name, key_file, scopes, http_auth, api_version,
                   user_agent):
    if http_auth is None:
        http_auth = _googleauth(key_file=key_file, scopes=scopes,
                                user_agent=user_agent)
    client = _build_google_client(service=mod_name, api_version=api_version,
                                  http_auth=http_auth)
    return client


def _googleauth(key_file=None, scopes=[], user_agent=None):
    """
    Google http_auth helper.

    If key_file is not specified, default credentials will be used.

    If scopes is specified (and key_file), will be used instead of DEFAULT_SCOPES

    :param key_file: path to key file to use. Default is None
    :type key_file: ``str``

    :param scopes: scopes to set.  Default is DEFAUL_SCOPES
    :type scopes: ``list``

    :param user_agent: User Agent string to use in requests. Default is None.
    :type http_auth: ``str`` or None

    :return: HTTPLib2 authorized client.
    :rtype: :class: `HTTPLib2`
    """
    if key_file:
        if not scopes:
            scopes = DEFAULT_SCOPES
        creds = ServiceAccountCredentials.from_json_keyfile_name(key_file,
                                                                 scopes=scopes)
    else:
        creds = GoogleCredentials.get_application_default()
    http = Http()
    if user_agent:
        http = set_user_agent(http, user_agent)
    http_auth = creds.authorize(http)
    return http_auth


def _build_google_client(service, api_version, http_auth):
    """
    Google build client helper.

    :param service: service to build client for
    :type service: ``str``

    :param api_version: API version to use.
    :type api_version: ``str``

    :param http_auth: Initialized HTTP client to use.
    :type http_auth: ``object``

    :return: google-python-api client initialized to use 'service'
    :rtype: ``object``
    """
    client = build(service, api_version, http=http_auth)
    return client
