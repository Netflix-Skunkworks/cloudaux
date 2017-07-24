# CloudAux AWS Lambda Function

CloudAux can build out a JSON object describing an AWS Lambda Function.

## Example

    # Imports
    from cloudaux.orchestration.aws.lambda_function import get_lambda_function, FLAGS
    from cloudaux.aws.lambda_function import list_functions

    conn = {
        'account_number': '111111111111',
        'assume_role': 'MyRole',
        'session_name': 'MySession',
        'region': 'us-east-1'
    }

    # List Functions in Region
    functions = list_functions(**conn)

    # By Name:
    lambda_function = get_lambda_function('MyLambdaFunction', **conn)

    # By ARN
    lambda_function = get_lambda_function('arn:aws:lambda:us-east-1:111111111111:function:MyLambdaFunction', **conn)

    # Pass in datastructure
    lambda_function = dict(FunctionName='MyLambdaFunction')
    lambda_function = get_lambda_function(lambda_function, **conn)

    # Iterate over output from list_functions and add policy info.
    for function in functions:
        function = get_lambda_function(function, flags=FLAGS.POLICY, **conn)


## Flags

The `get_lambda_function` command accepts flags describing what parts of the structure to build out.

    from cloudaux.orchestration.aws.lambda_function import FLAGS

    desired_fields = FLAGS.BASE | FLAGS.TAGS
    lambda_function = get_lambda_function('MyLambdaFunction', flags=desired_flags, **conn)

If not provided, `get_lambda_function` assumes `FLAGS.ALL`.

