from cloudaux.aws.events import describe_rule
from cloudaux.aws.events import list_targets_by_rule
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags


registry = FlagRegistry()
FLAGS = Flags('BASE', 'DESCRIBE', 'TARGETS')


@registry.register(flag=FLAGS.TARGETS, key='targets')
def list_targets(rule, **conn):
    return list_targets_by_rule(Rule=rule['name'], **conn)


@registry.register(flag=FLAGS.DESCRIBE)
def get_rule_description(rule, **conn):
    rule = describe_rule(Name=rule['name'], **conn)

    rule_detail = None

    if rule.get('ScheduleExpression', None):
        rule_detail = rule['ScheduleExpression']
    else:
        rule_detail = rule['EventPattern']

    return {
        'description': rule['Description'],
        'state': rule['State'],
        'rule': rule_detail
    }


@registry.register(flag=FLAGS.BASE)
def get_base(rule, **conn):
    return {
        'arn': "arn:aws:events:{region}:{account}:rule/{name}".format(
            region=conn.get('region'),
            account=conn.get('account'),
            name=rule['name']),
        'name': rule['name'],
        'region': conn.get('region'),
        '_version': 1
    }


@modify_output
def get_event(rule, flags=FLAGS.ALL, **conn):
    """
    Orchestrates all the calls required to fully build out a CloudWatch Event Rule in the following format:

    {
        "Arn": ...,
        "Name": ...,
        "Region": ...,
        "Description": ...,
        "State": ...,
        "Rule": ...,
        "Targets" ...,
        "_version": 1
    }

    :param rule: str cloudwatch event name
    :param flags: By default, set to ALL fields
    :param conn: dict containing enough information to make a connection to the desired account.
    Must at least have 'assume_role' key.
    :return: dict containing a fully built out event rule with targets.
    """
    # If STR is passed in, determine if it's a name or ARN and built a dict.
    if isinstance(rule, basestring):
        rule_arn = ARN(rule)
        if rule_arn.error:
            rule = dict(name=rule)
        else:
            rule = dict(name=rule_arn.name, arn=rule)

    return registry.build_out(flags, rule, **conn)
