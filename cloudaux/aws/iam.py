"""
.. module: cloudaux.aws.iam
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Patrick Kelley <pkelley@netflix.com> @monkeysecurity
.. moduleauthor:: Will Bengtson <wbengtson@netflix.com>
.. moduleauthor:: Steven Reiling <sreiling@netflix.com>
.. moduleauthor:: Travis McPeak <tmcpeak@netflix.com>
.. moduleauthor:: Mike Grima <mgrima@netflix.com>
"""
from cloudaux import get_iso_string
from cloudaux.aws.sts import sts_conn
from cloudaux.aws.decorators import rate_limited
from cloudaux.aws.decorators import paginated
from joblib import Parallel, delayed
import botocore.exceptions


class InvalidAuthorizationFilterException(Exception):
    """Exception if an invalid get_account_authorization_details filter was provided"""
    pass


@sts_conn('iam')
@rate_limited()
def list_saml_providers(client=None, **kwargs):
    return client.list_saml_providers()['SAMLProviderList']


@sts_conn('iam')
@rate_limited()
def get_saml_provider(arn, client=None, **kwargs):
    return client.get_saml_provider(SAMLProviderArn=arn)


@sts_conn('iam')
@rate_limited()
def list_roles(**kwargs):
    client = kwargs['client']
    roles = []
    marker = {}

    while True:
        response = client.list_roles(**marker)
        roles.extend(response['Roles'])

        if response['IsTruncated']:
            marker['Marker'] = response['Marker']
        else:
            return roles


@sts_conn('iam')
@rate_limited()
def list_users(**kwargs):
    client = kwargs['client']
    users = []
    marker = {}

    while True:
        response = client.list_users(**marker)
        users.extend(response['Users'])

        if response['IsTruncated']:
            marker['Marker'] = response['Marker']
        else:
            return users


@rate_limited()
@sts_conn('iam', service_type='client')
def get_role_inline_policy_names(role, client=None, **kwargs):
    marker = {}
    inline_policies = []

    while True:
        response = client.list_role_policies(
            RoleName=role['RoleName'],
            **marker
        )
        inline_policies.extend(response['PolicyNames'])

        if response['IsTruncated']:
            marker['Marker'] = response['Marker']
        else:
            return inline_policies


@rate_limited()
@sts_conn('iam', service_type='client')
def get_user_inline_policy_names(user, client=None, **kwargs):
    marker = {}
    inline_policies = []

    while True:
        response = client.list_user_policies(
            UserName=user['UserName'],
            **marker
        )
        inline_policies.extend(response['PolicyNames'])

        if response['IsTruncated']:
            marker['Marker'] = response['Marker']
        else:
            return inline_policies


def get_role_inline_policies(role, **kwargs):
    policy_names = get_role_inline_policy_names(role, **kwargs)

    policies = zip(
        policy_names,
        Parallel(n_jobs=20, backend="threading")(
            delayed(get_role_inline_policy_document)
            (role, policy_name, **kwargs) for policy_name in policy_names
        )
    )
    policies = dict(policies)

    return policies


def get_user_inline_policies(user, **kwargs):
    policy_names = get_user_inline_policy_names(user, **kwargs)

    policies = {}
    for policy_name in policy_names:
        policies[policy_name] = get_user_inline_policy_document(user, policy_name, **kwargs)

    return policies


@sts_conn('iam', service_type='client')
@rate_limited()
def get_role_inline_policy_document(role, policy_name, client=None, **kwargs):
    response = client.get_role_policy(
        RoleName=role['RoleName'],
        PolicyName=policy_name
    )
    return response.get('PolicyDocument')


@sts_conn('iam', service_type='client')
@rate_limited()
def get_user_inline_policy_document(user, policy_name, client=None, **kwargs):
    response = client.get_user_policy(
        UserName=user['UserName'],
        PolicyName=policy_name
    )
    return response.get('PolicyDocument')


