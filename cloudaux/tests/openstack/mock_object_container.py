"""
.. module: cloudaux.tests.openstack.mock_object_container
    :platform: Unix
    :copyright: Copyright (c) 2017 AT&T Intellectual Property. All rights reserved. See AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Michael Stair <mstair@att.com>
"""
def mock_get_container_metadata(conn=None, **kwargs):
     from openstack.object_store.v1.container import Container
     from cloudaux.tests.openstack.mock_utils import container_body, container_headers

     body_plus_headers = dict(container_body, **container_headers)

     container = Container(body_plus_headers)
     return container
