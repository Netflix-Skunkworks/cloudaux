"""
.. module: cloudaux.gcp.gce.forwarding_rule
    :platform: Unix
    :copyright: (c) 2019 by Fitbit Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Greg Harris <gharris@fitbit.com>
"""
from cloudaux.gcp.utils import gce_list, gce_list_aggregated
from cloudaux.gcp.decorators import gcp_conn


@gcp_conn('gce')
def list_forwarding_rules(client=None, **kwargs):
    """
    :rtype: ``list``
    """

    return gce_list_aggregated(service=client.forwardingRules(), **kwargs)


@gcp_conn('gce')
def list_global_forwarding_rules(client=None, **kwargs):
    """
    :rtype: ``list``
    """

    return gce_list(service=client.globalForwardingRules(), **kwargs)


@gcp_conn('gce')
def get_forwarding_rule(client=None, **kwargs):
    service = client.forwardingRules()
    req = service.get(project=kwargs['project'],
                      forwardingRule=kwargs['ForwardingRule'],
                      region=kwargs['Region'])
    return req.execute()


@gcp_conn('gce')
def get_global_forwarding_rule(client=None, **kwargs):
    service = client.globalForwardingRules()
    req = service.get(project=kwargs['project'],
                      forwardingRule=kwargs['GlobalForwardingRule'])
    return req.execute()
