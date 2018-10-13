"""
.. module: cloudaux.orchestration.aws.iam.managed_policy
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Mike Grima <mgrima@netflix.com>
"""
from cloudaux.aws.iam import get_policy, get_managed_policy_document
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags


registry = FlagRegistry()
FLAGS = Flags('BASE')


@registry.register(flag=FLAGS.BASE)
def get_base(policy_arn, **conn):
    """Fetch the base Managed Policy.

    This includes the base policy and the latest version document.

    :param policy_arn:
    :param conn:
    :return:
    """
    result = {
        '_version': 1
    }

    managed_policy = get_policy(policy_arn, **conn)
    document = get_managed_policy_document(policy_arn, policy_metadata=managed_policy, **conn)

    result.update(managed_policy['Policy'])
    result['Document'] = document

    # Fix the dates:
    result['CreateDate'] = result['CreateDate'].replace(tzinfo=None, microsecond=0).isoformat() + 'Z'
    result['UpdateDate'] = result['UpdateDate'].replace(tzinfo=None, microsecond=0).isoformat() + 'Z'

    return result


@modify_output
def get_managed_policy(policy_arn, flags=FLAGS.ALL, **conn):
    """
    Orchestrates all of the calls required to fully build out an IAM Managed Policy in the following format:

    {
        "Arn": "...",
        "PolicyName": "...",
        "PolicyId": "...",
        "Path": "...",
        "DefaultVersionId": "...",
        "AttachmentCount": 123,
        "PermissionsBoundaryUsageCount": 123,
        "IsAttachable": ...,
        "Description": "...",
        "CreateDate": "...",
        "UpdateDate": "...",
        "Document": "...",
        "_version": 1
    }

    :param policy_arn:
    :param flags:
    :param conn:
    :return:
    """
    return registry.build_out(flags, policy_arn, **conn)

