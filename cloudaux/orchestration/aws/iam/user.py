from cloudaux import CloudAux
from cloudaux.aws.iam import get_user_inline_policies
from cloudaux.aws.iam import get_user_access_keys
from cloudaux.aws.iam import get_user_login_profile
from cloudaux.aws.iam import get_user_managed_policies
from cloudaux.aws.iam import get_user_mfa_devices
from cloudaux.aws.iam import get_user_signing_certificates
from cloudaux.orchestration.aws import _get_name_from_structure, _conn_from_args
from cloudaux.orchestration import modify
from cloudaux.orchestration.flag_registry import FlagRegistry
from bunch import Bunch


FLAGS=Bunch(
    ACCESS_KEYS=1,
    INLINE_POLICIES=2,
    MANAGED_POLICIES=4,
    MFA_DEVICES=8,
    LOGIN_PROFILE=16,
    SIGNING_CERTIFICATES=32,
    ALL=63)

class UserFlagRegistry(FlagRegistry):
    from collections import defaultdict
    r = defaultdict(list)


@UserFlagRegistry.register(flag=FLAGS.ACCESS_KEYS, key='access_keys')
def get_access_keys(user, **conn):
    return get_user_access_keys(user, **conn)


@UserFlagRegistry.register(flag=FLAGS.INLINE_POLICIES, key='inline_policies')
def get_inline_policies(user, **conn):
    return get_user_inline_policies(user, **conn)


@UserFlagRegistry.register(flag=FLAGS.MANAGED_POLICIES, key='managed_policies')
def get_managed_policies(user, **conn):
    return get_user_managed_policies(user, **conn)


@UserFlagRegistry.register(flag=FLAGS.MFA_DEVICES, key='mfa_devices')
def get_mfa_devices(user, **conn):
    return get_user_mfa_devices(user, **conn)


@UserFlagRegistry.register(flag=FLAGS.LOGIN_PROFILE, key='login_profile')
def get_login_profile(user, **conn):
    return get_user_login_profile(user, **conn)


@UserFlagRegistry.register(flag=FLAGS.SIGNING_CERTIFICATES, key='signing_certificates')
def get_signing_certificates(user, **conn):
    return get_user_signing_certificates(user, **conn)


def _get_base(user, **conn):
    base_fields = frozenset(['Arn', 'CreateDate', 'Path', 'UserId', 'UserName'])
    needs_base = False
    for field in base_fields:
        if field not in user:
            needs_base = True
            break

    if needs_base:
        user_name = _get_name_from_structure(user, 'UserName')
        user = CloudAux.go('iam.client.get_user', UserName=user_name, **conn)
        user = user['User']

    # cast CreateDate from a datetime to something JSON serializable.
    user.update(dict(CreateDate=str(user['CreateDate'])))
    if 'PasswordLastUsed' in user:
        user.update(dict(PasswordLastUsed=str(user['PasswordLastUsed'])))

    user['_version'] = 1
    return user


def get_user(user, output='camelized', flags=FLAGS.ALL, **conn):
    """
    Orchestrates all the calls required to fully build out an IAM User in the following format:

    {
        "Arn": ...,
        "AccessKeys": ...,
        "CreateDate": ...,  # str
        "InlinePolicies": ...,
        "ManagedPolicies": ...,
        "MFADevices": ...,
        "Path": ...,
        "UserId": ...,
        "UserName": ...,
        "SigningCerts": ...
    }

    :param user: dict containing (at the very least) arn or the combination of user_name and account_number
    :param output: Determines whether keys should be returned camelized or underscored.
    :param conn: dict containing enough information to make a connection to the desired account.
    Must at least have 'assume_role' key.
    :return: dict containing fully built out user.
    """
    user = modify(user, 'camelized')
    _conn_from_args(user, conn)
    user = _get_base(user, **conn)
    UserFlagRegistry.build_out(user, flags, user, **conn)
    return modify(user, format=output)
