"""
.. module: cloudaux.gcp.crm
    :platform: Unix
    :copyright: (c) 2019 by Fitbit Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Greg Harris <gharris@fitbit.com>
"""
from cloudaux.gcp.utils import service_list
from cloudaux.gcp.decorators import gcp_conn, gcp_stats
from cloudaux.gcp.utils import service_list


@gcp_conn('crm')
def get_iam_policy(client=None, **kwargs):
    # body={} workaround for https://github.com/googleapis/google-api-python-client/issues/713
    req = client.projects().getIamPolicy(resource=kwargs['resource'], body={})
    return req.execute()

