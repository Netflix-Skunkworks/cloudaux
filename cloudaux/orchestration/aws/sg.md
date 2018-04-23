# CloudAux AWS Lambda Function

CloudAux can build out a JSON object describing an AWS Security Group.

## Example

    from cloudaux.orchestration.aws.sg import describe_security_group

    conn = dict(
        account_number='111111111111',
        assume_role='SecurityMonkey')

    sg = describe_security_group('sg-12345678', **conn)
    
    print(json.dumps(provider, indent=2, sort_keys=True))

    {
      "Description": ...,
      "GroupName": ...,
      "IpPermissions" ...,
      "OwnerId" ...,
      "GroupId" ...,
      "IpPermissionsEgress" ...,
      "VpcId" ...
    }
