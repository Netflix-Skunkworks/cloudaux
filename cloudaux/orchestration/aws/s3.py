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
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags

from botocore.exceptions import ClientError
import logging
import json

logger = logging.getLogger('cloudaux')

registry = FlagRegistry()
FLAGS = Flags('BASE', 'GRANTS', 'GRANT_REFERENCES', 'OWNER', 'LIFECYCLE',
              'LOGGING', 'POLICY', 'TAGS', 'VERSIONING', 'WEBSITE', 'CORS',
              'NOTIFICATIONS', 'ACCELERATION', 'REPLICATION', 'ANALYTICS',
              'METRICS', 'INVENTORY', 'CREATED_DATE')


@registry.register(
    flag=(FLAGS.GRANTS, FLAGS.GRANT_REFERENCES, FLAGS.OWNER),
    key=('grants', 'grant_references', 'owner'))
def get_grants(bucket_name, include_owner=True, **conn):
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


@registry.register(flag=FLAGS.LIFECYCLE, key='lifecycle_rules')
def get_lifecycle(bucket_name, **conn):
    try:
        result = get_bucket_lifecycle_configuration(Bucket=bucket_name, **conn)
    except ClientError as e:
        if 'NoSuchLifecycleConfiguration' not in str(e):
            raise e
        return []

    for rule in result['Rules']:
        # Save all dates as a Proper ISO 8601 String:
        for transition in rule.get('Transitions', []):
            if 'Date' in transition:
                transition['Date'] = transition["Date"].replace(tzinfo=None, microsecond=0).isoformat() + "Z"

        if rule.get("Expiration"):
            if 'Date' in rule["Expiration"]:
                rule["Expiration"]["Date"] = \
                    rule["Expiration"]["Date"].replace(tzinfo=None, microsecond=0).isoformat() + "Z"

    return result['Rules']


@registry.register(flag=FLAGS.LOGGING, key='logging')
def get_logging(bucket_name, **conn):
    result = get_bucket_logging(Bucket=bucket_name, **conn)

    logging_dict = {}
    if result.get('LoggingEnabled'):
        logging = result['LoggingEnabled']
        logging_dict['Enabled'] = True
        logging_dict['Prefix'] = logging['TargetPrefix']
        logging_dict['Target'] = logging['TargetBucket']
        grant_list = []
        if logging.get('TargetGrants'):
            for grant in logging['TargetGrants']:
                grant_dict = {}
                grant_dict['Permission'] = grant['Permission']
                grantee = grant['Grantee']
                grant_dict['Type'] = grantee['Type']
                if grantee['Type'] == 'CanonicalUser':
                    grant_dict['DisplayName'] = grantee['DisplayName']
                elif grantee['Type'] == 'Group':
                    grant_dict['GroupUri'] = grantee['URI']
                else:
                    grant_dict['Email'] = grantee['EmailAddress']
            grant_list.append(grant_dict)

        logging_dict['Grants'] = grant_list

    return logging_dict


@registry.register(flag=FLAGS.POLICY, key='policy')
def get_policy(bucket_name, **conn):
    try:
        result = get_bucket_policy(Bucket=bucket_name, **conn)
        return json.loads(result['Policy'])
    except ClientError as e:
        if 'NoSuchBucketPolicy' not in str(e):
            raise e
        return None


@registry.register(flag=FLAGS.TAGS, key='tags')
def get_tags(bucket_name, **conn):
    try:
        result = get_bucket_tagging(Bucket=bucket_name, **conn)
    except ClientError as e:
        if 'NoSuchTagSet' not in str(e):
            raise e
        return None

    return {tag['Key']: tag['Value'] for tag in result['TagSet']}


@registry.register(flag=FLAGS.VERSIONING, key='versioning')
def get_versioning(bucket_name, **conn):
    result = get_bucket_versioning(Bucket=bucket_name, **conn)
    versioning = {}
    if result.get('Status'):
        versioning['Status'] = result['Status']
    if result.get('MFADelete'):
        versioning['MFADelete'] = result['MFADelete']

    return versioning


@registry.register(flag=FLAGS.WEBSITE, key='website')
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


@registry.register(flag=FLAGS.CORS, key='cors')
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


@registry.register(flag=FLAGS.NOTIFICATIONS, key='notifications')
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


@registry.register(flag=FLAGS.ACCELERATION, key='acceleration')
def get_acceleration(bucket_name, **conn):
    result = get_bucket_accelerate_configuration(Bucket=bucket_name, **conn)
    return result.get("Status")


@registry.register(flag=FLAGS.REPLICATION, key='replication')
def get_replication(bucket_name, **conn):
    try:
        result = get_bucket_replication(Bucket=bucket_name, **conn)
    except ClientError as e:
        if "ReplicationConfigurationNotFoundError" not in str(e):
            raise e
        return {}
    return result["ReplicationConfiguration"]


@registry.register(flag=FLAGS.CREATED_DATE, key='creation_date')
def get_bucket_created(bucket_name, **conn):
    bucket = get_bucket_resource(bucket_name, **conn)

    # Return the creation date as a Proper ISO 8601 String:
    return bucket.creation_date.replace(tzinfo=None, microsecond=0).isoformat() + "Z"


@registry.register(flag=FLAGS.ANALYTICS, key='analytics_configurations')
def get_bucket_analytics_configurations(bucket_name, **conn):
    return list_bucket_analytics_configurations(Bucket=bucket_name, **conn)


@registry.register(flag=FLAGS.METRICS, key='metrics_configurations')
def get_bucket_metrics_configurations(bucket_name, **conn):
    return list_bucket_metrics_configurations(Bucket=bucket_name, **conn)


@registry.register(flag=FLAGS.INVENTORY, key='inventory_configurations')
def get_bucket_inventory_configurations(bucket_name, **conn):
    return list_bucket_inventory_configurations(Bucket=bucket_name, **conn)


@registry.register(flag=FLAGS.BASE)
def get_base(bucket_name, **conn):
    return {
        'arn': "arn:aws:s3:::{name}".format(name=bucket_name),
        'name': bucket_name,
        'region': conn.get('region'),
        '_version': 9
    }


@modify_output
def get_bucket(bucket_name, include_created=None, flags=FLAGS.ALL ^ FLAGS.CREATED_DATE, **conn):
    """
    Orchestrates all the calls required to fully build out an S3 bucket in the following format:
    
    {
        "Arn": ...,
        "Name": ...,
        "Region": ...,
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
        "CreationDate": ...,
        "AnalyticsConfigurations": ...,
        "MetricsConfigurations": ...,
        "InventoryConfigurations": ...,
        "_version": 9
    }

    NOTE: "GrantReferences" is an ephemeral field that is not guaranteed to be consistent -- do not base logic off of it
    
    :param include_created: legacy param moved to FLAGS.
    :param bucket_name: str bucket name
    :param flags: By default, set to ALL fields except for FLAGS.CREATED_DATE as obtaining that information is a slow
                  and expensive process.
    :param conn: dict containing enough information to make a connection to the desired account. Must at least have
                 'assume_role' key.
    :return: dict containing a fully built out bucket.
    """
    if type(include_created) is bool:
        # coerce the legacy param "include_created" into the flags param.
        if include_created:
            flags = flags | FLAGS.CREATED_DATE
        else:
            flags = flags & ~FLAGS.CREATED_DATE

    region = get_bucket_region(Bucket=bucket_name, **conn)
    if not region:
        return dict(Error='Unauthorized')

    conn['region'] = region
    return registry.build_out(flags, bucket_name, **conn)
