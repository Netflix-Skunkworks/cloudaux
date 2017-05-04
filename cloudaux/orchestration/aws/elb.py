from cloudaux.aws.elb import *
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags


registry = FlagRegistry()
FLAGS = Flags('BASE', 'ATTRIBUTES', 'TAGS')


@registry.register(flag=FLAGS.ATTRIBUTES, key='attributes')
def get_attributes(load_balancer_name, **conn):
    return describe_load_balancer_attributes(load_balancer_name, **conn)


@registry.register(flag=FLAGS.TAGS, key='tags')
def get_tags(load_balancer_name, **conn):
    return describe_tags([load_balancer_name], **conn)


@registry.register(flag=FLAGS.BASE)
def get_base(load_balancer_name, **conn):
    load_balancer = describe_load_balancers(LoadBalancerNames=[load_balancer_name], **conn)
    load_balancer = load_balancer[0]
    load_balancer['CreatedTime'] = str(load_balancer['CreatedTime'])

    # Amazingly, boto3 does not return an ARN, so let's build it ourselves.
    arn = 'arn:aws:elasticloadbalancing:{region}:{account_id}:loadbalancer/{name}'
    arn = arn.format(
        region=conn.get('region'),
        account_id=conn.get('account_number'),
        name=load_balancer_name)

    load_balancer.update({
        'arn': arn,
        'region': conn.get('region'),
        '_version': 1
    })
    return load_balancer


@modify_output
def get_load_balancer(load_balancer_name, flags=FLAGS.ALL, **conn):
    return registry.build_out(flags, load_balancer_name, **conn)