- [BASE](#flagsbase)
- [ALIASES](#flagsaliases)
- [EVENT_SOURCE_MAPPINGS](#flagsevent-source-mappings)
- [VERSIONS](#flagsversions)
- [TAGS](#flagstags)
- [POLICY](#flagspolicy)
- [ALL](#flagsall)


### FLAGS.BASE

Call boto3's [`client.get_function`](http://boto3.readthedocs.io/en/latest/reference/services/lambda.html#Lambda.Client.get_function).

    {
        'FunctionName': 'string',
        'FunctionArn': 'string',
        'Runtime': 'nodejs'|'nodejs4.3'|'nodejs6.10'|'java8'|'python2.7'|'python3.6'|'dotnetcore1.0'|'nodejs4.3-edge',
        'Role': 'string',
        'Handler': 'string',
        'CodeSize': 123,
        'Description': 'string',
        'Timeout': 123,
        'MemorySize': 123,
        'LastModified': 'string',
        'CodeSha256': 'string',
        'Version': 'string',
        'VpcConfig': {
            'SubnetIds': [
                'string',
            ],
            'SecurityGroupIds': [
                'string',
            ],
            'VpcId': 'string'
        },
        'DeadLetterConfig': {
            'TargetArn': 'string'
        },
        'Environment': {
            'Variables': {
                'string': 'string'
            },
            'Error': {
                'ErrorCode': 'string',
                'Message': 'string'
            }
        },
        'KMSKeyArn': 'string',
        'TracingConfig': {
            'Mode': 'Active'|'PassThrough'
        },
        'MasterArn': 'string'
    }


### FLAGS.ALIASES

Calls boto3's [`client.get_alias`](http://boto3.readthedocs.io/en/latest/reference/services/lambda.html#Lambda.Client.get_alias).

This will list every alias for the lambda function.  Example:

      "Aliases": [
        {
          "AliasArn": "arn:aws:lambda:us-east-1:111111111111:function:MyLambdaFunction:stable", 
          "Description": "", 
          "FunctionVersion": "4", 
          "Name": "stable"
        }
      ]
      
In this example, there is an alias called `stable` pointing to function version `4`.

### FLAGS.EVENT_SOURCE_MAPPINGS

Calls boto3's [`client.list_event_source_mappings`](http://boto3.readthedocs.io/en/latest/reference/services/lambda.html#Lambda.Client.list_event_source_mappings).

    "EventSourceMappings": [
        {
            'UUID': 'string',
            'BatchSize': 123,
            'EventSourceArn': 'string',
            'FunctionArn': 'string',
            'LastModified': datetime(2015, 1, 1),
            'LastProcessingResult': 'string',
            'State': 'string',
            'StateTransitionReason': 'string'
        },
    ]

### FLAGS.VERSIONS

Calls boto3's [`client.list_versions_by_function`](http://boto3.readthedocs.io/en/latest/reference/services/lambda.html#Lambda.Client.list_versions_by_function).

    'Versions': [
        {
            'FunctionName': 'string',
            'FunctionArn': 'string',
            'Runtime': 'nodejs'|'nodejs4.3'|'nodejs6.10'|'java8'|'python2.7'|'python3.6'|'dotnetcore1.0'|'nodejs4.3-edge',
            'Role': 'string',
            'Handler': 'string',
            'CodeSize': 123,
            'Description': 'string',
            'Timeout': 123,
            'MemorySize': 123,
            'LastModified': 'string',
            'CodeSha256': 'string',
            'Version': 'string',
            'VpcConfig': {
                'SubnetIds': [
                    'string',
                ],
                'SecurityGroupIds': [
                    'string',
                ],
                'VpcId': 'string'
            },
            'DeadLetterConfig': {
                'TargetArn': 'string'
            },
            'Environment': {
                'Variables': {
                    'string': 'string'
                },
                'Error': {
                    'ErrorCode': 'string',
                    'Message': 'string'
                }
            },
            'KMSKeyArn': 'string',
            'TracingConfig': {
                'Mode': 'Active'|'PassThrough'
            },
            'MasterArn': 'string'
        },
    ]

### FLAGS.TAGS

Calls boto3's [`client.list_tags`](http://boto3.readthedocs.io/en/latest/reference/services/lambda.html#Lambda.Client.list_tags).

    'Tags': {
        'string': 'string'
    }
    
### FLAGS.POLICY

Lambda Function Policies are complicated.  They can be attached to an alias, a version, and there is also a default policy. This method attempts to gather all three types.

Calls boto3's [`client.get_policy`](http://boto3.readthedocs.io/en/latest/reference/services/lambda.html#Lambda.Client.get_policy) for each version and alias and once for the default policy.

Depends on first obtaining the function aliases and versions, though [flagpole](https://github.com/monkeysecurity/flagpole) will take care of that.

Returns a datastructure like this:

    "Policy": {
        "Aliases": {
            "stable": {
                "Id": "default", 
                "Statement": [
                  {
                    "Action": "lambda:InvokeFunction", 
                    "Effect": "Allow", 
                    "Principal": {
                      "AWS": "arn:..."
                    }, 
                    "Resource": "arn:aws:lambda:us-east-1:111111111111:function:MyFunction:stable" 
                  }
                ], 
                "Version": "2012-10-17"
            }
        },
        "DEFAULT": {
            "Id": "default", 
            "Statement": [
              {
                "Action": "lambda:InvokeFunction", 
                "Effect": "Allow", 
                "Principal": {
                  "AWS": "arn:..."
                }, 
                "Resource": "arn:aws:lambda:us-east-1:111111111111:function:MyFunction" 
              }
            ], 
            "Version": "2012-10-17"
        }
        "Versions": {
            "4": {
                "Id": "default", 
                "Statement": [
                  {
                    "Action": "lambda:InvokeFunction", 
                    "Effect": "Allow", 
                    "Principal": {
                      "AWS": "arn:..."
                    }, 
                    "Resource": "arn:aws:lambda:us-east-1:111111111111:function:MyFunction:4" 
                  }
                ], 
                "Version": "2012-10-17"
            }
        }
    }

### FLAGS.ALL

`FLAGS.ALL` is the default if no other flag is passed into `get_lambda_function`.

Returns a datastructure like this:

    {
      "Aliases": [
        {
          "AliasArn": "arn:aws:lambda:us-east-1:111111111111:function:MyLambdaFunction:stable",
          "Description": "",
          "FunctionVersion": "4",
          "Name": "stable"
        }
      ],
      "Arn": "arn:aws:lambda:us-east-1:111111111111:function:MyLambdaFunction",
      "CodeSha256": "qdckFmOzIR1G2GSwD+0S3GQJK2+HyocjHj8UdqPzQkU=",
      "CodeSize": 11571373,
      "Description": "",
      "EventSourceMappings": [],
      "FunctionArn": "arn:aws:lambda:us-east-1:111111111111:function:MyLambdaFunction",
      "FunctionName": "MyLambdaFunction",
      "Handler": "my_lambda.lambda_handler",
      "LastModified": "2017-06-08T03:25:13.480+0000",
      "MemorySize": 128,
      "Policy": {
        "Aliases": {
          "stable": {
            "Id": "default",
            "Statement": [
              {
                "Action": "lambda:InvokeFunction",
                "Effect": "Allow",
                "Principal": {
                  "AWS": "arn:..."
                },
                "Resource": "arn:aws:lambda:us-east-1:111111111111:function:MyFunction:stable"
              }
            ],
            "Version": "2012-10-17"
          }
        },
        "DEFAULT": {
          "Id": "default",
          "Statement": [
            {
              "Action": "lambda:InvokeFunction",
              "Effect": "Allow",
              "Principal": {
                "AWS": "arn:..."
              },
              "Resource": "arn:aws:lambda:us-east-1:111111111111:function:MyFunction"
            }
          ],
          "Version": "2012-10-17"
        },
        "Versions": {
          "4": {
            "Id": "default",
            "Statement": [
              {
                "Action": "lambda:InvokeFunction",
                "Effect": "Allow",
                "Principal": {
                  "AWS": "arn:..."
                },
                "Resource": "arn:aws:lambda:us-east-1:111111111111:function:MyFunction:4"
              }
            ],
            "Version": "2012-10-17"
          }
        }
      },
      "Role": "arn:aws:iam::111111111111:role/MyLambdaFunctionLambdaProfile",
      "Runtime": "python2.7",
      "Tags": {},
      "Timeout": 60,
      "TracingConfig": {
        "Mode": "PassThrough"
      },
      "Version": "$LATEST",
      "Versions": [
        {
          "CodeSha256": "qdckFmOzIR1G2GSwD+0S3GQJK2+HyocjHj8UdqPzQkU=",
          "CodeSize": 11571373,
          "Description": "",
          "FunctionArn": "arn:aws:lambda:us-east-1:111111111111:function:MyLambdaFunction:$LATEST",
          "FunctionName": "MyLambdaFunction",
          "Handler": "my_lambda.lambda_handler",
          "LastModified": "2017-06-08T03:25:13.480+0000",
          "MemorySize": 128,
          "Role": "arn:aws:iam::111111111111:role/MyLambdaFunctionLambdaProfile",
          "Runtime": "python2.7",
          "Timeout": 60,
          "TracingConfig": {
            "Mode": "PassThrough"
          },
          "Version": "$LATEST",
          "VpcConfig": {
            "SecurityGroupIds": [],
            "SubnetIds": []
          }
        },
        {
          "CodeSha256": "qdckFmOzIR1G2GSwD+0S3GQJK2+HyocjHj8UdqPzQkU=",
          "CodeSize": 11571373,
          "Description": "1",
          "FunctionArn": "arn:aws:lambda:us-east-1:111111111111:function:MyLambdaFunction:4",
          "FunctionName": "MyLambdaFunction",
          "Handler": "my_lambda.lambda_handler",
          "LastModified": "2017-07-21T16:26:57.180+0000",
          "MemorySize": 128,
          "Role": "arn:aws:iam::111111111111:role/MyLambdaFunctionLambdaProfile",
          "Runtime": "python2.7",
          "Timeout": 60,
          "TracingConfig": {
            "Mode": "PassThrough"
          },
          "Version": "4",
          "VpcConfig": {
            "SecurityGroupIds": [],
            "SubnetIds": []
          }
        }
      ],
      "VpcConfig": {
        "SecurityGroupIds": [],
        "SubnetIds": []
      },
      "_version": 1
    }
    