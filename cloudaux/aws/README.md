# cloudaux AWS support

Cloud Auxiliary has support for Amazon Web Services.

## Documentation

 - [CloudAux](../../README.md "CloudAux Readme")
 - [AWS](README.md "Amazon Web Services Docs") [THIS FILE]

## Features

 - intelligent connection caching.
 - handles pagination for certain client methods.
 - multi-account sts:assumerole abstraction.

## Install

    pip install cloudaux

## Example

    # Define assume role session details:
    conn_details = {
        'account_number': '111111111111',
        'assume_role': 'MyRole',
        'session_name': 'MySession',
        'region': 'us-east-1'
    }
    
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
