"""
.. module: cloudaux.gcp.gce.network
    :platform: Unix
    :copyright: (c) 2016 by Google Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Tom Melendez (@supertom) <supertom@google.com>
"""
from cloudaux.gcp.utils import gce_list, gce_list_aggregated
from cloudaux.gcp.decorators import gcp_conn

@gcp_conn('gce')
def list_networks(client=None, **kwargs):
    """
    :rtype: ``list``
    """
    return gce_list(service=client.networks(),
                        **kwargs)

@gcp_conn('gce')
def list_subnetworks(client=None, **kwargs):
    """
    :rtype: ``list``
    """

    return gce_list_aggregated(service=client.subnetworks(),
                                   key_name='subnetworks', **kwargs)

@gcp_conn('gce')
def get_network(client=None, **kwargs):
    service = client.networks()
    req = service.get(project=kwargs['project'], network=kwargs['Network'])
    resp = req.execute()
    return resp

@gcp_conn('gce')
def get_subnetwork(client=None, **kwargs):
    service = client.subnetworks()
    req = service.get(project=kwargs['project'],
                      subnetwork=kwargs['Subnetwork'], region=kwargs['Region'])
    resp = req.execute()
    return resp
