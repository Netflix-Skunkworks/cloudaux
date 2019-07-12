"""
.. module: cloudaux.gcp.gce.disk
    :platform: Unix
    :copyright: (c) 2019 by Fitbit Inc., see AUTHORS for more
    :license: Apache, see LCIENSE for more details.
.. moduleauthor:: Greg Harris <gharris@fitbit.com>
"""
from cloudaux.gcp.utils import gce_list
from cloudaux.gcp.decorators import gcp_conn

@gcp_conn('gce')
def list_disks(client=None, **kwargs):
    """
    :rtype: ``list``
    """
    return gce_list(service=client.disks(),
                        **kwargs)

@gcp_conn('gce')
def get_disk(client=None, **kwargs):
    service = client.disks()
    req = service.get(project=kwargs['project'], name=kwargs['disk'])
    resp = req.execute()
    return resp
