"""
.. module: cloudaux.openstack.utils
    :platform: Unix
    :copyright: Copyright (c) 2017 AT&T Intellectual Property. All rights reserved. See AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Michael Stair <mstair@att.com>
"""
from cloudaux.openstack.decorators import openstack_conn

@openstack_conn()
def list_items(conn=None, **kwargs):
    """
    :rtype: ``list``
    """
    return [x for x in getattr( getattr( conn, kwargs.pop('service') ),
                kwargs.pop('generator'))(**kwargs)]
