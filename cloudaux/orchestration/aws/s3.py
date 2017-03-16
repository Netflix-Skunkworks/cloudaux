from cloudaux.aws.s3 import get_bucket_region
from cloudaux.aws.s3 import get_bucket_acl
from cloudaux.aws.s3 import get_bucket_lifecycle_configuration
from cloudaux.aws.s3 import get_bucket_logging
from cloudaux.aws.s3 import get_bucket_policy
from cloudaux.aws.s3 import get_bucket_tagging
from cloudaux.aws.s3 import get_bucket_versioning
from cloudaux.aws.s3 import get_bucket_website
from cloudaux.aws.s3 import get_bucket_cors
from cloudaux.aws.s3 import get_bucket_notification_configuration
from cloudaux.aws.s3 import get_bucket_accelerate_configuration
from cloudaux.aws.s3 import get_bucket_replication
from cloudaux.aws.s3 import get_bucket_resource
from cloudaux.aws.s3 import list_bucket_analytics_configurations
from cloudaux.aws.s3 import list_bucket_metrics_configurations
from cloudaux.aws.s3 import list_bucket_inventory_configurations
from cloudaux.orchestration import modify

from botocore.exceptions import ClientError
import logging
import json


logger = logging.getLogger('cloudaux')


def get_grants(bucket_name, include_owner=False, **conn):
    acl = get_bucket_acl(Bucket=bucket_name, **conn)
    grantees = {}
    grantee_ref = {}

    for grant in acl['Grants']:
        grantee = grant['Grantee']

        display_name = grantee.get('DisplayName')
        if display_name == 'None' or display_name == 'null':
            logger.info("Received a bad display name: %s", display_name)

        # Make the grantee based on the canonical ID -- if it's a canonical user:
        if grantee["Type"] == "CanonicalUser":
            gname = grantee["ID"]

            if display_name:
                grantee_ref[gname] = display_name

        # If it's a Group, then use the "URI"
        else:
            gname = grantee["URI"]

        if gname in grantees:
            grantees[gname].append(grant['Permission'])
            grantees[gname] = sorted(grantees[gname])
        else:
            grantees[gname] = [grant['Permission']]

    if include_owner:
        return grantees, grantee_ref, {"ID": acl["Owner"]["ID"]}

    return grantees, grantee_ref


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
            'prefix': rule.get('Prefix'),
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

        if rule.get('AbortIncompleteMultipartUpload'):
            abort_multipart_dict = {}
            abort_multipart = rule['AbortIncompleteMultipartUpload']
            if abort_multipart.get('DaysAfterInitiation'):
                abort_multipart_dict['days'] = abort_multipart['DaysAfterInitiation']
            rule_dict['abort_multipart'] = abort_multipart_dict

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
        versioning['Status'] = result['Status']
    if result.get('MFADelete'):
        versioning['MFADelete'] = result['MFADelete']

    return versioning


def get_website(bucket_name, **conn):
    try:
        result = get_bucket_website(Bucket=bucket_name, **conn)
    except ClientError as e:
        if "NoSuchWebsiteConfiguration" not in str(e):
            raise e
        return None

    website = {}
    if result.get("IndexDocument"):
        website["IndexDocument"] = result["IndexDocument"]
    if result.get("RoutingRules"):
        website["RoutingRules"] = result["RoutingRules"]
    if result.get("RedirectAllRequestsTo"):
        website["RedirectAllRequestsTo"] = result["RedirectAllRequestsTo"]
    if result.get("ErrorDocument"):
        website["ErrorDocument"] = result["ErrorDocument"]

    return website


def get_cors(bucket_name, **conn):
    try:
        result = get_bucket_cors(Bucket=bucket_name, **conn)
    except ClientError as e:
        if "NoSuchCORSConfiguration" not in str(e):
            raise e
        return []

    cors = []
    for rule in result["CORSRules"]:
        cors_rule = {}
        if rule.get("AllowedHeaders"):
            cors_rule["AllowedHeaders"] = rule["AllowedHeaders"]
        if rule.get("AllowedMethods"):
            cors_rule["AllowedMethods"] = rule["AllowedMethods"]
        if rule.get("AllowedOrigins"):
            cors_rule["AllowedOrigins"] = rule["AllowedOrigins"]
        if rule.get("ExposeHeaders"):
            cors_rule["ExposeHeaders"] = rule["ExposeHeaders"]
        if rule.get("MaxAgeSeconds"):
            cors_rule["MaxAgeSeconds"] = rule["MaxAgeSeconds"]

        cors.append(cors_rule)

    return cors


