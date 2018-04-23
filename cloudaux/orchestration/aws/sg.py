from cloudaux.aws.sg import describe_security_group
from cloudaux.decorators import modify_output
from cloudaux.orchestration.aws.arn import ARN
from flagpole import FlagRegistry, Flags
from six import string_types

registry = FlagRegistry()
FLAGS = Flags('BASE')


@registry.register(flag=FLAGS.BASE)
def _get_base(sg_obj, **conn):
    base_fields = ['Description', 'GroupName', 'IpPermissions', 'OwnerId', 'GroupId', 'IpPermissionsEgress', 'VpcId']

    if not all(field in sg_obj for field in base_fields):
        sg_obj = describe_security_group(sg_obj['GroupId'], **conn)

    sg_obj['_version'] = 1
    return sg_obj


@modify_output
def get_security_group(sg_obj, flags=FLAGS.ALL, **conn):
    """
    Orchestrates calls to build a Security Group in the following format:

    {
        "Description": ...,
        "GroupName": ...,
        "IpPermissions" ...,
        "OwnerId" ...,
        "GroupId" ...,
        "IpPermissionsEgress" ...,
        "VpcId" ...
    }
    Args:
        sg_obj: name, ARN, or dict of Security Group
        flags: Flags describing which sections should be included in the return value. Default ALL

    Returns:
        dictionary describing the requested Security Group
    """
    if isinstance(sg_obj, string_types):
        group_arn = ARN(sg_obj)
        if group_arn.error:
            sg_obj = {'GroupId': sg_obj}
        else:
            sg_obj = {'GroupId': group_arn.parsed_name}

    return registry.build_out(flags, sg_obj, **conn)
