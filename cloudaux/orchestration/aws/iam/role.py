"""
.. module: cloudaux.orchestration.aws.iam.role
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Patrick Kelley <pkelley@netflix.com> @monkeysecurity
.. moduleauthor:: Will Bengtson <wbengtson@netflix.com>
"""
from cloudaux import CloudAux, get_iso_string
from cloudaux.aws.iam import get_role_managed_policies, get_role_inline_policies, get_role_instance_profiles, \
    get_account_authorization_details, list_role_tags
from cloudaux.orchestration.aws import _get_name_from_structure, _conn_from_args
from cloudaux.orchestration import modify
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags


registry = FlagRegistry()
FLAGS = Flags('BASE', 'MANAGED_POLICIES', 'INLINE_POLICIES', 'INSTANCE_PROFILES', 'TAGS')


@registry.register(flag=FLAGS.TAGS, depends_on=FLAGS.BASE, key='tags')
def get_tags(role, **conn):
    tags = list_role_tags(role, **conn)
    # AWS Returns a funky format for tags:
    # [{
    #    "Key": "owner",
    #    "Value": "bandersnatch"
    # }]

    # reformat into a single dict.
    # { "owner": "bandersnatch" }
    return {t.get('Key'): t.get('Value') for t in tags}


@registry.register(flag=FLAGS.MANAGED_POLICIES, depends_on=FLAGS.BASE, key='managed_policies')
def get_managed_policies(role, **conn):
    return get_role_managed_policies(role, **conn)


@registry.register(flag=FLAGS.INLINE_POLICIES, depends_on=FLAGS.BASE, key='inline_policies')
def get_inline_policies(role, **conn):
    return get_role_inline_policies(role, **conn)


@registry.register(flag=FLAGS.INSTANCE_PROFILES, depends_on=FLAGS.BASE, key='instance_profiles')
def get_instance_profiles(role, **conn):
    return get_role_instance_profiles(role, **conn)


@registry.register(flag=FLAGS.BASE)
def _get_base(role, **conn):
    """
    Determine whether the boto get_role call needs to be made or if we already have all that data
    in the role object.
    :param role: dict containing (at the very least) role_name and/or arn.
    :param conn: dict containing enough information to make a connection to the desired account.
    :return: Camelized dict describing role containing all all base_fields.
    """
    base_fields = frozenset(['Arn', 'AssumeRolePolicyDocument', 'Path', 'RoleId', 'RoleName', 'CreateDate'])
    needs_base = False

    for field in base_fields:
        if field not in role:
            needs_base = True
            break

    if needs_base:
        role_name = _get_name_from_structure(role, 'RoleName')
        role = CloudAux.go('iam.client.get_role', RoleName=role_name, **conn)
        role = role['Role']

    # cast CreateDate from a datetime to something JSON serializable.
    role.update(dict(CreateDate=get_iso_string(role['CreateDate'])))
    role['_version'] = 3

    return role


@modify_output
def get_role(role, flags=FLAGS.ALL, **conn):
    """
    Orchestrates all the calls required to fully build out an IAM Role in the following format:

    {
        "Arn": ...,
        "AssumeRolePolicyDocument": ...,
        "CreateDate": ...,  # str
        "InlinePolicies": ...,
        "InstanceProfiles": ...,
        "ManagedPolicies": ...,
        "Path": ...,
        "RoleId": ...,
        "RoleName": ...,
        "Tags": {},
        "_version": 3
    }

    :param role: dict containing (at the very least) role_name and/or arn.
    :param output: Determines whether keys should be returned camelized or underscored.
    :param conn: dict containing enough information to make a connection to the desired account.
    Must at least have 'assume_role' key.
    :return: dict containing a fully built out role.
    """
    role = modify(role, output='camelized')
    _conn_from_args(role, conn)
    return registry.build_out(flags, start_with=role, pass_datastructure=True, **conn)


def get_all_roles(**conn):
    """
    Returns a List of Roles represented as the dictionary below:

    {
        "Arn": ...,
        "AssumeRolePolicyDocument": ...,
        "CreateDate": ...,  # str
        "InlinePolicies": ...,
        "InstanceProfiles": ...,
        "ManagedPolicies": ...,
        "Path": ...,
        "RoleId": ...,
        "RoleName": ...,
    }

    :param conn: dict containing enough information to make a connection to the desired account.
    :return: list containing dicts or fully built out roles
    """

    roles = []
    account_roles = get_account_authorization_details('Role', **conn)

    for role in account_roles:
        roles.append(
            {
                'Arn': role['Arn'],
                'AssumeRolePolicyDocument': role['AssumeRolePolicyDocument'],
                'CreateDate': get_iso_string(role['CreateDate']),
                'InlinePolicies': role['RolePolicyList'],
                'InstanceProfiles': [{
                                        'path': ip['Path'],
                                        'instance_profile_name': ip['InstanceProfileName'],
                                        'create_date': get_iso_string(ip['CreateDate']),
                                        'instance_profile_id': ip['InstanceProfileId'],
                                        'arn': ip['Arn']
                                    } for ip in role['InstanceProfileList']],
                'ManagedPolicies': [
                    {
                      "name": x['PolicyName'],
                      "arn": x['PolicyArn']
                    } for x in role['AttachedManagedPolicies']
                ],
                'Path': role['Path'],
                'RoleId': role['RoleId'],
                'RoleName': role['RoleName']
            }
        )

    return roles
