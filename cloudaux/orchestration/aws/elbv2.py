from cloudaux.aws.elbv2 import *
from cloudaux.orchestration import modify
from cloudaux.orchestration.flag_registry import FlagRegistry, Flags


class ALBFlagRegistry(FlagRegistry):
    from collections import defaultdict
    r = defaultdict(list)


FLAGS = Flags('BASE', 'LISTENERS', 'RULES', 'ATTRIBUTES', 'TAGS',
    'TARGET_GROUPS', 'TARGET_GROUP_ATTRIBUTES', 'TARGET_GROUP_HEALTH')


@ALBFlagRegistry.register(flag=FLAGS.LISTENERS, key='listeners')
def get_listeners(alb, **conn):
    return describe_listeners(load_balancer_arn=alb['Arn'], **conn)


@ALBFlagRegistry.register(flag=FLAGS.RULES, depends_on=FLAGS.LISTENERS, key='rules')
def get_rules(alb, **conn):
    rules = list()
    for listener in alb['listeners']:
        rules.append(describe_rules(listener_arn=listener['ListenerArn'], **conn))
    return rules


@ALBFlagRegistry.register(flag=FLAGS.ATTRIBUTES, key='attributes')
def get_attributes(alb, **conn):
    return describe_load_balancer_attributes(alb['Arn'], **conn)


@ALBFlagRegistry.register(flag=FLAGS.TAGS, key='tags')
def get_tags(alb, **conn):
    return describe_tags([alb['Arn']], **conn)


@ALBFlagRegistry.register(flag=FLAGS.TARGET_GROUPS, key='target_groups')
def get_target_groups(alb, **conn):
    return describe_target_groups(load_balancer_arn=alb['Arn'], **conn)


@ALBFlagRegistry.register(flag=FLAGS.TARGET_GROUP_ATTRIBUTES, depends_on=FLAGS.TARGET_GROUPS, key='target_group_attributes')
def _get_target_group_attributes(alb, **conn):
    target_group_attributes = list()
    for target_group in alb['target_groups']:
        target_group_attributes.append(
            describe_target_group_attributes(target_group['TargetGroupArn'], **conn))
    return target_group_attributes


@ALBFlagRegistry.register(flag=FLAGS.TARGET_GROUP_HEALTH, depends_on=FLAGS.TARGET_GROUPS, key='target_group_health')
def _get_target_group_health(alb, **conn):
    target_group_health = list()
    for target_group in alb['target_groups']:
        target_group_health.append(describe_target_health(target_group['TargetGroupArn'], **conn))
    return target_group_health


@ALBFlagRegistry.register(flag=FLAGS.BASE)
def get_base(alb, **conn):
    return {
        '_version': 1,
        'region': conn.get('region')
    }


# TODO: As elbv2 has no list method, we should really be taking a dictionary
# as an input instead of the name.
def get_elbv2(alb_name, output='camelized', flags=FLAGS.ALL, **conn):
    result = describe_load_balancers(names=[alb_name], **conn)[0]
    result['CreatedTime'] = str(result['CreatedTime'])

    # Rename LoadBalancerArn to just Arn
    result['Arn'] = result['LoadBalancerArn']
    del result['LoadBalancerArn']

    ALBFlagRegistry.build_out(result, flags, result, **conn)
    return modify(result, format=output)