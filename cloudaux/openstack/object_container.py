"""
.. module: cloudaux.openstack.object_container
    :platform: Unix
    :copyright: Copyright (c) 2017 AT&T Intellectual Property. All rights reserved. See AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Michael Stair <mstair@att.com>
"""
from cloudaux.openstack.decorators import openstack_conn

@openstack_conn()
def get_container_metadata(conn=None, **kwargs):
    return conn.object_store.get_container_metadata(**kwargs)
