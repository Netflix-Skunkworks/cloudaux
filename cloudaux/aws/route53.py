"""
.. module: cloudaux.aws.route53
    :platform: Unix
    :copyright: (c) 2016 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Patrick Kelley <patrick@netflix.com>
"""

from cloudaux.aws.sts import sts_conn
from cloudaux.aws.decorators import rate_limited


@sts_conn('route53', service_type='client')
@rate_limited()
def list_hosted_zones(**kwargs):
    client = kwargs.pop('client')
    paginator = client.get_paginator('list_hosted_zones')
    hosted_zones = []
    for hosted_zone in paginator.paginate():
        hosted_zones.extend(hosted_zone['HostedZones'])
    return hosted_zones


@sts_conn('route53', service_type='client')
@rate_limited()
def list_resource_record_sets(**kwargs):
    client = kwargs.pop('client')
    paginator = client.get_paginator('list_resource_record_sets')
    resource_record_sets = []
    for resource_record_set in paginator.paginate(HostedZoneId=kwargs.pop('Id')):
        resource_record_sets.extend(resource_record_set['ResourceRecordSets'])
    return resource_record_sets


@sts_conn('route53', service_type='client')
@rate_limited()
def get_hosted_zone(**kwargs):
    client = kwargs.pop('client')
    return client.get_hosted_zone(**kwargs)

