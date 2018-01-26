from cloudaux.aws.sqs import get_queue_url, get_queue_attributes, list_queue_tags, list_dead_letter_source_queues
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags

import logging

from cloudaux.orchestration.aws import ARN

logger = logging.getLogger('cloudaux')

registry = FlagRegistry()
FLAGS = Flags('BASE', 'TAGS', 'DEAD_LETTER_SOURCE_QUEUES')


@registry.register(flag=FLAGS.TAGS, key='tags')
def get_sqs_tags(sqs_queue, **conn):
    return list_queue_tags(QueueUrl=sqs_queue["QueueUrl"], **conn)


@registry.register(flag=FLAGS.DEAD_LETTER_SOURCE_QUEUES, key='dead_letter_source_queues')
def get_dead_letter_queues(sqs_queue, **conn):
    return list_dead_letter_source_queues(QueueUrl=sqs_queue["QueueUrl"], **conn)


@registry.register(flag=FLAGS.BASE)
def get_base(sqs_queue, **conn):
    sqs_queue["Attributes"] = get_queue_attributes(QueueUrl=sqs_queue["QueueUrl"], AttributeNames=["All"], **conn)

    # Get the Queue name:
    name = ARN(sqs_queue["Attributes"]["QueueArn"]).parsed_name

    return {
        'arn': sqs_queue["Attributes"]["QueueArn"],
        'url': sqs_queue["QueueUrl"],
        'name': name,
        'region': conn['region'],
        'attributes': sqs_queue["Attributes"],
        '_version': 1
    }


@modify_output
def get_queue(queue, flags=FLAGS.ALL, **conn):
    """
    Orchestrates all the calls required to fully fetch details about an SQS Queue:
    
    {
        "Arn": ...,
        "Region": ...,
        "Name": ...,
        "Url": ...,
        "Attributes": ...,
        "Tags": ...,
        "DeadLetterSourceQueues": ...,
        "_version": 1
    }

    :param queue: Either the queue name OR the queue url
    :param flags: By default, set to ALL fields.
    :param conn: dict containing enough information to make a connection to the desired account. Must at least have
                 'assume_role' key.
    :return: dict containing a fully built out SQS queue.
    """
    # Check if this is a Queue URL or a queue name:
    if queue.startswith("https://") or queue.startswith("http://"):
        queue_name = queue
    else:
        queue_name = get_queue_url(QueueName=queue, **conn)

    sqs_queue = {"QueueUrl": queue_name}

    return registry.build_out(flags, sqs_queue, **conn)
