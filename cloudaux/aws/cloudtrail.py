"""
Api for communication with the AWS.

This is similar to cloud aux like functions, that supports cloud trails
"""

from cloudaux.aws.decorators import paginated, rate_limited
from cloudaux.aws.sts import sts_conn


@sts_conn('cloudtrail', service_type='client')
@paginated("Events", request_pagination_marker="NextToken", response_pagination_marker="NextToken")
@rate_limited()
def lookup_events(client=None, **kwargs):
    """
    Method fetch events from aws
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudtrail.html#CloudTrail.Client.lookup_events  # noqa E501
    """
    return client.lookup_events(**kwargs)


@sts_conn('cloudtrail', service_type='client')
@paginated("trailList")
@rate_limited()
def describe_trails(client=None, **kwargs):
    """
    Method fetches all trail with descriptions
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudtrail.html#CloudTrail.Client.describe_trails # noqa E501
    """
    return client.describe_trails(**kwargs)


@sts_conn('cloudtrail', service_type='client')
@paginated("Trails")
@rate_limited()
def list_trails(client=None, **kwargs):
    """
    Method fetches all cloudtrail's
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudtrail.html#CloudTrail.Client.list_trails # noqa E501
    """
    return client.list_trails(**kwargs)
