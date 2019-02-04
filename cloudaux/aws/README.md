# cloudaux AWS support

Cloud Auxiliary has support for Amazon Web Services.

## Documentation

 - [CloudAux](../../README.md "CloudAux Readme")
 - [AWS](README.md "Amazon Web Services Docs") [THIS FILE]
 - [GCP](../gcp/README.md "Google Cloud Platform Docs")

## Features

 - intelligent connection caching.
 - handles pagination for certain client methods.
 - rate limit handling, with exponential backoff.
 - multi-account sts:assumerole abstraction.
 - orchestrates all the calls required to fully describe an item.
 - control which attributes are returned flags.

## Orchestration Supported Technologies

 - IAM Role
 - IAM User
 - IAM SAML Provider
 - [S3](../orchestration/aws/s3.md)
 - ELB (v1)
 - ELBv2 (ALB)
 - [Lambda Functions](../orchestration/aws/lambda_function.md)
 - [Glacier Vaults](../orchestration/aws/glacier.md)
 - [EC2 Image](../orchestration/aws/image.md)
 - [Cloudwatch Events](cloudaux/orchestration/aws/events.md)

## Install

    pip install cloudaux

For GCP support run:

    pip install cloudaux\[gcp\]

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
    #   BASE, MANAGED_POLICIES, INLINE_POLICIES, INSTANCE_PROFILES, TAGS, ALL (default)
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
        "Tags": {},
        "_version": 3    # Orchestration results return a _Version
    }
    
### User    
    
    from cloudaux.orchestration.aws.iam.user import get_user, FLAGS
    
    user = get_user(
        dict(arn='arn:aws:iam::000000000000:user/myUser', role_name='myUser'),
        flags=FLAGS.ALL,
        **conn)

    # The flags parameter is optional but allows the user to indicate that 
    # only a subset of the full item description is required.
    # IAM User Flag Options:
    #   BASE, ACCESS_KEYS, INLINE_POLICIES, MANAGED_POLICIES       
    #   MFA_DEVICES, LOGIN_PROFILE, SIGNING_CERTIFICATES, ALL (default)
    # For instance: flags=FLAGS.ACCESS_KEYS | FLAGS.MFA_DEVICES | FLAGS.LOGIN_PROFILE
    
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


## ELB (v1)

    from cloudaux.orchestration.aws.elb import get_load_balancer, FLAGS
    
    conn = dict(
        account_number='000000000000',
        assume_role='SecurityMonkey')
    
    load_balancer = get_load_balancer('MyELB', flags=FLAGS.ALL, **conn)
    
    # The flags parameter is optional but allows the user to indicate that 
    # only a subset of the full item description is required.
    # S3 Flag Options are:
    #   BASE, ATTRIBUTES, TAGS
    # For instance: flags=FLAGS.BASE | FLAGS.TAGS
    
    print(json.dumps(load_balancer, indent=2, sort_keys=True))
    
    {
      "Arn": "arn:aws:elasticloadbalancing:us-east-1:000000000000:loadbalancer/MyELB",
      "Attributes": {
        "AccessLog": {
          "EmitInterval": 5,
          "Enabled": true,
          "S3BucketName": "elb-log-bucket",
          "S3BucketPrefix": "MyELB"
        },
        "ConnectionDraining": {
          "Enabled": false,
          "Timeout": 300
        },
        "ConnectionSettings": {
          "IdleTimeout": 60
        },
        "CrossZoneLoadBalancing": {
          "Enabled": false
        }
      },
      "AvailabilityZones": [
        "us-east-1b"
      ],
      "BackendServerDescriptions": [],
      "CanonicalHostedZoneNameID": "ZXXXXXXXXXXXXX",
      "CreatedTime": "2015-07-07 19:15:06.490000+00:00",
      "DNSName": "internal-MyELB-1800000000.us-east-1.elb.amazonaws.com",
      "HealthCheck": {
        "HealthyThreshold": 2,
        "Interval": 30,
        "Target": "HTTP:80/health",
        "Timeout": 5,
        "UnhealthyThreshold": 2
      },
      "Instances": [],
      "ListenerDescriptions": [
        {
          "InstancePort": 443,
          "InstanceProtocol": "TCP",
          "LoadBalancerPort": 443,
          "Protocol": "TCP"
          "PolicyNames": []
        },
        {
          "InstancePort": 80,
          "InstanceProtocol": "HTTP",
          "LoadBalancerPort": 80,
          "Protocol": "HTTP"
          "PolicyNames": []
        }
      ],
      "LoadBalancerName": "MyELB",
      "Policies": {
        "AppCookieStickinessPolicies": [],
        "LBCookieStickinessPolicies": [],
        "OtherPolicies": []
      },
      "Region": "us-east-1",
      "Scheme": "internal",
      "SecurityGroups": [
        "sg-19999999"
      ],
      "SourceSecurityGroup": {
        "GroupName": "MyELB-SecurityGroup",
        "OwnerAlias": "000000000000"
      },
      "Subnets": [
        "subnet-19999999"
      ],
      "Tags": [
        {
              "Key": "tagkey",
              "Value": "tagvalue"
        }
      ],
      "VPCId": "vpc-49999999",
      "_version": 2
    }

