from cloudaux import CloudAux
from cloudaux.aws.iam import get_role_managed_policies, get_role_inline_policies, get_role_instance_profiles, \
    get_account_authorization_details
from cloudaux.orchestration.aws import _get_name_from_structure, _conn_from_args
from cloudaux.orchestration import modify
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags


registry = FlagRegistry()
FLAGS = Flags('BASE', 'MANAGED_POLICIES', 'INLINE_POLICIES', 'INSTANCE_PROFILES')


@registry.register(flag=FLAGS.MANAGED_POLICIES, key='managed_policies')
def get_managed_policies(role, **conn):
    return get_role_managed_policies(role, **conn)


@registry.register(flag=FLAGS.INLINE_POLICIES, key='inline_policies')
def get_inline_policies(role, **conn):
    return get_role_inline_policies(role, **conn)


@registry.register(flag=FLAGS.INSTANCE_PROFILES, key='instance_profiles')
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
    role.update(dict(CreateDate=str(role['CreateDate'])))
    role['_version'] = 1

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
    Returns a List of Roles respresented as dictionary below:

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
                'CreateDate': str(role['CreateDate']),  # str
                'InlinePolicies': role['RolePolicyList'],
                'InstanceProfiles': [{
                                        'path': ip['Path'],
                                        'instance_profile_name': ip['InstanceProfileName'],
                                        'create_date': ip['CreateDate'].strftime('%Y-%m-%dT%H:%M:%SZ'),
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
