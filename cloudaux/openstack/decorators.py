"""
.. module: cloudaux.openstack.decorators
    :platform: Unix
    :copyright: Copyright (c) 2017 AT&T Intellectual Property. All rights reserved. See AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Michael Stair <mstair@att.com>
"""
from functools import wraps

from os_client_config import OpenStackConfig
from openstack import connection
from openstack.exceptions import HttpException

""" this is mix of the aws and gcp decorator conventions """

CACHE = {}

def _connect(cloud_name, region, yaml_file):
    occ = OpenStackConfig(config_files=[yaml_file])
    cloud = occ.get_one_cloud(cloud_name, region_name=region)
    _cloud_name = cloud.get_auth_args().get('project_id')
    return ( _cloud_name, connection.from_config(cloud_config=cloud) )


def get_regions(cloud_name, yaml_file):
    occ = OpenStackConfig(config_files=[yaml_file])
    return occ._get_regions(cloud_name)


def keystone_cached_conn(cloud_name, region, yaml_file):
    key = (
        cloud_name,
        region )

    if key in CACHE:
        """ check the token to see if our connection is still valid """
        _cloud_name, conn = CACHE[key]
        try:
            conn.authorize()
        except HttpException:
            del CACHE[key]
        else:
            return conn
    try:
        _cloud_name, conn = _connect(cloud_name, region, yaml_file)
    except Exception as e:
        raise e

    CACHE[key] = (_cloud_name, conn)
    return conn

def openstack_conn():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            kwargs['conn'] = keystone_cached_conn(
                kwargs.pop('cloud_name'), kwargs.pop('region'), kwargs.pop('yaml_file') )
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def iter_account_region(account_regions):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            threads = []
            for account_creds, regions in account_regions.iteritems():
                account_name, cloud_name, yaml_file = account_creds
                for region in regions:
                    kwargs['account_name'] = account_name
                    kwargs['cloud_name'] = cloud_name
                    kwargs['yaml_file'] = yaml_file
                    kwargs['region'] = region
                    result = func(*args, **kwargs)
                    if result:
                        threads.append(result)
            result = []
            for thread in threads:
                result.append(thread)
            return result
        return decorated_function
    return decorator
