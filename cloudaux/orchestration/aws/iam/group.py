"""
.. module: cloudaux.orchestration.aws.iam.group
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Mike Grima <mgrima@netflix.com>
"""
from cloudaux import get_iso_string
from cloudaux.aws.iam import get_group as get_group_api, list_group_policies, get_group_policy_document, \
    list_attached_group_managed_policies
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags

from cloudaux.orchestration import modify
from cloudaux.orchestration.aws import _conn_from_args
from cloudaux.orchestration.aws.iam import MissingFieldException

registry = FlagRegistry()
FLAGS = Flags('BASE', 'INLINE_POLICIES', 'MANAGED_POLICIES', 'USERS')


@registry.register(flag=FLAGS.INLINE_POLICIES, key='inline_policies')
def get_inline_policies(group, **conn):
    """Get the inline policies for the group."""
    policy_list = list_group_policies(group['GroupName'], **conn)

    policy_documents = {}

    for policy in policy_list:
        policy_documents[policy] = get_group_policy_document(group['GroupName'], policy, **conn)

    return policy_documents


@registry.register(flag=FLAGS.MANAGED_POLICIES, key='managed_policies')
def get_managed_policies(group, **conn):
    """Get a list of the managed policy names that are attached to the group."""
    managed_policies = list_attached_group_managed_policies(group['GroupName'], **conn)

    managed_policy_names = []

    for policy in managed_policies:
        managed_policy_names.append(policy['PolicyName'])

    return managed_policy_names


@registry.register(flag=FLAGS.USERS, key='users')
def get_users(group, **conn):
    """Gets a list of the usernames that are a part of this group."""
    group_details = get_group_api(group['GroupName'], **conn)

    user_list = []
    for user in group_details.get('Users', []):
        user_list.append(user['UserName'])

    return user_list


@registry.register(flag=FLAGS.BASE)
def _get_base(group, **conn):
    """Fetch the base IAM Group."""
    group['_version'] = 1

    # Get the initial group details (only needed if we didn't grab the users):
    group.update(get_group_api(group['GroupName'], users=False, **conn)['Group'])

    # Cast CreateDate from a datetime to something JSON serializable.
    group['CreateDate'] = get_iso_string(group['CreateDate'])
    return group


@modify_output
def get_group(group, flags=FLAGS.BASE | FLAGS.INLINE_POLICIES | FLAGS.MANAGED_POLICIES, **conn):
    """
    Orchestrates all the calls required to fully build out an IAM Group in the following format:

    {
        "Arn": ...,
        "GroupName": ...,
        "Path": ...,
        "GroupId": ...,
        "CreateDate": ...,  # str
        "InlinePolicies": ...,
        "ManagedPolicies": ...,  # These are just the names of the Managed Policies.
        "Users": ...,  # False by default -- these are just the names of the users.
        "_version": 1
    }

    :param flags: By default, Users is disabled. This is somewhat expensive as it has to call the `get_group` call
                  multiple times.
    :param group: dict MUST contain the GroupName and also a combination of either the ARN or the account_number.
    :param output: Determines whether keys should be returned camelized or underscored.
    :param conn: dict containing enough information to make a connection to the desired account.
                 Must at least have 'assume_role' key.
    :return: dict containing fully built out Group.
    """
    if not group.get('GroupName'):
        raise MissingFieldException('Must include GroupName.')

    group = modify(group, output='camelized')
    _conn_from_args(group, conn)
    return registry.build_out(flags, start_with=group, pass_datastructure=True, **conn)
