"""
.. module: cloudaux.aws.sts
    :platform: Unix
    :copyright: (c) 2015 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Patrick Kelley <patrick@netflix.com>
"""
from functools import wraps
import boto3
import dateutil.tz
import datetime

from cloudaux.aws.decorators import rate_limited

CACHE = {}


def _conn_kwargs(region, role):
    kwargs = dict(region_name=region)

    if role:
        kwargs.update(dict(
            aws_access_key_id=role['Credentials']['AccessKeyId'],
            aws_secret_access_key=role['Credentials']['SecretAccessKey'],
            aws_session_token=role['Credentials']['SessionToken']
        ))

    return kwargs


def _client(service, region, role):
    return boto3.session.Session().client(
        service,
        **_conn_kwargs(region, role)
    )


def _resource(service, region, role):
    return boto3.session.Session().resource(
        service,
        **_conn_kwargs(region, role)
    )


def _get_cached_creds(key, service, service_type, region, future_expiration_minutes, return_credentials):
    role = CACHE[key]
    now = datetime.datetime.now(dateutil.tz.tzutc()) + datetime.timedelta(minutes=future_expiration_minutes)
    if role["Credentials"]["Expiration"] > now:
        if service_type == 'client':
            conn = _client(service, region, role)
        else:
            conn = _resource(service, region, role)

        if return_credentials:
            return conn, role

        return conn

    else:
        del CACHE[key]


@rate_limited()
def boto3_cached_conn(service, service_type='client', future_expiration_minutes=15, account_number=None,
                      assume_role=None, session_name='cloudaux', region='us-east-1', return_credentials=False,
                      external_id=None):
    """
    Used to obtain a boto3 client or resource connection.
    For cross account, provide both account_number and assume_role.

    :usage:

    # Same Account:
    client = boto3_cached_conn('iam')
    resource = boto3_cached_conn('iam', service_type='resource')

    # Cross Account Client:
    client = boto3_cached_conn('iam', account_number='000000000000', assume_role='role_name')

    # Cross Account Resource:
    resource = boto3_cached_conn('iam', service_type='resource', account_number='000000000000', assume_role='role_name')

    :param service: AWS service (i.e. 'iam', 'ec2', 'kms')
    :param service_type: 'client' or 'resource'
    :param future_expiration_minutes: Connections will expire from the cache
        when their expiration is within this many minutes of the present time. [Default 15]
    :param account_number: Required if assume_role is provided.
    :param assume_role:  Name of the role to assume into for account described by account_number.
    :param session_name: Session name to attach to requests. [Default 'cloudaux']
    :param region: Region name for connection. [Default us-east-1]
    :param return_credentials: Indicates if the STS credentials should be returned with the client [Default False]
    :param external_id: Optional external id to pass to sts:AssumeRole.
        See https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user_externalid.html
    :return: boto3 client or resource connection
    """
    key = (
        account_number,
        assume_role,
        session_name,
        external_id,
        region,
        service_type,
        service)

    if key in CACHE:
        retval = _get_cached_creds(key, service, service_type, region, future_expiration_minutes, return_credentials)
        if retval:
            return retval

    role = None
    if assume_role:
        sts = boto3.session.Session().client('sts')

        # prevent malformed ARN
        if not all([account_number, assume_role]):
            raise ValueError("Account number and role to assume are both required")

        arn = 'arn:aws:iam::{0}:role/{1}'.format(
            account_number,
            assume_role
        )

        assume_role_kwargs = {
            'RoleArn': arn,
            'RoleSessionName': session_name
        }

        if external_id:
            assume_role_kwargs['ExternalId'] = external_id

        role = sts.assume_role(**assume_role_kwargs)

    if service_type == 'client':
        conn = _client(service, region, role)
    elif service_type == 'resource':
        conn = _resource(service, region, role)

    if role:
        CACHE[key] = role

    if return_credentials:
        return conn, role['Credentials']

    return conn


def sts_conn(service, service_type='client', future_expiration_minutes=15):
    """
    This will wrap all calls with an STS AssumeRole if the required parameters are sent over.
    Namely, it requires the following in the kwargs:
    - Service Type (Required)
    - Account Number (Required for Assume Role)
    - IAM Role Name (Required for Assume Role)
    - Region (Optional, but recommended)
    - IAM Session Name (Optional, but recommended to appear in CloudTrail)

    If `force_client` is set to a boto3 client, then this will simply pass that in as the client.
    `force_client` is mostly useful for mocks and tests.
    :param service:
    :param service_type:
    :param future_expiration_minutes:
    :return:
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if kwargs.get("force_client"):
                kwargs[service_type] = kwargs.pop("force_client")
                kwargs.pop("account_number", None)
                kwargs.pop("region", None)
            else:
                kwargs[service_type] = boto3_cached_conn(
                    service,
                    service_type=service_type,
                    future_expiration_minutes=future_expiration_minutes,
                    account_number=kwargs.pop('account_number', None),
                    assume_role=kwargs.pop('assume_role', None),
                    session_name=kwargs.pop('session_name', 'cloudaux'),
                    external_id=kwargs.pop('external_id', None),
                    region=kwargs.pop('region', 'us-east-1'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