@sts_conn('iam', service_type='client')
@rate_limited()
def get_role_instance_profiles(role, client=None, **kwargs):
    marker = {}
    instance_profiles = []

    while True:
        response = client.list_instance_profiles_for_role(
            RoleName=role['RoleName'],
            **marker
        )
        instance_profiles.extend(response['InstanceProfiles'])

        if response['IsTruncated']:
            marker['Marker'] = response['Marker']
        else:
            break

    return [
        {
            'Path': ip['Path'],
            'InstanceProfileName': ip['InstanceProfileName'],
            'CreateDate': get_iso_string(ip['CreateDate']),
            'InstanceProfileId': ip['InstanceProfileId'],
            'Arn': ip['Arn']
        } for ip in instance_profiles
    ]


@sts_conn('iam', service_type='client')
@paginated('Tags')
@rate_limited()
def list_role_tags(role, client=None, **kwargs):
    return client.list_role_tags(
        RoleName=role['RoleName'],
        **kwargs
    )


@sts_conn('iam', service_type='client')
@paginated('Policies')
@rate_limited()
def get_all_managed_policies(client=None, **kwargs):
    return client.list_policies(
        **kwargs
    )

@sts_conn('iam', service_type='client')
@rate_limited()
def get_role_managed_policy_documents(role, client=None, **kwargs):
    """Retrieve the currently active policy version document for every managed policy that is attached to the role."""
    policies = get_role_managed_policies(role, force_client=client)

    policy_names = (policy['name'] for policy in policies)
    delayed_gmpd_calls = (delayed(get_managed_policy_document)(policy['arn'], force_client=client) for policy
                          in policies)
    policy_documents = Parallel(n_jobs=20, backend="threading")(delayed_gmpd_calls)

    return dict(zip(policy_names, policy_documents))


@sts_conn('iam', service_type='client')
@rate_limited()
def get_managed_policy_document(policy_arn, policy_metadata=None, client=None, **kwargs):
    """Retrieve the currently active (i.e. 'default') policy version document for a policy.

    :param policy_arn:
    :param policy_metadata: This is a previously fetch managed policy response from boto/cloudaux.
                            This is used to prevent unnecessary API calls to get the initial policy default version id.
    :param client:
    :param kwargs:
    :return:
    """
    if not policy_metadata:
        policy_metadata = client.get_policy(PolicyArn=policy_arn)

    policy_document = client.get_policy_version(PolicyArn=policy_arn,
                                                VersionId=policy_metadata['Policy']['DefaultVersionId'])
    return policy_document['PolicyVersion']['Document']


@sts_conn('iam', service_type='client')
@rate_limited()
def get_policy(policy_arn, client=None, **kwargs):
    """Retrieve the IAM Managed Policy."""
    return client.get_policy(PolicyArn=policy_arn, **kwargs)


@sts_conn('iam', service_type='client')
@rate_limited()
def get_role_managed_policies(role, client=None, **kwargs):
    marker = {}
    policies = []

    while True:
        response = client.list_attached_role_policies(
            RoleName=role['RoleName'],
            **marker
        )
        policies.extend(response['AttachedPolicies'])

        if response['IsTruncated']:
            marker['Marker'] = response['Marker']
        else:
            break

    return [{'name': p['PolicyName'], 'arn': p['PolicyArn']} for p in policies]


@paginated('AttachedPolicies')
def _get_user_managed_policies(user, client=None, **kwargs):
    return client.list_attached_user_policies(
        UserName=user['UserName'],
        **kwargs
    )


@sts_conn('iam', service_type='client')
@rate_limited()
def get_user_managed_policies(user, client=None, **kwargs):
    policies = _get_user_managed_policies(user, client=client, **kwargs)
    return [{'name': p['PolicyName'], 'arn': p['PolicyArn']} for p in policies]


@paginated('AccessKeyMetadata')
def _get_user_access_keys(user, client=None, **kwargs):
    return client.list_access_keys(
        UserName=user['UserName'],
        **kwargs)


