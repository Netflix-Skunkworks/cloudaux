"""
.. module: cloudaux.tests.aws.test_sts
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Josafat Gonzalez <josafatg@netflix.com>
"""
from botocore.client import Config
from cloudaux.aws.sts import boto3_cached_conn
from mock import patch


def test_boto3_cached_conn_read_only():
    # Arrange
    conn_details = {
        'account_number': '111111111111',
        'assume_role': 'role_one',
        'region': 'us-east-1',
        'read_only': True
    }

    with patch('boto3.session.Session.client'):

        # Act
        conn = boto3_cached_conn('s3', **conn_details)

        # Assert
        assert 'PolicyArns' in conn.assume_role.call_args.kwargs


def test_boto3_cached_conn_default():
    # Arrange
    conn_details = {
        'account_number': '111111111111',
        'assume_role': 'role_one',
        'region': 'us-east-1'
    }

    with patch('boto3.session.Session.client'):

        # Act
        conn = boto3_cached_conn('s3', **conn_details)

        # Assert
        assert 'PolicyArns' not in conn.assume_role.call_args.kwargs


def test_boto3_cached_conn_retry_config(sts):
    from cloudaux.aws.sts import _client
    import cloudaux.aws.sts

    def mock_client(*args, **kwargs):
        with patch('boto3.session.Session') as p:
            _client(*args, **kwargs)

        return p

    # With the default:
    with patch('cloudaux.aws.sts._client', mock_client):
        conn = boto3_cached_conn('s3')
        assert conn.mock_calls[1].kwargs['config'].retries == {'max_attempts': 10}
        cloudaux.aws.sts.CACHE = {}

    # With STS role assumption:
    conn_details = {
        'account_number': '111111111111',
        'assume_role': 'role_one',
        'region': 'us-east-1'
    }
    with patch('cloudaux.aws.sts._client', mock_client):
        conn = boto3_cached_conn('s3', **conn_details)
        assert conn.mock_calls[1].kwargs['config'].retries == {'max_attempts': 10}
        cloudaux.aws.sts.CACHE = {}

    # With a specified retry Config:
    with patch('cloudaux.aws.sts._client', mock_client):
        conn = boto3_cached_conn('s3', retry_max_attempts=1000)
        assert conn.mock_calls[1].kwargs['config'].retries == {'max_attempts': 1000}
        cloudaux.aws.sts.CACHE = {}

    # With STS role assumption:
    conn_details['retry_max_attempts'] = 1000
    with patch('cloudaux.aws.sts._client', mock_client):
        conn = boto3_cached_conn('s3', **conn_details)
        assert conn.mock_calls[1].kwargs['config'].retries == {'max_attempts': 1000}
        cloudaux.aws.sts.CACHE = {}

def test_boto3_cached_conn_config(sts):
    from cloudaux.aws.sts import _client
    import cloudaux.aws.sts

    def mock_client(*args, **kwargs):
        with patch('boto3.session.Session') as p:
            _client(*args, **kwargs)

        return p

    # With the default:
    with patch('cloudaux.aws.sts._client', mock_client):
        conn = boto3_cached_conn('s3', config=Config(signature_version='s3v4'))
        assert conn.mock_calls[1].kwargs['config'].signature_version == 's3v4'
        cloudaux.aws.sts.CACHE = {}

    # With STS role assumption:
    conn_details = {
        'account_number': '111111111111',
        'assume_role': 'role_one',
        'region': 'us-east-1'
    }
    with patch('cloudaux.aws.sts._client', mock_client):
        conn = boto3_cached_conn('s3', config=Config(signature_version='s3v4'), **conn_details)
        assert conn.mock_calls[1].kwargs['config'].signature_version == 's3v4'
        cloudaux.aws.sts.CACHE = {}
