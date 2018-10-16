# CloudAux AWS IAM Managed Policies

CloudAux can build out a JSON object describing an IAM Managed Policy.

## Example

    from cloudaux.orchestration.aws.iam.managed_policy import get_managed_policy, FLAGS

    conn = dict(
        account_number='123456789012',
        assume_role='SecurityMonkey')

    managed_policy = get_managed_policy('arn:aws:iam::123456789012:policy/testCloudAuxPolicy', flags=FLAGS.ALL, **conn)

    # The flags parameter is optional. It presently doesn't have any other specified items at this time.

    print(json.dumps(managed_policy, indent=2, sort_keys=True))

    {
      "Arn": "arn:aws:iam::123456789012:policy/testCloudAuxPolicy",
      "AttachmentCount": 0,
      "CreateDate": "2018-10-16T00:24:27Z",
      "DefaultVersionId": "v1",
      "Description": "Test CloudAux Policy",
      "Document": {
        "Statement": [
          {
            "Action": "s3:ListBucket",
            "Effect": "Allow",
            "Resource": "*"
          }
        ],
        "Version": "2012-10-17"
      },
      "Path": "/",
      "PolicyId": "AVJIT34BWVH14CIACU1CM",
      "PolicyName": "testCloudAuxPolicy",
      "UpdateDate": "2018-10-16T00:24:27Z",
      "_version": 1
    }
