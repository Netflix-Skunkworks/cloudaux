"""
.. module: cloudaux.aws.sqs
    :platform: Unix
    :copyright: (c) 2015 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
.. moduleauthor:: Patrick Kelley <patrick@netflix.com>
"""
from cloudaux.aws.sts import sts_conn
from cloudaux.aws.decorators import rate_limited


@sts_conn('sqs')
@rate_limited()
def add_permission(client=None, **kwargs):
    return client.add_permission(**kwargs)


@sts_conn('sqs')
@rate_limited()
def change_message_visibility(client=None, **kwargs):
    return client.change_message_visibility(**kwargs)


@sts_conn('sqs')
@rate_limited()
def create_queue(client=None, **kwargs):
    return client.create_queue(**kwargs)['QueueUrl']


@sts_conn('sqs')
@rate_limited()
def delete_message(client=None, **kwargs):
    return client.delete_message(**kwargs)


@sts_conn('sqs')
@rate_limited()
def delete_message_batch(client=None, **kwargs):
    return client.delete_message_batch(**kwargs)


@sts_conn('sqs')
@rate_limited()
def delete_queue(client=None, **kwargs):
    return client.delete_queue(**kwargs)


@sts_conn('sqs')
@rate_limited()
def get_queue_attributes(client=None, **kwargs):
    return client.get_queue_attributes(**kwargs)['Attributes']


@sts_conn('sqs')
@rate_limited()
def get_queue_url(client=None, **kwargs):
    return client.get_queue_url(**kwargs)['QueueUrl']


@sts_conn('sqs')
@rate_limited()
def list_dead_letter_source_queues(client=None, **kwargs):
    return client.list_dead_letter_source_queues(**kwargs)['queueUrls']


@sts_conn('sqs')
@rate_limited()
def list_queues(client=None, **kwargs):
    return client.list_queues(**kwargs)['QueueUrls']


@sts_conn('sqs')
@rate_limited()
def purge_queue(client=None, **kwargs):
    return client.purge_queue(**kwargs)


@sts_conn('sqs')
@rate_limited()
def receive_message(client=None, **kwargs):
    return client.receive_message(**kwargs)['Messages']


@sts_conn('sqs')
@rate_limited()
def remove_permission(client=None, **kwargs):
    return client.remove_permission(**kwargs)


@sts_conn('sqs')
@rate_limited()
def send_message(client=None, **kwargs):
    return client.send_message(**kwargs)


@sts_conn('sqs')
@rate_limited()
def send_message_batch(client=None, **kwargs):
    return client.send_message_batch(**kwargs)


@sts_conn('sqs')
@rate_limited()
def set_queue_attributes(client=None, **kwargs):
    return client.set_queue_attributes(**kwargs)
