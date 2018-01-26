# cloudaux

[![Join the chat at https://gitter.im/Netflix-Skunkworks/cloudaux](https://badges.gitter.im/Netflix-Skunkworks/cloudaux.svg)](https://gitter.im/Netflix-Skunkworks/cloudaux?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[![Version](http://img.shields.io/pypi/v/cloudaux.svg?style=flat)](https://pypi.python.org/pypi/cloudaux/)

[![Build Status](https://travis-ci.org/Netflix-Skunkworks/cloudaux.svg?branch=master)](https://travis-ci.org/Netflix-Skunkworks/cloudaux)

[![Coverage Status](https://coveralls.io/repos/github/Netflix-Skunkworks/cloudaux/badge.svg?branch=master)](https://coveralls.io/github/Netflix-Skunkworks/cloudaux?branch=master)

Cloud Auxiliary is a python wrapper and orchestration module for interacting with cloud providers.

## Documentation

 - [CloudAux](README.md "CloudAux Readme") [THIS FILE]
 - [AWS](cloudaux/aws/README.md "Amazon Web Services Docs")
 - [GCP](cloudaux/gcp/README.md "Google Cloud Platform Docs")
 - [OpenStack](cloudaux/openstack/README.md "OpenStack Docs")

## Features

AWS:
 - intelligent connection caching.
 - handles pagination for certain client methods.
 - rate limit handling, with exponential backoff.
 - multi-account sts:assumerole abstraction.
 - orchestrates all the calls required to fully describe an item.
 - control which attributes are returned with flags.

GCP:
 - choosing the best client based on service
 - client caching
 - general caching and stats decorators available
 - basic support for non-specified discovery-API services
 - control which attributes are returned with flags.

OpenStack:
 - intelligent connection caching.
 - generalized OpenStack SDK generator usage.
 - orchestrates all the calls required to fully describe an item.
 - control which attributes are returned flags.

## Orchestration Supported Technologies

AWS:
 - IAM Role
 - IAM User
 - IAM SAML Provider
 - [S3](cloudaux/orchestration/aws/s3.md)
 - ELB (v1)
 - ELBv2 (ALB)
 - [Lambda Functions](cloudaux/orchestration/aws/lambda_function.md)
 - [Glacier](cloudaux/orchestration/aws/glacier.md)
 - [EC2 Image](cloudaux/orchestration/aws/image.md)
 - [Cloudwatch Events](cloudaux/orchestration/aws/events.md)
 - [SQS](cloudaux/orchestration/aws/sqs.md)

GCP:
 - IAM Service Accounts
 - Network/Subnetworks
 - Storage Buckets

OpenStack:
 - Network/Subnet
 - Floating IP/Router/Port
 - User
 - Instance/Image
 - Load Balancer
 - Object Storage Container

## Install

    pip install cloudaux

For GCP support run:

    pip install cloudaux\[gcp\]

For OpenStack support run:

    pip install cloudaux\[openstack\]

## Examples



### AWS Example

    # Using wrapper methods:
    from cloudaux.aws.sqs import get_queue, get_messages
    conn_details = {
        'account_number': '111111111111',
        'assume_role': 'MyRole',
        'session_name': 'MySession',
        'region': 'us-east-1'
    }
    queue = get_queue(queue_name='MyQueue', **conn_details)
    messages = get_messages(queue=queue)

    
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

### GCP Example

    # directly asking for a client:
    from cloudaux.aws.gcp.auth import get_client
    client = get_client('gce', **conn_details)
   
    # Over your entire environment:
    from cloudaux.gcp.decorators import iter_project
   
    projects = ['my-project-one', 'my-project-two']

    # To specify per-project key_files, you can do thie following:
    # projects = [
    #  {'project': 'my-project-one', key_file='/path/to/project-one.json'},
    #  {'project': 'my-project-two', key_file='/path/to/project-two.json'}
    # ]
    #
    # To specify a single key_file for all projects, use the key_file argument
    # to the decorator
    # @iter_project(projects=projects, key_file='/path/to/key.json')
    #
    # To use default credentials, omit the key_file argument
    # @iter_project(projects=projects)
    
    from cloudaux.gcp.iam import list_serviceaccounts
    from cloudaux.orchestration.gcp.iam.serviceaccount import get_serviceaccount_complete
    
    @iter_project(projects=projects, key_file='/path/to/key.json')
    def test_iter(**kwargs):
       accounts = list_serviceaccounts(**kwargs)
       ret = []
       for account in accounts:
         ret.append(get_serviceaccount_complete(service_account=account['name']))
       return ret

### OpenStack Example

    from cloudaux.openstack.decorators import _connect
    conn = _connect(cloud_name, region, yaml_file):

    # Over your entire environment:
    from cloudaux.openstack.decorators import iter_account_region, get_regions

    @iter_account_region(account_regions=get_regions())
    def list_networks(conn=None, service='network', generator='security_groups'):
        from cloudaux.openstack.utils import list_items
        list_items(**kwargs)

## Orchestration Example

### AWS IAM Role

    from cloudaux.orchestration.aws.iam.role import get_role, FLAGS
    
    # account_number may be extracted from the ARN of the role passed to get_role
    # if not included in conn.
    conn = dict(
        assume_role='SecurityMonkey',  # or whichever role you wish to assume into
        session_name='cloudaux',
        region='us-east-1'
    )

    role = get_role(
        dict(arn='arn:aws:iam::000000000000:role/myRole', role_name='myRole'),
        output='camelized',  # optional: {camelized underscored}
        flags=FLAGS.ALL,  # optional
        **conn)

    # The flags parameter is optional but allows the user to indicate that 
    # only a subset of the full item description is required.
    # IAM Role Flag Options:
    #   BASE, MANAGED_POLICIES, INLINE_POLICIES, INSTANCE_PROFILES, ALL (default)
    # For instance: flags=FLAGS.MANAGED_POLICIES | FLAGS.INSTANCE_PROFILES

    # cloudaux makes a number of calls to obtain a full description of the role
    print(json.dumps(role, indent=4, sort_keys=True))

    {
        "Arn": ...,
        "AssumeRolePolicyDocument": ...,
        "CreateDate": ...,  # str
        "InlinePolicies": ...,
        "InstanceProfiles": ...,
        "ManagedPolicies": ...,
        "Path": ...,
        "RoleId": ...,
        "RoleName": ...,
        "_version": 1    # Orchestration results return a _Version
    }
    
### GCP IAM Service Account

    from cloudaux.orchestration.gcp.iam.serviceaccount import get_serviceaccount_complete, FLAGS
    sa_name = 'projects/my-project-one/serviceAccounts/service-account-key@my-project-one.iam.gserviceaccount.com'
    sa = get_serviceaccount_complete(sa_name, flags=FLAGS.ALL, **conn_details)
    print(json.dumps(sa, indent=4, sort_keys=True))

    # Flag options for Service Accounts are BASE, KEYS, POLICY, ALL (default).
    
    {
      "DisplayName": "service-account", 
      "Email": "service-account@my-project-one.iam.gserviceaccount.com", 
      "Etag": "BwUzTDvWgHw=", 
      "Keys": [
          {
              "KeyAlgorithm": "KEY_ALG_RSA_2048", 
              "Name": "projects/my-project-one/serviceAccounts/service-account@my-project-one.iam.gserviceaccount.com/keys/8be0096886f6ed5cf51abb463d3448c8aee6c6b6", 
              "ValidAfterTime": "2016-06-30T18:26:45Z", 
              "ValidBeforeTime": "2026-06-28T18:26:45Z"
          }, 
 	  ...
      ], 
      "Name": "projects/my-project-one/serviceAccounts/service-account@my-project-one.iam.gserviceaccount.com", 
      "Oauth2ClientId": "115386704809902483492", 
      "Policy": [
          {
              "Members": [
                  "user:test-user@gmail.com"
              ], 
              "Role": "roles/iam.serviceAccountActor"
          }
      ], 
      "ProjectId": "my-project-one", 
      "UniqueId": "115386704809902483492"
    }

### OpenStack Security Group

    from cloudaux.orchestration.openstack.security_group import get_security_group, FLAGS

    secgroup = get_security_group(result, flags=flags, **kwargs)

    # The flags parameter is optional but allows the user to indicate that
    # only a subset of the full item description is required.
    # Security Group Flag Options:
    #   RULES, INSTANCES (default)
    # For instance: flags=FLAGS.RULES | FLAGS.INSTANCES

    print(json.dumps(secgroup, indent=4, sort_keys=True))

    {
        "assigned_to": [
            {
               "instance_id": "..."
            }
        ],
        "created_at": "...",
        "description": "...",
        "id": "...",
        "location": "...",
        "name": "...",
        "project_id": "...",
        "revision_number": 3,
        "rules": [
            {
                "rule_type": "...",
                "remote_group_id": "...",
                "from_port": "...",
                "description": "...",
                "tags": [],
                "to_port": "...",
                "ethertype": "...",
                "created_at": "...",
                "updated_at": "...",
                "security_group_id": "...",
                "revision_number": 0,
                "tenant_id": "...",
                "project_id": "..."",
                "id": "...",
                "cidr_ip": "...",
                "ip_protocol": "..."
            },
        ],
        "updated_at": "..."
    }
