from cloudaux.aws.s3 import get_bucket_region
from cloudaux.aws.s3 import get_bucket_acl
from cloudaux.aws.s3 import get_bucket_lifecycle_configuration
from cloudaux.aws.s3 import get_bucket_logging
from cloudaux.aws.s3 import get_bucket_policy
from cloudaux.aws.s3 import get_bucket_tagging
from cloudaux.aws.s3 import get_bucket_versioning
from cloudaux.orchestration import modify

from botocore.exceptions import ClientError
import logging
import json


logger = logging.getLogger('cloudaux')


def get_grants(bucket_name, **conn):
    acl = get_bucket_acl(Bucket=bucket_name, **conn)
    grantees = {}

    for grant in acl['Grants']:
        grantee = grant['Grantee']

        display_name = grantee.get('DisplayName')
        if display_name == 'None' or display_name == 'null':
            logger.info("Received a bad display name: %s", display_name)

        if display_name is None:
            gname = grantee.get('URI')
        else:
            gname = grantee['DisplayName']

        if gname in grantees:
            grantees[gname].append(grant['Permission'])
            grantees[gname] = sorted(grantees[gname])
        else:
            grantees[gname] = [grant['Permission']]

    return grantees


def get_lifecycle(bucket_name, **conn):
    try:
        result = get_bucket_lifecycle_configuration(Bucket=bucket_name, **conn)
    except ClientError as e:
        if 'NoSuchLifecycleConfiguration' not in str(e):
            raise e
        return []
    
    lifecycle_rules = []
    rules = result['Rules']
    for rule in rules:
        rule_dict = {
            'id': rule['ID'],
            'status': rule['Status'],
            'prefix': rule['Prefix'],
        }

        if rule.get('Transitions'):
            transition_list = []
            for transition in rule['Transitions']:
                transition_dict = {}
                if transition.get('Days'):
                    transition_dict['days'] = transition['Days']
                if transition.get('Date'):
                    transition_dict['date'] = transition['Date'].strftime('%Y-%m-%dT%H:%M:%SZ')
                transition_dict['storage_class'] = transition['StorageClass']
                transition_list.append(transition_dict)

            rule_dict['transitions'] = transition_list

        if rule.get('Expiration'):
            expiration_dict = {}
            expiration = rule['Expiration']
            if expiration.get('Days'):
                expiration_dict['days'] = expiration['Days']
            if expiration.get('Date'):
                expiration_dict['date'] = expiration['Date'].strftime('%Y-%m-%dT%H:%M:%SZ')

            rule_dict['expiration'] = expiration_dict

        lifecycle_rules.append(rule_dict)
    return lifecycle_rules


def get_logging(bucket_name, **conn):
    result = get_bucket_logging(Bucket=bucket_name, **conn)
    
    logging_dict = {}
    if result.get('LoggingEnabled'):
        logging = result['LoggingEnabled']
        logging_dict['enabled'] = True
        logging_dict['prefix'] = logging['TargetPrefix']
        logging_dict['target'] = logging['TargetBucket']
        grant_list = []
        if logging.get('TargetGrants'):
            for grant in logging['TargetGrants']:
                grant_dict = {}
                grant_dict['permission'] = grant['Permission']
                grantee = grant['Grantee']
                grant_dict['type'] = grantee['Type']
                if grantee['Type'] == 'CanonicalUser':
                    grant_dict['display_name'] = grantee['DisplayName']
                elif grantee['Type'] == 'Group':
                    grant_dict['group_uri'] = grantee['URI']
                else:
                    grant_dict['email'] = grantee['EmailAddress']
            grant_list.append(grant_dict)

        logging_dict['grants'] = grant_list

    return logging_dict


def get_policy(bucket_name, **conn):
    try:
        result = get_bucket_policy(Bucket=bucket_name, **conn)
        return json.loads(result['Policy'])
    except ClientError as e:
        if 'NoSuchBucketPolicy' not in str(e):
            raise e
        return None


def get_tags(bucket_name, **conn):
    try:
        result = get_bucket_tagging(Bucket=bucket_name, **conn)
    except ClientError as e:
        if 'NoSuchTagSet' not in str(e):
            raise e
        return None

    return {tag['Key']: tag['Value'] for tag in result['TagSet']}


def get_versioning(bucket_name, **conn):
    result = get_bucket_versioning(Bucket=bucket_name, **conn)
    versioning = {}
    if result.get('Status'):
        versioning['Versioning'] = result['Status']
    if result.get('MFADelete'):
        versioning['MFADelete'] = result['MFADelete']

    return versioning


def get_bucket(bucket_name, output='camelized', **conn):
    """
    Orchestrates all the calls required to fully build out an S3 bucket in the following format:
    
    {
        "Arn": ...,
        "Grants": ...,
        "LifecycleRules": ...,
        "Logging": ...,
        "Policy": ...,
        "Tags": ...,
        "Versioning": ...,
        "_version": 1
    }
    
    :param bucket_name: str bucket name 
    :param output: Determines whether keys should be returned camelized or underscored.
    :param conn: dict containing enough information to make a connection to the desired account.
    Must at least have 'assume_role' key.
    :return: dict containing a fully built out bucket.
    """
    region = get_bucket_region(Bucket=bucket_name, **conn)
    if not region:
        region = 'us-east-1'
        return modify(dict(Error='Unauthorized'), format=output)

    conn['region'] = region

    result = {
       'arn': "arn:aws:s3:::{name}".format(name=bucket_name),
       'grants': get_grants(bucket_name, **conn),
       'lifecycle_rules': get_lifecycle(bucket_name, **conn),
       'logging': get_logging(bucket_name, **conn),
       'policy': get_policy(bucket_name, **conn),
       'region': region,
       'tags': get_tags(bucket_name, **conn),
       'versioning': get_versioning(bucket_name, **conn),
       '_version': 1
    }

    return modify(result, format=output)