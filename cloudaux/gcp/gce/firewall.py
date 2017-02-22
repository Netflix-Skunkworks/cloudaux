"""
.. module: cloudaux.gcp.gce.firewall
    :platform: Unix
    :copyright: (c) 2016 by Google Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Tom Melendez (@supertom) <supertom@google.com>
"""
from cloudaux.gcp.utils import gce_list
from cloudaux.gcp.decorators import gcp_conn

@gcp_conn('gce')
def list_firewall_rules(client=None, **kwargs):
    """
    :rtype: ``list``
    """
    return gce_list(service=client.firewalls(),
                        **kwargs)

@gcp_conn('gce')
def get_firewall_rule(client=None, **kwargs):
    service = client.firewalls()
    req = service.get(project=kwargs['project'], firewall=kwargs['Firewall'])
    resp = req.execute()
    return resp