def get_notifications(bucket_name, **conn):
    result = get_bucket_notification_configuration(Bucket=bucket_name, **conn)

    notifications = {}
    if result.get("TopicConfigurations"):
        notifications["TopicConfigurations"] = result["TopicConfigurations"]

    if result.get("QueueConfigurations"):
        notifications["QueueConfigurations"] = result["QueueConfigurations"]

    if result.get("LambdaFunctionConfigurations"):
        notifications["LambdaFunctionConfigurations"] = result["LambdaFunctionConfigurations"]

    return notifications


def get_acceleration(bucket_name, **conn):
    result = get_bucket_accelerate_configuration(Bucket=bucket_name, **conn)

    return result.get("Status")


def get_replication(bucket_name, **conn):
    try:
        result = get_bucket_replication(Bucket=bucket_name, **conn)

    except ClientError as e:
        if "ReplicationConfigurationNotFoundError" not in str(e):
            raise e

        return {}

    return result["ReplicationConfiguration"]


def get_bucket_created(bucket_name, **conn):
    bucket = get_bucket_resource(bucket_name, **conn)

    return str(bucket.creation_date)


def get_bucket_analytics_configurations(bucket_name, **conn):
    return list_bucket_analytics_configurations(Bucket=bucket_name, **conn)


def get_bucket_metrics_configurations(bucket_name, **conn):
    return list_bucket_metrics_configurations(Bucket=bucket_name, **conn)


def get_bucket_inventory_configurations(bucket_name, **conn):
    return list_bucket_inventory_configurations(Bucket=bucket_name, **conn)


def get_bucket(bucket_name, output='camelized', include_created=False, **conn):
    """
    Orchestrates all the calls required to fully build out an S3 bucket in the following format:
    
    {
        "Arn": ...,
        "Owner": ...,
        "Grants": ...,
        "GrantReferences": ...,
        "LifecycleRules": ...,
        "Logging": ...,
        "Policy": ...,
        "Tags": ...,
        "Versioning": ...,
        "Website": ...,
        "Cors": ...,
        "Notifications": ...,
        "Acceleration": ...,
        "Replication": ...,
        "Created": ...,
        "AnalyticsConfigurations": ...,
        "MetricsConfigurations": ...,
        "InventoryConfigurations": ...,
        "_version": 5
    }

    NOTE: "GrantReferences" is an ephemeral field that is not guaranteed to be consistent -- do not base logic off of it
    
    :param include_created:
    :param bucket_name: str bucket name
    :param output: Determines whether keys should be returned camelized or underscored.
    :param conn: dict containing enough information to make a connection to the desired account.
    Must at least have 'assume_role' key.
    :return: dict containing a fully built out bucket.
    """
    region = get_bucket_region(Bucket=bucket_name, **conn)
    if not region:
        return modify(dict(Error='Unauthorized'), format=output)

    conn['region'] = region

    grants, grant_refs, owner = get_grants(bucket_name, include_owner=True, **conn)

    result = {
        'arn': "arn:aws:s3:::{name}".format(name=bucket_name),
        'grants': grants,
        'grant_references': grant_refs,
        'owner': owner,
        'lifecycle_rules': get_lifecycle(bucket_name, **conn),
        'logging': get_logging(bucket_name, **conn),
        'policy': get_policy(bucket_name, **conn),
        'region': region,
        'tags': get_tags(bucket_name, **conn),
        'versioning': get_versioning(bucket_name, **conn),
        'website': get_website(bucket_name, **conn),
        'cors': get_cors(bucket_name, **conn),
        'notifications': get_notifications(bucket_name, **conn),
        'acceleration': get_acceleration(bucket_name, **conn),
        'replication': get_replication(bucket_name, **conn),
        'analytics_configurations': get_bucket_analytics_configurations(bucket_name, **conn),
        'metrics_configurations': get_bucket_metrics_configurations(bucket_name, **conn),
        'inventory_configurations': get_bucket_inventory_configurations(bucket_name, **conn),
        '_version': 5
    }

    if include_created:
        result["Created"] = get_bucket_created(bucket_name, **conn)

    return modify(result, format=output)
