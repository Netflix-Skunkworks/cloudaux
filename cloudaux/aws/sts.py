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
from botocore.config import Config

CACHE = {}


def _conn_kwargs(region, role, retry_config):
    kwargs = dict(region_name=region)
    kwargs.update(dict(config=retry_config))
    if role:
        kwargs.update(dict(
            aws_access_key_id=role['Credentials']['AccessKeyId'],
            aws_secret_access_key=role['Credentials']['SecretAccessKey'],
            aws_session_token=role['Credentials']['SessionToken']
        ))

    return kwargs


def _client(service, region, role, retry_config, client_kwargs):
    return boto3.session.Session().client(
        service,
        **_conn_kwargs(region, role, retry_config),
        **client_kwargs,
    )


def _resource(service, region, role, retry_config, client_kwargs):
    return boto3.session.Session().resource(
        service,
        **_conn_kwargs(region, role, retry_config),
        **client_kwargs,
    )


def _get_cached_creds(key, service, service_type, region, future_expiration_minutes, return_credentials, client_config,
                      client_kwargs):
    role = CACHE[key]
    now = datetime.datetime.now(dateutil.tz.tzutc()) + datetime.timedelta(minutes=future_expiration_minutes)
    if role["Credentials"]["Expiration"] > now:
        if service_type == 'client':
            conn = _client(service, region, role, client_config, client_kwargs)
        else:
            conn = _resource(service, region, role, client_config, client_kwargs)

        if return_credentials:
            return conn, role

        return conn

    else:
        del CACHE[key]



def boto3_cached_conn(service, service_type='client', future_expiration_minutes=15, account_number=None,
                      assume_role=None, session_name='cloudaux', region='us-east-1', return_credentials=False,
                      external_id=None, arn_partition='aws', read_only=False, retry_max_attempts=10, config=None,
                      sts_client_kwargs=None, client_kwargs=None):
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
    :param arn_partition: Optional parameter to specify other aws partitions such as aws-us-gov for aws govcloud
    :param read_only: Optional parameter to specify the built in ReadOnlyAccess AWS policy
    :param retry_max_attempts: An integer representing the maximum number of retry attempts that will be made on a
        single request
    :param config: Optional botocore.client.Config
    :param sts_client_kwargs: Optional arguments to pass during STS client creation
    :return: boto3 client or resource connection
    """
    key = (
        account_number,
        assume_role,
        session_name,
        external_id,
        region,
        service_type,
        service,
        arn_partition,
        read_only
    )
    client_config = Config(retries=dict(max_attempts=retry_max_attempts))
    if not client_kwargs:
        client_kwargs = {}
    if config:
        client_config = client_config.merge(config)

    if key in CACHE:
        retval = _get_cached_creds(key, service, service_type, region, future_expiration_minutes, return_credentials, client_config, client_kwargs)
        if retval:
            return retval

    role = None
    if assume_role:
        sts_client_kwargs = sts_client_kwargs or {}
        sts = boto3.session.Session().client('sts', **sts_client_kwargs)

        # prevent malformed ARN
        if not all([account_number, assume_role]):
            raise ValueError("Account number and role to assume are both required")

        arn = 'arn:{partition}:iam::{0}:role/{1}'.format(
            account_number,
            assume_role,
            partition=arn_partition
        )

        assume_role_kwargs = {
            'RoleArn': arn,
            'RoleSessionName': session_name
        }

        if read_only:
            assume_role_kwargs['PolicyArns'] = [
                {
                    'arn': 'arn:aws:iam::aws:policy/ReadOnlyAccess'
                },
            ]

        if external_id:
            assume_role_kwargs['ExternalId'] = external_id

        role = sts.assume_role(**assume_role_kwargs)


    if service_type == 'client':
        conn = _client(service, region, role, client_config, client_kwargs)
    elif service_type == 'resource':
        conn = _resource(service, region, role, client_config, client_kwargs)

    if role:
        CACHE[key] = role

    if return_credentials:
        return conn, role['Credentials']

    return conn


def sts_conn(service, service_type='client', future_expiration_minutes=15, retry_max_attempts=10, config=None,
             sts_client_kwargs=None, client_kwargs=None):
    """
    This will wrap all calls with an STS AssumeRole if the required parameters are sent over.
    Namely, it requires the following in the kwargs:
    - Service Type (Required)
    - Account Number (Required for Assume Role)
    - IAM Role Name (Required for Assume Role)
    - Region (Optional, but recommended)
    - AWS Partition (Optional, defaults to 'aws' if none specified)
    - IAM Session Name (Optional, but recommended to appear in CloudTrail)
    - ReadOnly (Optional, but recommended if no write actions are being executed)

    If `force_client` is set to a boto3 client, then this will simply pass that in as the client.
    `force_client` is mostly useful for mocks and tests.
    :param service:
    :param service_type:
    :param retry_max_attempts: An integer representing the maximum number of retry attempts that will be made on a
        single request
    :param sts_client_kwargs: Optional arguments to pass during STS client creation
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
                    region=kwargs.pop('region', 'us-east-1'),
                    arn_partition=kwargs.pop('arn_partition', 'aws'),
                    read_only=kwargs.pop('read_only', False),
                    retry_max_attempts=kwargs.pop('retry_max_attempts', retry_max_attempts),
                    config=config,
                    sts_client_kwargs=kwargs.pop("sts_client_kwargs", None),
                    client_kwargs=kwargs.pop("client_kwargs", None),
                )
            return f(*args, **kwargs)
        return decorated_function
    return decorator
