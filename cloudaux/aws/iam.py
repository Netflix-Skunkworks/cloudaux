from cloudaux.aws.sts import sts_conn
from cloudaux.aws.decorators import rate_limited
from cloudaux.aws.decorators import paginated
from joblib import Parallel, delayed
import botocore.exceptions


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
            'path': ip['Path'],
            'instance_profile_name': ip['InstanceProfileName'],
            'create_date': ip['CreateDate'].strftime('%Y-%m-%dT%H:%M:%SZ'),
            'instance_profile_id': ip['InstanceProfileId'],
            'arn': ip['Arn']
        } for ip in instance_profiles
    ]


@sts_conn('iam', service_type='client')
@rate_limited()
def get_role_managed_policy_documents(role, client=None, **kwargs):
    """Retrieve the currently active policy version document for every managed policy that is attached to the role."""
    policies = get_role_managed_policies(role, force_client=client)

    policy_names = (policy['name'] for policy in policies)
    delayed_gmpd_calls = (delayed(get_managed_policy_document)(policy['arn'], force_client=client) for policy in policies)
    policy_documents = Parallel(n_jobs=20, backend="threading")(delayed_gmpd_calls)

    return dict(zip(policy_names, policy_documents))


@sts_conn('iam', service_type='client')
@rate_limited()
def get_managed_policy_document(policy_arn, client=None, **kwargs):
    """Retrieve the currently active (i.e. 'default') policy version document for a policy."""
    policy_metadata = client.get_policy(PolicyArn=policy_arn)
    policy_document = client.get_policy_version(PolicyArn=policy_arn,
                                                VersionId=policy_metadata['Policy']['DefaultVersionId'])
    return policy_document['PolicyVersion']['Document']

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
    if not filter:
        raise Exception('Must provide filter value')

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
