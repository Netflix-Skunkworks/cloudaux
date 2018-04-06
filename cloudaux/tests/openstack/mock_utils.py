"""
.. module: cloudaux.tests.openstack.mock_utils
    :platform: Unix
    :copyright: Copyright (c) 2017 AT&T Intellectual Property. All rights reserved. See AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Michael Stair <mstair@att.com>
"""
from mock import patch
from openstack import connection


""" Utilizes the OpenStack SDK unit test data. Avoids duplication, but does couple """

def mock_list_items(conn=None, **kwargs):
    with patch('openstack.connection.Connection'):
        service = kwargs['service']
        generator = kwargs['generator']
        f = 'mock_list_%s'%generator

        return globals()[f](conn, **kwargs)

def mock_list_networks(conn=None, **kwargs):
    with patch('openstack.connection.Connection'):
         from openstack.network.v2.network import Network
         from openstack.tests.unit.network.v2.test_network import EXAMPLE

         conn = connection.Connection()
         conn.network.networks.side_effect = [ [Network(**EXAMPLE)] ]
         return [x for x in conn.network.networks()]

def mock_list_ports(conn=None, **kwargs):
    with patch('openstack.connection.Connection'):
         from openstack.network.v2.port import Port
         from openstack.tests.unit.network.v2.test_port import EXAMPLE

         conn = connection.Connection()
         conn.network.ports.side_effect = [ [Port(**EXAMPLE)] ]
         return [x for x in conn.network.ports()]

def mock_list_subnets(conn=None, **kwargs):
    with patch('openstack.connection.Connection'):
         from openstack.network.v2.subnet import Subnet
         from openstack.tests.unit.network.v2.test_subnet import EXAMPLE

         conn = connection.Connection()
         conn.network.subnets.side_effect = [ [Subnet(**EXAMPLE)] ]
         return [x for x in conn.network.subnets()]

def mock_list_routers(conn=None, **kwargs):
    with patch('openstack.connection.Connection'):
         from openstack.network.v2.router import Router
         from openstack.tests.unit.network.v2.test_router import EXAMPLE

         conn = connection.Connection()
         conn.network.routers.side_effect = [ [Router(**EXAMPLE)] ]
         return [x for x in conn.network.routers()]

def mock_list_ips(conn=None, **kwargs):
    with patch('openstack.connection.Connection'):
         from openstack.network.v2.floating_ip import FloatingIP
         from openstack.tests.unit.network.v2.test_floating_ip import EXAMPLE

         conn = connection.Connection()
         conn.network.ips.side_effect = [ [FloatingIP(**EXAMPLE)] ]
         return [x for x in conn.network.ips()]

def mock_list_security_groups(conn=None, **kwargs):
    with patch('openstack.connection.Connection'):
         from openstack.network.v2.security_group import SecurityGroup
         from openstack.tests.unit.network.v2.test_security_group import EXAMPLE

         conn = connection.Connection()
         conn.network.security_groups.side_effect = [ [SecurityGroup(**EXAMPLE)] ]
         return [x for x in conn.network.security_groups()]

def mock_list_servers(conn=None, **kwargs):
    with patch('openstack.connection.Connection'):
         from openstack.compute.v2.server import Server
         from openstack.tests.unit.compute.v2.test_server import EXAMPLE

         # The server example has an invalid security_group list
         server = Server(**EXAMPLE)
         server.security_groups=[{u'name': u'default'}]

         conn = connection.Connection()
         conn.compute.servers.side_effect = [ [server] ]
         return [x for x in conn.compute.servers()]

def mock_list_images(conn=None, **kwargs):
    with patch('openstack.connection.Connection'):
         from openstack.compute.v2.image import Image
         from openstack.tests.unit.compute.v2.test_image import DETAIL_EXAMPLE

         conn = connection.Connection()
         conn.compute.images.side_effect = [ [Image(**DETAIL_EXAMPLE)] ]
         return [x for x in conn.compute.images()]

def mock_list_users(conn=None, **kwargs):
    with patch('openstack.connection.Connection'):
         from openstack.identity.v3.user import User
         from openstack.tests.unit.identity.v3.test_user import EXAMPLE

         conn = connection.Connection()
         conn.identity.users.side_effect = [ [User(**EXAMPLE)] ]
         return [x for x in conn.identity.users()]

def mock_list_load_balancers(conn=None, **kwargs):
    with patch('openstack.connection.Connection'):
         from openstack.load_balancer.v2.load_balancer import LoadBalancer
         from openstack.tests.unit.load_balancer.test_load_balancer import EXAMPLE

         conn = connection.Connection()
         conn.load_balancer.load_balancers.side_effect = [ [LoadBalancer(**EXAMPLE)] ]
         return [x for x in conn.load_balancer.load_balancers()]

def mock_list_containers(conn=None, **kwargs):
    with patch('openstack.connection.Connection'):
         from openstack.object_store.v1.container import Container
         from openstack.tests.unit.object_store.v1.test_container import CONT_EXAMPLE, HEAD_EXAMPLE

         container = Container(CONT_EXAMPLE)
         container._attrs.update({'headers': HEAD_EXAMPLE})

         conn = connection.Connection()
         conn.object_store.containers.side_effect = [ [container] ]
         return [x for x in conn.object_store.containers()]
