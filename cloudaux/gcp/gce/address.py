"""
.. module: cloudaux.gcp.gce.address
    :platform: Unix
    :copyright: (c) 2019 by Fitbit Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Greg Harris <gharris@fitbit.com>
"""
from cloudaux.gcp.utils import gce_list, gce_list_aggregated
from cloudaux.gcp.decorators import gcp_conn

@gcp_conn('gce')
def list_addresses(client=None, **kwargs):
    """
    :rtype: ``list``
    """

    return gce_list_aggregated(service=client.addresses(), **kwargs)


@gcp_conn('gce')
def list_global_addresses(client=None, **kwargs):
    """
    :rtype: ``list``
    """

    return gce_list(service=client.globalAddresses(), **kwargs)


@gcp_conn('gce')
def get_address(client=None, **kwargs):
    service = client.addresses()
    req = service.get(project=kwargs['project'],
                      address=kwargs['Address'],
                      region=kwargs['Region'])
    return req.execute()


@gcp_conn('gce')
def get_global_address(client=None, **kwargs):
    service = client.globalAddresses()
    req = service.get(project=kwargs['project'],
                      address=kwargs['GlobalAddress'])
    return req.execute()
