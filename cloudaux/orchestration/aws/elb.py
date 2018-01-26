from cloudaux.aws.elb import *
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags


registry = FlagRegistry()
FLAGS = Flags('BASE', 'ATTRIBUTES', 'TAGS', 'POLICIES', 'POLICY_TYPES')


def _reformat_policy(policy):
    """
    Policies returned from boto3 are massive, ugly, and difficult to read.
    This method flattens and reformats the policy.

    :param policy: Result from invoking describe_load_balancer_policies(...)
    :return: Returns a tuple containing policy_name and the reformatted policy dict.
    """
    policy_name = policy['PolicyName']
    ret = {}
    ret['type'] = policy['PolicyTypeName']
    attrs = policy['PolicyAttributeDescriptions']

    if ret['type'] != 'SSLNegotiationPolicyType':
        return policy_name, ret

    attributes = dict()
    for attr in attrs:
        attributes[attr['AttributeName']] = attr['AttributeValue']

    ret['protocols'] = dict()
    ret['protocols']['sslv2'] = bool(attributes.get('Protocol-SSLv2'))
    ret['protocols']['sslv3'] = bool(attributes.get('Protocol-SSLv3'))
    ret['protocols']['tlsv1'] = bool(attributes.get('Protocol-TLSv1'))
    ret['protocols']['tlsv1_1'] = bool(attributes.get('Protocol-TLSv1.1'))
    ret['protocols']['tlsv1_2'] = bool(attributes.get('Protocol-TLSv1.2'))
    ret['server_defined_cipher_order'] = bool(attributes.get('Server-Defined-Cipher-Order'))
    ret['reference_security_policy'] = attributes.get('Reference-Security-Policy', None)

    non_ciphers = [
        'Server-Defined-Cipher-Order',
        'Protocol-SSLv2',
        'Protocol-SSLv3',
        'Protocol-TLSv1',
        'Protocol-TLSv1.1',
        'Protocol-TLSv1.2',
        'Reference-Security-Policy'
    ]

    ciphers = []
    for cipher in attributes:
        if attributes[cipher] == 'true' and cipher not in non_ciphers:
            ciphers.append(cipher)

    ciphers.sort()
    ret['supported_ciphers'] = ciphers

    return policy_name, ret


def _flatten_listener(listener):
    """
    from

    {
      "Listener": {
        "InstancePort": 80,
        "LoadBalancerPort": 80,
        "Protocol": "HTTP",
        "InstanceProtocol": "HTTP"
      },
      "PolicyNames": []
    },

    to

    {
        "InstancePort": 80,
        "LoadBalancerPort": 80,
        "Protocol": "HTTP",
        "InstanceProtocol": "HTTP",
        "PolicyNames": []
    }
    """
    result = dict()
    if set(listener.keys()) == set(['Listener', 'PolicyNames']):
        result.update(listener['Listener'])
        result['PolicyNames'] = listener['PolicyNames']
    else:
        result = dict(listener)
    return result


@registry.register(flag=FLAGS.ATTRIBUTES, key='attributes')
def get_attributes(load_balancer, **conn):
    return describe_load_balancer_attributes(load_balancer['LoadBalancerName'], **conn)


@registry.register(flag=FLAGS.TAGS, key='tags')
def get_tags(load_balancer, **conn):
    return describe_tags([load_balancer['LoadBalancerName']], **conn)[0]['Tags']


@registry.register(flag=FLAGS.POLICIES, depends_on=FLAGS.BASE, key='policy_descriptions')
def get_policies(load_balancer, **conn):
    result = dict()
    policy_names = set()
    for listener in load_balancer['ListenerDescriptions']:
        listener_policy_names = listener['PolicyNames']
        policy_names = policy_names.union(set(listener_policy_names))

    descriptions = describe_load_balancer_policies(load_balancer['LoadBalancerName'], list(policy_names), **conn)
    for description in descriptions:
        policy_name, reformatted_policy = _reformat_policy(description)
        result[policy_name] = reformatted_policy
    return result


@registry.register(flag=FLAGS.POLICY_TYPES, depends_on=FLAGS.POLICIES, key='policy_type_descriptions')
def get_policy_types(load_balancer, **conn):
    policy_types = set()
    for policy_name, policy in load_balancer['policy_descriptions'].items():
        policy_types.add(policy['type'])

    return describe_load_balancer_policy_types(list(policy_types), **conn)


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

    listeners = load_balancer['ListenerDescriptions']
    new_listeners = list()
    for listener in listeners:
        new_listener = _flatten_listener(listener)
        new_listeners.append(new_listener)

    load_balancer['ListenerDescriptions'] = new_listeners

    # Amazingly, boto3 does not return an ARN, so let's build it ourselves.
    arn = 'arn:aws:elasticloadbalancing:{region}:{account_id}:loadbalancer/{name}'
    arn = arn.format(
        region=conn.get('region'),
        account_id=conn.get('account_number'),
        name=load_balancer['LoadBalancerName'])

    load_balancer.update({
        'arn': arn,
        'region': conn.get('region'),
        '_version': 2})
    return load_balancer


@modify_output
def get_load_balancer(load_balancer, flags=FLAGS.ALL ^ FLAGS.POLICY_TYPES, **conn):
    """
    Fully describes an ELB.

    :param loadbalancer: Could be an ELB Name or a dictionary. Likely the return value from a previous call to describe_load_balancers. At a minimum, must contain a key titled 'LoadBalancerName'.
    :param flags: Flags describing which sections should be included in the return value. Default is FLAGS.ALL minus FLAGS.POLICY_TYPES.
    :return: Returns a dictionary describing the ELB with the fields described in the flags parameter.
    """
    # Python 2 and 3 support:
    try:
        basestring
    except NameError as _:
        basestring = str

    if isinstance(load_balancer, basestring):
        load_balancer = dict(LoadBalancerName=load_balancer)

    return registry.build_out(flags, start_with=load_balancer, pass_datastructure=True, **conn)