@sts_conn('iam', service_type='client')
@rate_limited()
def get_user_access_keys(user, client=None, **kwargs):
    keys = _get_user_access_keys(user, client=client, **kwargs)

    # add date-last-used info
    for key in keys:
        key['CreateDate'] = str(key['CreateDate'])
        response = client.get_access_key_last_used(AccessKeyId=key['AccessKeyId'])
        response = response['AccessKeyLastUsed']
        if 'LastUsedDate' in response:
            response['LastUsedDate'] = str(response['LastUsedDate'])
        key.update(response.items())
    return keys


@paginated('MFADevices')
def _get_user_mfa_devices(user, client=None, **kwargs):
    return client.list_mfa_devices(
        UserName=user['UserName'],
        **kwargs)


@sts_conn('iam', service_type='client')
@rate_limited()
def get_user_mfa_devices(user, client=None, **kwargs):
    mfas = _get_user_mfa_devices(user, client=client, **kwargs)
    for mfa in mfas:
        mfa['EnableDate'] = str(mfa['EnableDate'])

    return {mfa['SerialNumber']: dict(mfa) for mfa in mfas}


@sts_conn('iam', service_type='client')
@rate_limited()
def get_user_login_profile(user, client=None, **kwargs):
    try:
        login_profile = client.get_login_profile(UserName=user['UserName'])
        login_profile = login_profile['LoginProfile']
        login_profile['CreateDate'] = str(login_profile['CreateDate'])
        return login_profile
    except botocore.exceptions.ClientError as _:
        return None


@paginated('Certificates')
def _get_user_signing_certificates(user, client=None, **kwargs):
    return client.list_signing_certificates(
        UserName=user['UserName'],
        **kwargs)


@sts_conn('iam', service_type='client')
@rate_limited()
def get_user_signing_certificates(user, client=None, **kwargs):
    certificates = _get_user_signing_certificates(user, client=client, **kwargs)
    for certificate in certificates:
        if 'UploadDate' in certificate:
            certificate['UploadDate'] = str(certificate['UploadDate'])

    return {certificate['CertificateId']: dict(certificate) for certificate in certificates}


@sts_conn('iam', service_type='client')
@rate_limited()
def delete_role_policy(client=None, **kwargs):
    return client.delete_role_policy(**kwargs)


@sts_conn('iam', service_type='client')
@rate_limited()
def put_role_policy(client=None, **kwargs):
    return client.put_role_policy(**kwargs)


@sts_conn('iam', service_type='resource')
@rate_limited()
def all_managed_policies(resource=None, **kwargs):
    managed_policies = {}

    for policy in resource.policies.all():
        for attached_role in policy.attached_roles.all():
            policy_dict = {
                "name": policy.policy_name,
                "arn": policy.arn,
                "version": policy.default_version_id
            }

            if attached_role.arn not in managed_policies:
                managed_policies[attached_role.arn] = [policy_dict]
            else:
                managed_policies[attached_role.arn].append(policy_dict)

    return managed_policies


@paginated('RoleDetailList')
def _get_account_authorization_role_details(client=None, **kwargs):
    return client.get_account_authorization_details(
        Filter=['Role'],
        **kwargs
    )


@paginated('UserDetailList')
def _get_account_authorization_user_details(client=None, **kwargs):
    return client.get_account_authorization_details(
        Filter=['User'],
        **kwargs
    )


@paginated('GroupDetailList')
def _get_account_authorization_group_details(client=None, **kwargs):
    return client.get_account_authorization_details(
        Filter=['Group'],
        **kwargs
    )


@paginated('Policies')
def _get_account_authorization_local_managed_policies_details(client=None, **kwargs):
    return client.get_account_authorization_details(
        Filter=['LocalManagedPolicy'],
        **kwargs
    )


