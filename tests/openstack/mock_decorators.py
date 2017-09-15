"""
.. module: cloudaux.tests.openstack.mock_decorators
    :platform: Unix
    :copyright: Copyright (c) 2017 AT&T Intellectual Property. All rights reserved. See AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Michael Stair <mstair@att.com>
"""
from functools import wraps

from os_client_config import OpenStackConfig
from openstack import connection


def mock_get_regions(cloud_name, yaml_file):
    return [ {'name':'RegionOne'} ]

def mock_openstack_conn():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            kwargs['conn'] = None
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def mock_iter_account_region(account_regions):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            results = []
            kwargs['account_name'] = 'TEST_ACCOUNT'
            kwargs['cloud_name'] = 'foo'
            kwargs['yaml_file'] = 'bar'
            kwargs['region'] = 'RegionOne'
            results.append(func(*args, **kwargs))
            return results
        return decorated_function
    return decorator
