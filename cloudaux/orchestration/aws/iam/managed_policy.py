"""
.. module: cloudaux.orchestration.aws.iam.managed_policy
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Mike Grima <mgrima@netflix.com>
"""
from cloudaux import get_iso_string
from cloudaux.aws.iam import get_policy, get_managed_policy_document
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags

from cloudaux.orchestration.aws import _conn_from_args
from cloudaux.orchestration.aws import _get_name_from_structure
from cloudaux.orchestration.aws.iam import MissingFieldException

registry = FlagRegistry()
FLAGS = Flags('BASE')


@registry.register(flag=FLAGS.BASE)
def get_base(managed_policy, **conn):
    """Fetch the base Managed Policy.

    This includes the base policy and the latest version document.

    :param managed_policy:
    :param conn:
    :return:
    """
    managed_policy['_version'] = 1

    arn = _get_name_from_structure(managed_policy, 'Arn')
    policy = get_policy(arn, **conn)
    document = get_managed_policy_document(arn, policy_metadata=policy, **conn)

    managed_policy.update(policy['Policy'])
    managed_policy['Document'] = document

    # Fix the dates:
    managed_policy['CreateDate'] = get_iso_string(managed_policy['CreateDate'])
    managed_policy['UpdateDate'] = get_iso_string(managed_policy['UpdateDate'])

    return managed_policy


@modify_output
def get_managed_policy(managed_policy, flags=FLAGS.ALL, **conn):
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

    :param managed_policy: dict MUST contain the ARN.
    :param flags:
    :param conn:
    :return:
    """
    if not managed_policy.get('Arn'):
        raise MissingFieldException('Must include Arn.')

    _conn_from_args(managed_policy, conn)
    return registry.build_out(flags, start_with=managed_policy, pass_datastructure=True, **conn)
