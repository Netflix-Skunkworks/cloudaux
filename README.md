# cloudaux

[![Join the chat at https://gitter.im/Netflix-Skunkworks/cloudaux](https://badges.gitter.im/Netflix-Skunkworks/cloudaux.svg)](https://gitter.im/Netflix-Skunkworks/cloudaux?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[![Version](http://img.shields.io/pypi/v/cloudaux.svg?style=flat)](https://pypi.python.org/pypi/cloudaux/)

[![Build Status](https://travis-ci.com/Netflix-Skunkworks/cloudaux.svg?branch=master)](https://travis-ci.com/Netflix-Skunkworks/cloudaux)

[![Coverage Status](https://coveralls.io/repos/github/Netflix-Skunkworks/cloudaux/badge.svg?branch=master)](https://coveralls.io/github/Netflix-Skunkworks/cloudaux?branch=master)

Cloud Auxiliary is a python wrapper for interacting with AWS.

## SPECIAL NOTE:
All support for boto2 and OpenStack, and GCP have been removed in cloudaux 2.0+. This also removes most of the old AWS code and only leaves behind the decorators.
If you still need that, then pin to `cloudaux < 2.0`.

## NOTE: Python 2 Deprecation
Python 2 support has been dropped as of version 1.9.0. For projects that still require Python 2 support, please use the latest 1.8.x builds.

## Documentation

 - [CloudAux](README.md "CloudAux Readme") [THIS FILE]
 - [AWS](cloudaux/aws/README.md "Amazon Web Services Docs")

## Install

    pip install cloudaux

### AWS Example

    # Using the CloudAux class
    from cloudaux import CloudAux
    CloudAux.go('kms.client.list_aliases', **conn_details)

    ca = CloudAux(**conn_details)
    ca.call('kms.client.list_aliases')


    # directly asking for a boto3 connection:
    from cloudaux.aws.sts import boto3_cached_conn
    conn = boto3_cached_conn('ec2', **conn_details)


    # Over your entire environment:
    from cloudaux.decorators import iter_account_region

    accounts = ['000000000000', '111111111111']

    conn_details = {
        'assume_role': 'MyRole',
        'session_name': 'MySession',
        'conn_type': 'boto3'
    }

    @iter_account_region('kms', accounts=accounts, regions=['us-east-1'], **conn_details)
    def list_keys(conn=None):
        return conn.list_keys()['Keys']

    # If you want your role to be read-only, you can assume your role and add the read_only flag to connection details
    # to inherit the AWS ReadOnlyAccess policy. This flag defaults to False
    # The permissions from the role being assumed will be limited to Read and List only
    conn_details = {
        'account_number': '111111111111',
        'assume_role': 'MyRole',
        'session_name': 'MySession',
        'region': 'us-east-1',
        'read_only': True
    }

