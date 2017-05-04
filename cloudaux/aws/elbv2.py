from cloudaux.aws.sts import sts_conn
from cloudaux.aws.decorators import rate_limited
from cloudaux.aws.decorators import paginated


@paginated('LoadBalancers', response_pagination_marker='NextMarker')
@sts_conn('elbv2')
@rate_limited()
def describe_load_balancers(arns=None, names=None, client=None):
    """
    Permission: elasticloadbalancing:DescribeLoadBalancers
    """
    kwargs = dict()
    if arns:
        kwargs.update(dict(LoadBalancerArns=arns))
    if names:
        kwargs.update(dict(Names=names))
    return client.describe_load_balancers(**kwargs)


@paginated('Listeners', response_pagination_marker='NextMarker')
@sts_conn('elbv2')
@rate_limited()
def describe_listeners(load_balancer_arn=None, listener_arns=None, client=None):
    """
    Permission: elasticloadbalancing:DescribeListeners
    """
    kwargs = dict()
    if load_balancer_arn:
        kwargs.update(dict(LoadBalancerArn=load_balancer_arn))
    if listener_arns:
        kwargs.update(dict(ListenerArns=listener_arns))
    return client.describe_listeners(**kwargs)


@sts_conn('elbv2')
@rate_limited()
def describe_load_balancer_attributes(arn, client=None):
    """
    Permission: elasticloadbalancing:DescribeLoadBalancerAttributes
    """
    return client.describe_load_balancer_attributes(
        LoadBalancerArn=arn)['Attributes']


@sts_conn('elbv2')
@rate_limited()
def describe_rules(listener_arn=None, rule_arns=None, client=None):
    """
    Permission: elasticloadbalancing:DescribeRules
    """
    kwargs = dict()
    if listener_arn:
        kwargs.update(dict(ListenerArn=listener_arn))
    if rule_arns:
        kwargs.update(dict(RuleArns=rule_arns))
    return client.describe_rules(**kwargs)['Rules']


@paginated('SslPolicies', response_pagination_marker='NextMarker')
@sts_conn('elbv2')
@rate_limited()
def describe_ssl_policies(names, client=None):
    return client.describe_ssl_policies(Names=names)


@sts_conn('elbv2')
@rate_limited()
def describe_tags(arns, client=None):
    """
    Permission: elasticloadbalancing:DescribeTags
    """
    return client.describe_tags(ResourceArns=arns)['TagDescriptions']


@sts_conn('elbv2')
@rate_limited()
def describe_target_group_attributes(arn, client=None):
    """
    Permission: elasticloadbalancing:DescribeTargetGroupAttributes
    """
    return client.describe_target_group_attributes(TargetGroupArn=arn)['Attributes']


@paginated('TargetGroups', response_pagination_marker='NextMarker')
@sts_conn('elbv2')
@rate_limited()
def describe_target_groups(load_balancer_arn=None, target_group_arns=None, names=None, client=None):
    """
    Permission: elasticloadbalancing:DescribeTargetGroups
    """
    kwargs = dict()
    if load_balancer_arn:
        kwargs.update(LoadBalancerArn=load_balancer_arn)
    if target_group_arns:
        kwargs.update(TargetGroupArns=target_group_arns)
    if names:
        kwargs.update(Names=names)
    return client.describe_target_groups(**kwargs)


@sts_conn('elbv2')
@rate_limited()
def describe_target_health(target_group_arn, targets=None, client=None):
    """
    Permission: elasticloadbalancing:DescribeTargetHealth
    """
    kwargs = dict(TargetGroupArn=target_group_arn)
    if targets:
        kwargs.update(Targets=targets)
    return client.describe_target_health(**kwargs)['TargetHealthDescriptions']
