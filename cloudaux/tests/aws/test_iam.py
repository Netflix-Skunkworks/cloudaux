"""
.. module: cloudaux.tests.aws.test_iam
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Will Bengtson <wbengtson@netflix.com>
"""

from cloudaux.aws.iam import get_account_authorization_details


def test_get_account_authorization_details_role(test_iam):
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
