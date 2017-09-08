"""
.. module: cloudaux.aws.sns
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Patrick Kelley <patrick@netflix.com>
"""
from cloudaux.aws.sts import sts_conn
from cloudaux.aws.decorators import rate_limited, paginated


@sts_conn('sns')
@rate_limited()
def add_permission(client=None, **kwargs):
    return client.add_permission(**kwargs)


@sts_conn('sns')
@rate_limited()
def check_if_phone_number_is_opted_out(client=None, **kwargs):
    return client.check_if_phone_number_is_opted_out(**kwargs)['isOptedOut']


@sts_conn('sns')
@rate_limited()
def confirm_subscription(client=None, **kwargs):
    return client.confirm_subscription(**kwargs)['SubscriptionArn']


@sts_conn('sns')
@rate_limited()
def create_platform_application(client=None, **kwargs):
    return client.create_platform_application(**kwargs)['PlatformApplicationArn']


@sts_conn('sns')
@rate_limited()
def create_platform_endpoint(client=None, **kwargs):
    return client.create_platform_endpoint(**kwargs)['EndpointArn']


@sts_conn('sns')
@rate_limited()
def create_topic(client=None, **kwargs):
    return client.create_topic(**kwargs)['TopicArn']


@sts_conn('sns')
@rate_limited()
def delete_endpoint(client=None, **kwargs):
    return client.delete_endpoint(**kwargs)


@sts_conn('sns')
@rate_limited()
def delete_platform_application(client=None, **kwargs):
    return client.delete_platform_application(**kwargs)


@sts_conn('sns')
@rate_limited()
def delete_topic(client=None, **kwargs):
    return client.delete_topic(**kwargs)


@sts_conn('sns')
@rate_limited()
def get_endpoint_attributes(client=None, **kwargs):
    return client.get_endpoint_attributes(**kwargs)['Attributes']


@sts_conn('sns')
@rate_limited()
def get_platform_application_attributes(client=None, **kwargs):
    return client.get_platform_application_attributes(**kwargs)['Attributes']


@sts_conn('sns')
@rate_limited()
def get_sms_attributes(client=None, **kwargs):
    return client.get_sms_attributes(**kwargs)['attributes']


@sts_conn('sns')
@rate_limited()
def get_subscription_attributes(client=None, **kwargs):
    return client.get_subscription_attributes(**kwargs)['Attributes']


@sts_conn('sns')
@rate_limited()
def get_topic_attributes(client=None, **kwargs):
    return client.get_topic_attributes(**kwargs)['Attributes']


@sts_conn('sns')
@paginated('Endpoints', request_pagination_marker="NextToken", response_pagination_marker="NextToken")
@rate_limited()
def list_endpoints_by_platform_application(client=None, **kwargs):
    return client.list_endpoints_by_platform_application(**kwargs)


@sts_conn('sns')
@paginated('phoneNumbers', request_pagination_marker="nextToken", response_pagination_marker="nextToken")
@rate_limited()
def list_phone_numbers_opted_out(client=None, **kwargs):
    return client.list_phone_numbers_opted_out(**kwargs)


@sts_conn('sns')
@paginated('PlatformApplications', request_pagination_marker="NextToken", response_pagination_marker="NextToken")
@rate_limited()
def list_platform_applications(client=None, **kwargs):
    return client.list_platform_applications(**kwargs)


@sts_conn('sns')
@paginated('Subscriptions', request_pagination_marker="NextToken", response_pagination_marker="NextToken")
@rate_limited()
def list_subscriptions(client=None, **kwargs):
    return client.list_subscriptions(**kwargs)


@sts_conn('sns')
@paginated('Subscriptions', request_pagination_marker="NextToken", response_pagination_marker="NextToken")
@rate_limited()
def list_subscriptions_by_topic(client=None, **kwargs):
    return client.list_subscriptions_by_topic(**kwargs)


@sts_conn('sns')
@pagiated('Topics', request_pagination_marker="NextToken", response_pagination_marker="NextToken")
@rate_limited()
def list_topics(client=None, **kwargs):
    return client.list_topics(**kwargs)


@sts_conn('sns')
@rate_limited()
def opt_in_phone_number(client=None, **kwargs):
    return client.opt_in_phone_number(**kwargs)


@sts_conn('sns')
@rate_limited()
def publish(client=None, **kwargs):
    return client.publish(**kwargs)['MessageId']


@sts_conn('sns')
@rate_limited()
def remove_permission(client=None, **kwargs):
    return client.remove_permission(**kwargs)


@sts_conn('sns')
@rate_limited()
def set_endpoint_attributes(client=None, **kwargs):
    return client.set_endpoint_attributes(**kwargs)


@sts_conn('sns')
@rate_limited()
def set_platform_application_attributes(client=None, **kwargs):
    return client.set_platform_application_attributes(**kwargs)


@sts_conn('sns')
@rate_limited()
def set_sms_attributes(client=None, **kwargs):
    return client.set_sms_attributes(**kwargs)


@sts_conn('sns')
@rate_limited()
def set_subscription_attributes(client=None, **kwargs):
    return client.set_subscription_attributes(**kwargs)


@sts_conn('sns')
@rate_limited()
def set_topic_attributes(client=None, **kwargs):
    return client.set_topic_attributes(**kwargs)


@sts_conn('sns')
@rate_limited()
def subscribe(client=None, **kwargs):
    return client.subscribe(**kwargs)['SubscriptionArn']


@sts_conn('sns')
@rate_limited()
def unsubscribe(client=None, **kwargs):
    return client.unsubscribe(**kwargs)