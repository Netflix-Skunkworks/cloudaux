"""
.. module: cloudaux.tests.aws.test_iam
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Will Bengtson <wbengtson@netflix.com>
.. moduleauthor:: Mike Grima <mgrima@netflix.com>
"""


def test_get_account_authorization_details_role(test_iam):
    """Tests the get_account_authorization API."""
    from cloudaux.aws.iam import get_account_authorization_details

    # Test that we can get the results we expect from get_account_authorization_details
    roles = get_account_authorization_details('Role')
    assert len(roles) == 1
    assert roles[0]['RoleName'] == 'testRoleCloudAuxName'

    users = get_account_authorization_details('User')
    assert len(users) == 1
    assert users[0]['UserName'] == 'testCloudAuxUser'

    groups = get_account_authorization_details('Group')
    assert len(groups) == 1
    assert groups[0]['GroupName'] == 'testCloudAuxGroup'

    local_managed_policies = get_account_authorization_details('LocalManagedPolicy')
    assert len(local_managed_policies) == 1
    assert local_managed_policies[0]['PolicyName'] == 'testCloudAuxPolicy'

    # aws_managed_policies gets updated from time to time so the length might change
    # Just test that we have more than 1
    aws_managed_policies = get_account_authorization_details('AWSManagedPolicy')
    assert len(aws_managed_policies) > 1


def test_get_policy_and_document(test_iam):
    """Tests both the get_policy and get_managed_policy_document APIs."""
    from cloudaux.aws.iam import get_policy, get_managed_policy_document
    # Test that we can get the managed policy:
    mp = get_policy('arn:aws:iam::123456789012:policy/testCloudAuxPolicy')
    assert mp['Policy']['PolicyName'] == 'testCloudAuxPolicy'
    assert mp['Policy']['Description'] == 'Test CloudAux Policy'
    assert mp['Policy']['DefaultVersionId'] == 'v1'

    # Test with and without the MP passed in:
    pd = get_managed_policy_document('arn:aws:iam::123456789012:policy/testCloudAuxPolicy')
    pd_mp = get_managed_policy_document('arn:aws:iam::123456789012:policy/testCloudAuxPolicy', policy_metadata=mp)
    assert len(pd['Statement']) == len(pd_mp['Statement']) == 1
    assert pd['Statement'][0]['Action'] == pd_mp['Statement'][0]['Action'] == 's3:ListBucket'
    assert pd['Statement'][0]['Resource'] == pd_mp['Statement'][0]['Resource'] == '*'
    assert pd['Statement'][0]['Effect'] == pd_mp['Statement'][0]['Effect'] == 'Allow'


def test_get_managed_policy_orchestration(test_iam, mock_iam_client):
    """Tests the orchestration for getting a managed policy."""
    from cloudaux.orchestration.aws.iam.managed_policy import get_managed_policy

    result = get_managed_policy('arn:aws:iam::123456789012:policy/testCloudAuxPolicy', force_client=mock_iam_client)

    assert result
    assert result['Arn'] == 'arn:aws:iam::123456789012:policy/testCloudAuxPolicy'
    assert isinstance(result['CreateDate'], str)
    assert isinstance(result['UpdateDate'], str)
    assert result['Document']
