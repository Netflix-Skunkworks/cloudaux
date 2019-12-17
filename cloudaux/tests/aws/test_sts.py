"""
.. module: cloudaux.tests.aws.test_sts
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Josafat Gonzalez <josafatg@netflix.com>
"""
from mock import patch
from cloudaux.aws.sts import boto3_cached_conn


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