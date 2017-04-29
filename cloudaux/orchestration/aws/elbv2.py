from cloudaux.aws.elbv2 import *
from cloudaux.orchestration import modify
from cloudaux.orchestration.flag_registry import FlagRegistry, Flags


class ALBFlagRegistry(FlagRegistry):
    from collections import defaultdict
    r = defaultdict(list)


FLAGS = Flags('BASE', 'LISTENERS', 'ATTRIBUTES', 'TAGS')


@ALBFlagRegistry.register(flag=FLAGS.LISTENERS, key='listeners')
def get_listeners(arn, **conn):
    return describe_listeners(load_balancer_arn=arn, **conn)


@ALBFlagRegistry.register(flag=FLAGS.ATTRIBUTES, key='attributes')
def get_attributes(arn, **conn):
    return describe_load_balancer_attributes(arn, **conn)


@ALBFlagRegistry.register(flag=FLAGS.TAGS, key='tags')
def get_tags(arn, **conn):
    return describe_tags([arn], **conn)


@ALBFlagRegistry.register(flag=FLAGS.BASE)
def get_base(alb_name, **conn):
    return {
        '_version': 1,
        'region': conn.get('region')
    }


def get_elbv2(alb_name, output='camelized', flags=FLAGS.ALL, **conn):
    result = describe_load_balancers(names=[alb_name], **conn)[0]
    result['CreatedTime'] = str(result['CreatedTime'])

    # Rename LoadBalancerArn to just Arn
    alb_arn = result['LoadBalancerArn']
    result['Arn'] = alb_arn
    del result['LoadBalancerArn']

    ALBFlagRegistry.build_out(result, flags, alb_arn, **conn)
    return modify(result, format=output)