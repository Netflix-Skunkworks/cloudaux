from cloudaux.aws.elbv2 import *
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags

registry = FlagRegistry()
FLAGS = Flags('BASE', 'LISTENERS', 'RULES', 'ATTRIBUTES', 'TAGS',
              'TARGET_GROUPS', 'TARGET_GROUP_ATTRIBUTES', 'TARGET_GROUP_HEALTH')


@registry.register(flag=FLAGS.LISTENERS, depends_on=FLAGS.BASE, key='listeners')
def get_listeners(alb, **conn):
    return describe_listeners(load_balancer_arn=alb['LoadBalancerArn'], **conn)


@registry.register(flag=FLAGS.RULES, depends_on=FLAGS.LISTENERS, key='rules')
def get_rules(alb, **conn):
    rules = list()
    for listener in alb['listeners']:
        rules.extend(describe_rules(listener_arn=listener['ListenerArn'], **conn))
    return rules


@registry.register(flag=FLAGS.ATTRIBUTES, depends_on=FLAGS.BASE, key='attributes')
def get_attributes(alb, **conn):
    return describe_load_balancer_attributes(alb['LoadBalancerArn'], **conn)


@registry.register(flag=FLAGS.TAGS, depends_on=FLAGS.BASE, key='tags')
def get_tags(alb, **conn):
    return describe_tags([alb['LoadBalancerArn']], **conn)


@registry.register(flag=FLAGS.TARGET_GROUPS, depends_on=FLAGS.BASE, key='target_groups')
def get_target_groups(alb, **conn):
    return describe_target_groups(load_balancer_arn=alb['LoadBalancerArn'], **conn)


@registry.register(flag=FLAGS.TARGET_GROUP_ATTRIBUTES, depends_on=FLAGS.TARGET_GROUPS, key='target_group_attributes')
def _get_target_group_attributes(alb, **conn):
    target_group_attributes = list()
    for target_group in alb['target_groups']:
        target_group_attributes.extend(
            describe_target_group_attributes(target_group['TargetGroupArn'], **conn))
    return target_group_attributes


@registry.register(flag=FLAGS.TARGET_GROUP_HEALTH, depends_on=FLAGS.TARGET_GROUPS, key='target_group_health')
def _get_target_group_health(alb, **conn):
    target_group_health = list()
    for target_group in alb['target_groups']:
        target_group_health.extend(describe_target_health(target_group['TargetGroupArn'], **conn))
    return target_group_health


@registry.register(flag=FLAGS.BASE)
def get_base(alb, **conn):
    base_fields = frozenset(
        ['LoadBalancerArn', 'State', 'DNSName', 'CreatedTime', 'Scheme', 'Type', 'IpAddressType', 'VpcId',
         'CanonicalHostedZoneId', 'SecurityGroups', 'LoadBalancerName', 'AvailabilityZones'])
    needs_base = False

    for field in base_fields:
        if field not in alb:
            needs_base = True
            break

    if needs_base:
        if 'LoadBalancerName' in alb:
            alb = describe_load_balancers(names=[alb['LoadBalancerName']], **conn)
        elif 'LoadBalancerArn' in alb:
            alb = describe_load_balancers(arns=[alb['LoadBalancerArn']], **conn)
        alb = alb[0]

    if not isinstance(alb['CreatedTime'], basestring):
        alb['CreatedTime'] = str(alb['CreatedTime'])

    # Copy LoadBalancerArn to just Arn
    alb['Arn'] = alb.get('LoadBalancerArn')
    alb.update({
        '_version': 2,
        'region': conn.get('region')})
    return alb


@modify_output
def get_elbv2(alb, flags=FLAGS.ALL, **conn):
    """
    Fully describes an ALB (ELBv2).

    :param alb: Could be an ALB Name, ALB ARN, or a dictionary. Likely the return value from a previous call to describe_load_balancers. At a minimum, must contain a key titled 'LoadBalancerArn'.
    :param flags: Flags describing which sections should be included in the return value. Default is FLAGS.ALL.
    :return: Returns a dictionary describing the ALB with the fields described in the flags parameter.
    """
    # Python 2 and 3 support:
    try:
        basestring
    except NameError as _:
        basestring = str

    if isinstance(alb, basestring):
        from cloudaux.orchestration.aws.arn import ARN
        alb_arn = ARN(alb)
        if alb_arn.error:
            alb = dict(LoadBalancerName=alb)
        else:
            alb = dict(LoadBalancerArn=alb)

    return registry.build_out(flags, start_with=alb, pass_datastructure=True, **conn)
