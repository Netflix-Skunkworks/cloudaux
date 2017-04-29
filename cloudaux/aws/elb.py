"""
.. module: cloudaux.aws.elb
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Patrick Kelley <patrick@netflix.com>
"""
from cloudaux.aws.sts import sts_conn
from cloudaux.aws.decorators import rate_limited
from cloudaux.aws.decorators import paginated


@paginated('LoadBalancerDescriptions', response_pagination_marker='NextMarker')
@sts_conn('elb')
@rate_limited()
def describe_load_balancers(client=None, **kwargs):
    return client.describe_load_balancers(**kwargs)


@sts_conn('elb')
@rate_limited()
def describe_load_balancer_attributes(load_balancer_name, client=None):
    return client.describe_load_balancer_attributes(
        LoadBalancerName=load_balancer_name)['LoadBalancerAttributes']


@sts_conn('elb')
@rate_limited()
def describe_load_balancer_policies(load_balancer_name, policy_names, client=None):
    return client.describe_load_balancer_policies(
        LoadBalancerName=load_balancer_name,
        PolicyNames=policy_names)['PolicyDescriptions']


@sts_conn('elb')
@rate_limited()
def describe_load_balancer_policy_types(policy_type_names, client=None):
    return client.describe_load_balancer_policy_types(
        PolicyTypeNames=policy_type_names)['PolicyTypeDescriptions']


@sts_conn('elb')
@rate_limited()
def describe_tags(load_balancer_names, client=None):
    return client.describe_tags(
        LoadBalancerNames=load_balancer_names)['TagDescriptions']