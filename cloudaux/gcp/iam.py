"""
.. module: cloudaux.gcp.iam
    :platform: Unix
    :copyright: (c) 2016 by Google Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Tom Melendez (@supertom) <supertom@google.com>
"""
from cloudaux.gcp.utils import service_list
from cloudaux.gcp.decorators import gcp_conn, gcp_stats
from cloudaux.gcp.utils import service_list

@gcp_conn('iam')
def list_serviceaccounts(client=None, **kwargs):
    return service_list(service=client.projects().serviceAccounts(),
                        key_name='accounts', **kwargs)
@gcp_conn('iam')
def get_serviceaccount(client=None, **kwargs):
    """
    service_account='string'
    """
    service_account=kwargs.pop('service_account')
    resp = client.projects().serviceAccounts().get(
        name=service_account).execute()
    return resp

@gcp_conn('iam')
def get_serviceaccount_keys(client=None, **kwargs):
    """
    service_account='string'
    """
    service_account=kwargs.pop('service_account')
    kwargs['name'] = service_account
    return service_list(client.projects().serviceAccounts().keys(),
                        key_name='keys', **kwargs)
@gcp_conn('iam')
def get_iam_policy(client=None, **kwargs):
    """
    service_account='string'
    """
    service_account=kwargs.pop('service_account')
    resp = client.projects().serviceAccounts().getIamPolicy(
        resource=service_account).execute()
    # TODO(supertom): err handling, check if 'bindings' is correct
    if 'bindings' in resp:
        return resp['bindings']
    else:
        return None
