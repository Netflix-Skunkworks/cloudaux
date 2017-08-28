from cloudaux.aws.events import describe_rule
from cloudaux.aws.events import list_targets_by_rule
from cloudaux.aws.events_bus import describe_event_bus
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags

from botocore.exceptions import ClientError
import logging
import json


logger = logging.getLogger('cloudaux')


registry = FlagRegistry()
FLAGS = Flags('BASE', 'DESCRIBE')

@registry.register(flag=FLAGS.DESCRIBE)
def get_rule_description(rule_name, **conn):
    rule = describe_rule(Name=rule_name, **conn)

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
def get_base(rule_name, **conn):
    return {
        'arn': "arn:aws:events:{region}:{account}:rule/{name}".format(
            region=conn.get('region'),
            account=conn.get('account'),
            name=rule_name),
        'name': rule_name,
        'region': conn.get('region'),
        '_version': 1
    }

@modify_output
def get_event(rule_name, flags=FLAGS.ALL, **conn):
    """
    Orchestrates all the calls required to fully build out a CloudWatch Event Rule in the following format:

    {
        "Arn": ...,
        "Name": ...,
        "Region": ...,
        "Description": ...,
        "State": ...,
        "Rule": ...,
        "_version": 1
    }

    NOTE: "GrantReferences" is an ephemeral field that is not guaranteed to be consistent -- do not base logic off of it

    :param rule_name: str cloudwatch event name
    :param flags: By default, set to ALL fields
    :param conn: dict containing enough information to make a connection to the desired account.
    Must at least have 'assume_role' key.
    :return: dict containing a fully built out event rule with targets.
    """

    return registry.build_out(flags, rule_name, **conn)
