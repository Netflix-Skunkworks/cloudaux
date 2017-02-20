from cloudaux.aws.sts import sts_conn
from cloudaux.aws.decorators import rate_limited, paginated
from botocore.exceptions import ClientError


S3_REGION_MAPPING = dict(
    APNortheast='ap-northeast-1',
    APSoutheast='ap-southeast-1',
    APSoutheast2='ap-southeast-2',
    DEFAULT='', 
    EU='eu-west-1',
    SAEast='sa-east-1',
    USWest='us-west-1',
    USWest2='us-west-2')


@sts_conn('s3')
@rate_limited()
def list_buckets(client=None, **kwargs):
    return client.list_buckets()


@sts_conn('s3')
@rate_limited()
def get_bucket_location(client=None, **kwargs):
    """
    Bucket='string'
    """
    return client.get_bucket_location(**kwargs)


@sts_conn('s3')
@rate_limited()
def get_bucket_acl(client=None, **kwargs):
    """
    Bucket='string'
    """
    return client.get_bucket_acl(**kwargs)


@sts_conn('s3')
@rate_limited()
def get_bucket_policy(client=None, **kwargs):
    """
    Bucket='string'
    """
    return client.get_bucket_policy(**kwargs)


@sts_conn('s3')
@rate_limited()
def get_bucket_tagging(client=None, **kwargs):
    """
    Bucket='string'
    """
    return client.get_bucket_tagging(**kwargs)


@sts_conn('s3')
@rate_limited()
def get_bucket_versioning(client=None, **kwargs):
    """
    Bucket='string'
    """
    return client.get_bucket_versioning(**kwargs)


@sts_conn('s3')
@rate_limited()
def get_bucket_lifecycle_configuration(client=None, **kwargs):
    """
    Bucket='string'
    """
    return client.get_bucket_lifecycle_configuration(**kwargs)
    

@sts_conn('s3')
@rate_limited()
def get_bucket_logging(client=None, **kwargs):
    """
    Bucket='string'
    """
    return client.get_bucket_logging(**kwargs)


@sts_conn('s3')
@rate_limited()
def get_bucket_website(client=None, **kwargs):
    """
    Bucket='string'
    """
    return client.get_bucket_website(**kwargs)


@sts_conn('s3')
@rate_limited()
def get_bucket_cors(client=None, **kwargs):
    """
    Bucket='string'
    """
    return client.get_bucket_cors(**kwargs)


@sts_conn('s3')
@rate_limited()
def get_bucket_notification_configuration(client=None, **kwargs):
    """
    Bucket='string'
    """
    return client.get_bucket_notification_configuration(**kwargs)


@sts_conn('s3')
@rate_limited()
def get_bucket_accelerate_configuration(client=None, **kwargs):
    """
    Bucket='string'
    """
    return client.get_bucket_accelerate_configuration(**kwargs)


@sts_conn('s3')
@rate_limited()
def get_bucket_replication(client=None, **kwargs):
    """
    Bucket='string'
    """
    return client.get_bucket_replication(**kwargs)


@sts_conn('s3')
@paginated('AnalyticsConfigurationList', request_pagination_marker="ContinuationToken",
           response_pagination_marker="NextContinuationToken")
@rate_limited()
def list_bucket_analytics_configurations(client=None, **kwargs):
    """
    Bucket='string'
    """
    result = client.list_bucket_analytics_configurations(**kwargs)
    if not result.get("AnalyticsConfigurationList"):
        result.update({"AnalyticsConfigurationList": []})

    return result


@sts_conn('s3')
@paginated('MetricsConfigurationList', request_pagination_marker="ContinuationToken",
           response_pagination_marker="NextContinuationToken")
@rate_limited()
def list_bucket_metrics_configurations(client=None, **kwargs):
    """
    Bucket='string'
    """
    result = client.list_bucket_metrics_configurations(**kwargs)
    if not result.get("MetricsConfigurationList"):
        result.update({"MetricsConfigurationList": []})

    return result


@sts_conn('s3')
@paginated('InventoryConfigurationList', request_pagination_marker="ContinuationToken",
           response_pagination_marker="NextContinuationToken")
@rate_limited()
def list_bucket_inventory_configurations(client=None, **kwargs):
    """
    Bucket='string'
    """
    result = client.list_bucket_inventory_configurations(**kwargs)
    if not result.get("InventoryConfigurationList"):
        result.update({"InventoryConfigurationList": []})

    return result


@sts_conn('s3', service_type='resource')
@rate_limited()
def get_bucket_resource(bucket_name, resource=None, **kwargs):
    return resource.Bucket(bucket_name)


def get_bucket_region(**kwargs):
    # Some s3 buckets do not allow viewing of details. We do not want to
    # throw an error in this case because we still want to see that the
    # bucket exists
    try:
        result = get_bucket_location(**kwargs)
        location = result['LocationConstraint']
    except ClientError as e:
        if 'AccessDenied' not in str(e):
            raise e
        return None

    if not location:
        return 'us-east-1'

    return S3_REGION_MAPPING.get(location, location)
