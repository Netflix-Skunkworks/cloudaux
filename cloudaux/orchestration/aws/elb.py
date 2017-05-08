from cloudaux.aws.elb import *
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags


registry = FlagRegistry()
FLAGS = Flags('BASE', 'ATTRIBUTES', 'TAGS')


@registry.register(flag=FLAGS.ATTRIBUTES, key='attributes')
def get_attributes(load_balancer, **conn):
    return describe_load_balancer_attributes(load_balancer['LoadBalancerName'], **conn)


@registry.register(flag=FLAGS.TAGS, key='tags')
def get_tags(load_balancer, **conn):
    return describe_tags([load_balancer['LoadBalancerName']], **conn)


@registry.register(flag=FLAGS.BASE)
def get_base(load_balancer, **conn):
    base_fields = frozenset(['Subnets', 'CanonicalHostedZoneNameID', 'CanonicalHostedZoneName', 'ListenerDescriptions', 'HealthCheck', 'VPCId', 'BackendServerDescriptions', 'Instances', 'DNSName', 'SecurityGroups', 'Policies', 'LoadBalancerName', 'CreatedTime', 'AvailabilityZones', 'Scheme', 'SourceSecurityGroup'])
    needs_base = False

    for field in base_fields:
        if field not in load_balancer:
            needs_base = True
            break

    if needs_base:
        load_balancer = describe_load_balancers(LoadBalancerNames=[load_balancer['LoadBalancerName']], **conn)
        load_balancer = load_balancer[0]

    if not isinstance(load_balancer['CreatedTime'], basestring):
        load_balancer['CreatedTime'] = str(load_balancer['CreatedTime'])

    # Amazingly, boto3 does not return an ARN, so let's build it ourselves.
    arn = 'arn:aws:elasticloadbalancing:{region}:{account_id}:loadbalancer/{name}'
    arn = arn.format(
        region=conn.get('region'),
        account_id=conn.get('account_number'),
        name=load_balancer['LoadBalancerName'])

    load_balancer.update({
        'arn': arn,
        'region': conn.get('region'),
        '_version': 1})
    return load_balancer


@modify_output
def get_load_balancer(load_balancer, flags=FLAGS.ALL, **conn):
    """
    Fully describes an ELB.

    :param loadbalancer: Could be an ELB Name or a dictionary. Likely the return value from a previous call to describe_load_balancers. At a minimum, must contain a key titled 'LoadBalancerName'.
    :param flags: Flags describing which sections should be included in the return value. Default is FLAGS.ALL.
    :return: Returns a dictionary describing the ELB with the fields described in the flags parameter.
    """

    if isinstance(load_balancer, basestring):
        load_balancer = dict(LoadBalancerName=load_balancer)

    return registry.build_out(flags, load_balancer, **conn)