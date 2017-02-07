# cloudaux AWS support

Cloud Auxiliary has support for Amazon Web Services.

## Documenation

 - [CloudAux](../../README.md "CloudAux Readme")
 - [AWS](README.md "Amazon Web Services Docs") [THIS FILE]
 - [GCP](../gcp/README.md "Google Cloud Platform Docs")

## Features

 - intelligent connection caching.
 - handles pagination for certain client methods.
 - rate limit handling, with exponential backoff.
 - multi-account sts:assumerole abstraction.
 - orchestrates all the calls required to fully describe an item.

## Orchestration Supported Technologies

 - IAM Role
 - IAM User
 - S3

## Install

    pip install cloudaux

## Example

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

## Orchestration Example

### Role

    from cloudaux.orchestration.aws.iam.role import get_role
    
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
        **conn)

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
    
### User    
    
    from cloudaux.orchestration.aws.iam.user import get_user
    
    user = get_user(
        dict(arn='arn:aws:iam::000000000000:user/myUser', role_name='myUser'),
        **conn)
    
    print(json.dumps(user, indent=2, sort_keys=True))
    
    
    {
      "AccessKeys": [
        {
          "AccessKeyId": ...,
          "CreateDate": ...,
          "LastUsedDate": ...,
          "Region": "us-east-1", 
          "ServiceName": ...,
          "Status": "Active", 
          "UserName": ...,
        }
      ], 
      "Arn": ...,
      "CreateDate": ...,
      "InlinePolicies": ..., 
      "LoginProfile": null, 
      "ManagedPolicies": [], 
      "MfaDevices": {}, 
      "Path": "/", 
      "SigningCertificates": {}, 
      "UserId": ..., 
      "UserName": ...,
      "_version": 1
    }

### S3

    from cloudaux.orchestration.aws.s3 import get_bucket
    
    conn = dict(
        account_number='000000000000',
        assume_role='SecurityMonkey')
    
    bucket = get_bucket('MyS3Bucket', **conn)
    
    print(json.dumps(bucket, indent=2, sort_keys=True))
    
    {
      "Arn": "arn:aws:s3:::MyS3Bucket", 
      "Grants": {
        "cloudaux_grantee": [
          "FULL_CONTROL"
        ]
      },
      "Owner": {
        "ID": "SomeIdStringHere",
        "DisplayName": "cloudaux_grantee"
      },
      "LifecycleRules": [
        {
          "expiration": {
            "days": 365
          }, 
          "id": "deleteoldstuff", 
          "prefix": "/doesntactuallyexist", 
          "status": "Enabled"
        }
      ], 
      "Logging": {
        "enabled": true, 
        "grants": [], 
        "prefix": "logs/", 
        "target": "MyS3LoggingBucket"
      }, 
      "Policy": {
        "Statement": [
          {
            "Action": "s3:GetObject", 
            "Effect": "Allow", 
            "Principal": {
              "AWS": "*"
            }, 
            "Resource": "arn:aws:s3:::MyS3Bucket/*", 
            "Sid": "AddPerm"
          }
        ], 
        "Version": "2008-10-17"
      },
      "Region": "us-east-1",
      "Tags": {
        "tagkey": "tagvalue"
      }, 
      "Versioning": {
        "Status": "Enabled"
      },
      "Website": {
        "IndexDocument": {
          "Suffix": "index.html"
        }
      },
      "Cors": {
        "AllowedMethods": [
          "GET"
        ],
        "MaxAgeSeconds": 3000,
        "AllowedHeaders": [
          "Authorization"
        ],
        "AllowedOrigins": [
          "*",
        ]
      },
      "Notifications": {
        "LambdaFunctionConfigurations": [
          {
            "LambdaFunctionArn": "arn:aws:lambda:us-east-1:ACCNTNUM:function:LAMBDAFUNC",
            "Id": "1234-34534-12-5-123-4213-4123-41235612423",
            "Filter": {
              "Key": {
                "FilterRules": [
                  {
                    "Name": "Prefix",
                    "Value": "somepath/"
                  }
                ]
              },
              "Events": [
                "s3:ObjectCreated:Put"
              ]
            }
          }
        ]
      },
      "Acceleration": "Enabled",
      "Replication": {
        "Rules": [
          {
            "Prefix": "",
            "ID": "MyS3Bucket",
            "Destination": {
              "Bucket": "arn:aws:s3:::MyOtherS3Bucket"
            },
            "Status": "Enabled"
          }
        ],
        "Role": "arn:aws:iam::ACCOUNTNUM:role/MYREPLICATIONROLE"
      },
      "AnalyticsConfigurations": [
        "Filter": {
          "Prefix": "someprefix"
        },
        "StorageClassAnalysis": {
          "DataExport": {
            "Destination": {
              "S3BucketDestination": {
                "Prefix": "someother/prefix",
                "Format": "CSV",
                "Bucket": "arn:aws:s3:::SOMEBUCKETDESTINATION"
              }
              "OutputSchemaVersion": "V_1"
            }
          }
          "Id": "s3analytics"
        }
      ],
      "MetricsConfigurations": [
        {
          "Id": "SomeWholeBucketMetricsConfig"
        },
        {
          "Filter": {
            "Prefix": "some/prefix"
          },
          "Id": "SomeOtherMetricsConfig"
        }
      ],
      "InventoryConfigurations": [
        {
          "Destination": {
            "S3BucketDestination": {
              "Prefix": "someother/prefix",
              "Format": "CSV",
              "Bucket": "arn:aws:s3:::SOMEBUCKETDESTINATION"
            },
            "Filter": {
              "Prefix": "someprefix/"
            },
            "IsEnabled": true,
            "OptionalFields": [
              "Size",
              "LastModifiedDate",
              "StorageClass",
              "ETag",
              "ReplicationStatus"
            ],
            "IncludedObjectVersions": "All",
            "Schedule": {
              "Frequency": "Weekly"
            },
            "Id": "inventoryconfig"
          }
        }
      ],
      "Created": "2016-12-2 10:00:00+00:00",
      "_version": 4
    }