## ELBv2 (ALB)

    from cloudaux.orchestration.aws.elbv2 import get_elbv2, FLAGS

    conn = dict(
        account_number='000000000000',
        assume_role='SecurityMonkey')

    alb = get_elbv2('MyALB', flags=FLAGS.ALL, **conn)

    # The flags parameter is optional but allows the user to indicate that
    # only a subset of the full item description is required.
    # S3 Flag Options are:
    #   BASE LISTENERS RULES ATTRIBUTES TAGS
    #   TARGET_GROUPS TARGET_GROUP_ATTRIBUTES TARGET_GROUP_HEALTH
    # For instance: flags=FLAGS.BASE | FLAGS.TARGET_GROUPS

    print(json.dumps(alb, indent=2, sort_keys=True))

    {
      "Arn": "arn:aws:elasticloadbalancing:us-east-1:000000000000:loadbalancer/app/MyALB/0000000000000000", 
      "Attributes": [
        {
          "Key": "access_logs.s3.enabled", 
          "Value": "false"
        }, 
        {
          "Key": "idle_timeout.timeout_seconds", 
          "Value": "60"
        }, 
        {
          "Key": "access_logs.s3.prefix", 
          "Value": ""
        }, 
        {
          "Key": "deletion_protection.enabled", 
          "Value": "false"
        }, 
        {
          "Key": "access_logs.s3.bucket", 
          "Value": ""
        }
      ], 
      "AvailabilityZones": [
        {
          "SubnetId": "subnet-00000000", 
          "ZoneName": "us-east-1d"
        }, 
        {
          "SubnetId": "subnet-00000000", 
          "ZoneName": "us-east-1c"
        }, 
        {
          "SubnetId": "subnet-00000000", 
          "ZoneName": "us-east-1e"
        }
      ], 
      "CanonicalHostedZoneId": "Z0000000000000", 
      "CreatedTime": "2016-08-18 01:11:45.430000+00:00", 
      "DNSName": "MyALB-000000000.us-east-1.elb.amazonaws.com", 
      "IpAddressType": "ipv4", 
      "Listeners": [
        {
          "Certificates": [
            {
              "CertificateArn": "arn:aws:iam::000000000000:server-certificate/Blah"
            }
          ], 
          "DefaultActions": [
            {
              "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:000000000000:targetgroup/.../0000000000000000", 
              "Type": "forward"
            }
          ], 
          "ListenerArn": "arn:aws:elasticloadbalancing:us-east-1:000000000000:listener/app/MyALB/0000000000000000/0000000000000000", 
          "LoadBalancerArn": "arn:aws:elasticloadbalancing:us-east-1:000000000000:loadbalancer/app/MyALB/0000000000000000", 
          "Port": 443, 
          "Protocol": "HTTPS", 
          "SslPolicy": "ELBSecurityPolicy-2015-05"
        }
      ], 
      "LoadBalancerName": "MyALB", 
      "Region": "us-east-1", 
      "Rules": [
        {
          "Actions": [
            {
              "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:000000000000:targetgroup/targets/0000000000000000", 
              "Type": "forward"
            }
          ], 
          "Conditions": [], 
          "IsDefault": true, 
          "Priority": "default", 
          "RuleArn": "arn:aws:elasticloadbalancing:us-east-1:000000000000:listener-rule/app/.../0000000000000000/0000000000000000/0000000000000000"
        }
      ], 
      "Scheme": "internet-facing", 
      "SecurityGroups": [
        "sg-00000000" 
      ], 
      "State": {
        "Code": "active"
      }, 
      "Tags": [
        {
          "ResourceArn": "arn:aws:elasticloadbalancing:us-east-1:000000000000:loadbalancer/app/.../0000000000000000", 
          "Tags": []
        }
      ], 
      "TargetGroupAttributes": [
        {
          "Key": "stickiness.enabled", 
          "Value": "false"
        }, 
        {
          "Key": "deregistration_delay.timeout_seconds", 
          "Value": "300"
        }, 
        {
          "Key": "stickiness.type", 
          "Value": "lb_cookie"
        }, 
        {
          "Key": "stickiness.lb_cookie.duration_seconds", 
          "Value": "86400"
        }
      ], 
      "TargetGroupHealth": [],
      "TargetGroups": [
        {
          "HealthCheckIntervalSeconds": 30, 
          "HealthCheckPath": "/healthcheck", 
          "HealthCheckPort": "traffic-port", 
          "HealthCheckProtocol": "HTTP", 
          "HealthCheckTimeoutSeconds": 5, 
          "HealthyThresholdCount": 2, 
          "LoadBalancerArns": [
            "arn:aws:elasticloadbalancing:us-east-1:000000000000:loadbalancer/app/.../0000000000000000"
          ], 
          "Matcher": {
            "HttpCode": "200"
          }, 
          "Port": 7001, 
          "Protocol": "HTTP", 
          "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:000000000000:targetgroup/targets/0000000000000000", 
          "TargetGroupName": "targets", 
          "UnhealthyThresholdCount": 2, 
          "VpcId": "vpc-00000000"
        }
      ], 
      "Type": "application", 
      "VpcId": "vpc-00000000", 
      "_version": 2
    }


## IAM SAML Provider

    from cloudaux.orchestration.aws.iam.saml_provider import get_saml_provider

    conn = dict(
        account_number='000000000000',
        assume_role='SecurityMonkey')

    provider = get_saml_provider('arn:aws:iam::111111111111:saml-provider/MySAMLProvider', **conn)
    
    or
    
    provider = get_saml_provider(dict(Arn='arn:aws:iam::111111111111:saml-provider/MySAMLProvider'), **conn)

    print(json.dumps(provider, indent=2, sort_keys=True))
    
    {
      "Arn": "arn:aws:iam::111111111111:saml-provider/MySAMLProvider", 
      "Company": "Acme, Inc.", 
      "CreateDate": "2017-03-06 21:27:03+00:00", 
      "Email": "identity@acme.com", 
      "GivenName": "Identity", 
      "Name": "https://identity.acme.com", 
      "ValidUntil": "2018-03-06 21:27:03.086000+00:00", 
      "X510": "MIIDXx...xx="
    }
