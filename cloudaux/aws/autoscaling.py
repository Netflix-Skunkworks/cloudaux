"""
.. module: cloudaux.aws.autoscaling
    :platform: Unix
    :copyright: (c) 2015 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
.. moduleauthor:: Patrick Kelley <patrick@netflix.com>
"""
from cloudaux.aws.sts import sts_conn
from cloudaux.aws.decorators import rate_limited


@sts_conn('autoscaling')
@rate_limited()
def describe_auto_scaling_groups(account_number=None, region=None, assume_role=None, client=None):
    return client.get_paginator('describe_auto_scaling_groups').paginate(PaginationConfig={'MaxItems': 500})


@sts_conn('autoscaling')
@rate_limited()
def describe_launch_configurations(account_number=None, region=None, assume_role=None, client=None):
    return client.get_paginator('describe_launch_configurations').paginate()


@sts_conn('autoscaling')
@rate_limited()
def create_launch_configuration(**kwargs):
    return kwargs.pop('client').create_launch_configuration(**kwargs)


@sts_conn('autoscaling')
@rate_limited()
def create_auto_scaling_group(name, launch_config_name, account_number=None, region=None, assume_role=None, client=None):
    return client.create_auto_scaling_group(
        AutoScalingGroupName=name,
        MaxSize=1,
        MinSize=1,
        LaunchConfigurationName=launch_config_name
    )


@sts_conn('autoscaling')
@rate_limited()
def update_auto_scaling_group(**kwargs):
    return kwargs.pop('client').update_auto_scaling_group(**kwargs)
