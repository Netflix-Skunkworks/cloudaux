"""
.. module: cloudaux.tests.aws.test_iam
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Will Bengtson <wbengtson@netflix.com>
.. moduleauthor:: Mike Grima <mgrima@netflix.com>
"""
import pytest

from cloudaux.aws.iam import InvalidAuthorizationFilterException
from cloudaux.orchestration.aws.iam import MissingFieldException


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

    # With no filter supplied:
    with pytest.raises(InvalidAuthorizationFilterException,
                       match='Must provide filter value: User, Role, Group, LocalManagedPolicy, AWSManagedPolicy'):
        get_account_authorization_details(filter='LOLNO')


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

    # Don't pass in the Arn:
    with pytest.raises(MissingFieldException, match='Must include Arn.'):
        get_managed_policy({}, force_client=mock_iam_client)

    result = get_managed_policy({'Arn': 'arn:aws:iam::123456789012:policy/testCloudAuxPolicy'},
                                force_client=mock_iam_client)

    assert result
    assert result['Arn'] == 'arn:aws:iam::123456789012:policy/testCloudAuxPolicy'
    assert isinstance(result['CreateDate'], str)
    assert isinstance(result['UpdateDate'], str)
    assert result['Document']


def test_get_group(group_fixture):
    """Test the get_group API."""
    from cloudaux.aws.iam import get_group

    # Without users:
    result = get_group('testCloudAuxGroup', users=False, force_client=group_fixture)

    for item in ['Users', 'IsTruncated', 'Marker']:
        assert not result.get(item)

    result = result['Group']
    assert result['Path'] == '/'
    assert result['GroupName'] == 'testCloudAuxGroup'
    assert result['GroupId']
    assert result['Arn'] == 'arn:aws:iam::123456789012:group/testCloudAuxGroup'
    assert result['CreateDate']

    # With users:
    result = get_group('testCloudAuxGroup', force_client=group_fixture)
    assert len(result['Users']) == 1
    assert result['Users'][0]['UserName'] == 'testCloudAuxUser'
    assert not result['IsTruncated']


def test_list_group_policies(group_fixture):
    """Test the list_group_policies API."""
    from cloudaux.aws.iam import list_group_policies

    result = list_group_policies('testCloudAuxGroup', force_client=group_fixture)

    assert len(result) == 1
    assert result[0] == 'TestPolicy'


def test_get_group_policy_document(group_fixture):
    """Test the get_group_policy_document API."""
    from cloudaux.aws.iam import get_group_policy_document

    result = get_group_policy_document('testCloudAuxGroup', 'TestPolicy', force_client=group_fixture)

    assert len(result['Statement']) == 1
    assert result['Statement'][0]['Action'] == 's3:ListBucket'


def test_list_attached_group_managed_policies(group_fixture):
    """Test the list_attached_group_managed_policies API."""
    from cloudaux.aws.iam import list_attached_group_managed_policies

    result = list_attached_group_managed_policies('testCloudAuxGroup', force_client=group_fixture)

    assert len(result) == 1
    assert result[0]['PolicyName'] == 'testCloudAuxPolicy'


def test_list_groups_for_user(group_fixture):
    """Test the list_groups_for_user API."""
    from cloudaux.aws.iam import list_groups_for_user

    result = list_groups_for_user('testCloudAuxUser', force_client=group_fixture)

    assert len(result) == 1
    assert result[0]['GroupName'] == 'testCloudAuxGroup'


def test_get_role_orchestration(test_iam):
    """Tests the get_group orchestration."""
    from cloudaux.orchestration.aws.iam.role import get_role

    # Don't pass in the RoleName:
    with pytest.raises(MissingFieldException, match='Cannot extract item name from input: {}'):
        get_role({}, force_client=test_iam)

    result = get_role({'RoleName': 'testRoleCloudAuxName'}, force_client=test_iam)
    assert result['RoleName'] == 'testRoleCloudAuxName'
    assert isinstance(result['CreateDate'], str)
    assert len(result['InstanceProfiles']) == 1
    assert isinstance(result['InstanceProfiles'][0]['CreateDate'], str)


def test_get_group_orchestration(group_fixture):
    """Tests the get_group orchestration."""
    from cloudaux.orchestration.aws.iam.group import FLAGS, get_group

    # Don't pass in the GroupName:
    with pytest.raises(MissingFieldException, match='Must include GroupName.'):
        get_group({}, force_client=group_fixture)

    result = get_group({'GroupName': 'testCloudAuxGroup'}, force_client=group_fixture)

    assert result['GroupName'] == 'testCloudAuxGroup'
    assert not result.get('Users')
    assert len(result['InlinePolicies']) == 1
    assert result['InlinePolicies']['TestPolicy']
    assert result['_version']
    assert len(result['ManagedPolicies']) == 1
    assert result['ManagedPolicies'][0] == 'testCloudAuxPolicy'
    assert isinstance(result['CreateDate'], str)

    # Get the Users too:
    result = get_group({'GroupName': 'testCloudAuxGroup'}, flags=FLAGS.ALL, force_client=group_fixture)

    assert len(result['Users']) == 1
    assert result['Users'][0] == 'testCloudAuxUser'
    assert result['_version']


def test_get_user_orchestration(test_iam):
    """Tests the get_group orchestration."""
    from cloudaux.orchestration.aws.iam.user import get_user

    # Don't pass in the RoleName:
    with pytest.raises(MissingFieldException, match='Cannot extract item name from input: {}'):
        get_user({}, force_client=test_iam)

    result = get_user({'UserName': 'testCloudAuxUser'}, force_client=test_iam)
    assert result['UserName'] == 'testCloudAuxUser'
    assert isinstance(result['CreateDate'], str)


def test_list_server_certificates(server_certificates):
    """Tests the list_server_certificates API."""
    from cloudaux.aws.iam import list_server_certificates

    result = list_server_certificates(force_client=server_certificates)

    validate_results = ['certOne', 'certTwo']

    for cert in result:
        validate_results.remove(cert['ServerCertificateName'])

    assert not validate_results


def test_get_server_certificate(server_certificates):
    """Tests the get_server_certificate API."""
    from cloudaux.aws.iam import get_server_certificate
    from cloudaux.tests.aws.conftest import MOCK_CERT_ONE, MOCK_CERT_TWO

    validate_results = {
        'certOne': MOCK_CERT_ONE,
        'certTwo': MOCK_CERT_TWO
    }

    for name, cert in validate_results.items():
        result = get_server_certificate(name)

        assert result['CertificateBody'] == cert


def test_get_server_certificate_orchestration(server_certificates):
    """Tests the Server Certificate orchestration."""
    from cloudaux.orchestration.aws.iam.server_certificate import get_server_certificate
    from cloudaux.tests.aws.conftest import MOCK_CERT_ONE

    # Don't pass in the ServerCertificateName:
    with pytest.raises(MissingFieldException, match='Must include ServerCertificateName.'):
        get_server_certificate({}, force_client=server_certificates)

    result = get_server_certificate({'ServerCertificateName': 'certOne'}, force_client=server_certificates)
    assert result['ServerCertificateName'] == 'certOne'
    assert isinstance(result['UploadDate'], str)
    assert isinstance(result['Expiration'], str)
    assert not result['CertificateChain']
    assert result['CertificateBody'] == MOCK_CERT_ONE
    assert result['_version'] == 1
    assert result['Path'] == '/'
    assert result['Arn'] == 'arn:aws:iam::123456789012:server-certificate/certOne'
    assert result['ServerCertificateName'] == 'certOne'