@paginated('Policies')
def _get_account_authorization_aws_managed_policies_details(client=None, **kwargs):
    return client.get_account_authorization_details(
        Filter=['AWSManagedPolicy'],
        **kwargs
    )


@sts_conn('iam', service_type='client')
@rate_limited()
def get_account_authorization_details(filter=None, client=None, **kwargs):
    possible_filters = ['User', 'Role', 'Group', 'LocalManagedPolicy', 'AWSManagedPolicy']

    if filter not in possible_filters:
        raise InvalidAuthorizationFilterException('Must provide filter value: {}'.format(', '.join(possible_filters)))

    if filter == 'User':
        return _get_account_authorization_user_details(client=client, **kwargs)
    elif filter == 'Role':
        return _get_account_authorization_role_details(client=client, **kwargs)
    elif filter == 'Group':
        return _get_account_authorization_group_details(client=client, **kwargs)
    elif filter == 'LocalManagedPolicy':
        return _get_account_authorization_local_managed_policies_details(client=client, **kwargs)
    elif filter == 'AWSManagedPolicy':
        return _get_account_authorization_aws_managed_policies_details(client=client, **kwargs)


@paginated('Users')
@rate_limited()
def _get_users_for_group(client, **kwargs):
    """Fetch the paginated users attached to the group."""
    return client.get_group(**kwargs)


@sts_conn('iam', service_type='client')
@rate_limited()
def get_group(group_name, users=True, client=None, **kwargs):
    """Get's the IAM Group details.

    :param group_name:
    :param users: Optional -- will return the IAM users that the group is attached to if desired (paginated).
    :param client:
    :param kwargs:
    :return:
    """
    # First, make the initial call to get the details for the group:
    result = client.get_group(GroupName=group_name, **kwargs)

    # If we care about the user details, then fetch them:
    if users:
        if result.get('IsTruncated'):
            kwargs_to_send = {'GroupName': group_name}
            kwargs_to_send.update(kwargs)

            user_list = result['Users']
            kwargs_to_send['Marker'] = result['Marker']

            result['Users'] = user_list + _get_users_for_group(client, **kwargs_to_send)

    else:
        result.pop('Users', None)
        result.pop('IsTruncated', None)
        result.pop('Marker', None)

    return result


@sts_conn('iam', service_type='client')
@paginated('PolicyNames')
@rate_limited()
def list_group_policies(group_name, client=None, **kwargs):
    """Lets the IAM group inline policies for a given group."""
    return client.list_group_policies(GroupName=group_name, **kwargs)


@sts_conn('iam', service_type='client')
@rate_limited()
def get_group_policy_document(group_name, policy_name, client=None, **kwargs):
    """Fetches the specific IAM group inline-policy document."""
    return client.get_group_policy(GroupName=group_name, PolicyName=policy_name, **kwargs)['PolicyDocument']


@sts_conn('iam', service_type='client')
@paginated('AttachedPolicies')
@rate_limited()
def list_attached_group_managed_policies(group_name, client=None, **kwargs):
    """Lists the attached IAM managed policies for a given IAM group."""
    return client.list_attached_group_policies(GroupName=group_name, **kwargs)


@sts_conn('iam', service_type='client')
@paginated('Groups')
@rate_limited()
def list_groups_for_user(user_name, client=None, **kwargs):
    """Lists the IAM groups that is attached to a given IAM user."""
    return client.list_groups_for_user(UserName=user_name, **kwargs)


@sts_conn('iam', service_type='client')
@paginated('ServerCertificateMetadataList')
@rate_limited()
def list_server_certificates(client=None, **kwargs):
    """Lists the IAM Server Certificates (IAM SSL) for a given AWS account."""
    return client.list_server_certificates(**kwargs)


@sts_conn('iam', service_type='client')
@rate_limited()
def get_server_certificate(name, client=None, **kwargs):
    return client.get_server_certificate(ServerCertificateName=name).get('ServerCertificate', {})
