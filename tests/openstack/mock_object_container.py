"""
.. module: cloudaux.tests.openstack.mock_object_container
    :platform: Unix
    :copyright: Copyright (c) 2017 AT&T Intellectual Property. All rights reserved. See AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Michael Stair <mstair@att.com>
"""
def mock_get_container_metadata(conn=None, **kwargs):
     from openstack.object_store.v1.container import Container
     from openstack.tests.unit.object_store.v1.test_container import CONT_EXAMPLE, HEAD_EXAMPLE

     container = Container(CONT_EXAMPLE)
     container._attrs.update({'headers': HEAD_EXAMPLE})
     return container
