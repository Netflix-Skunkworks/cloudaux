# CloudAux AWS SQS

CloudAux can build out a JSON object describing an SQS Queue.

## Example

    from cloudaux.orchestration.aws.sqs import get_queue, FLAGS

    conn = dict(
        account_number='012345678910',
        assume_role='SecurityMonkey',
        region="us-west-2")

    queue = get_queue('MyQueue', flags=FLAGS.ALL, **conn)
    # Or the queue URL:
    # queue = get_queue('https://sqs.us-west-2.amazonaws.com/012345678910/MyQueue', flags=FLAGS.ALL, **conn)

    # The flags parameter is optional but allows the user to indicate that
    # only a subset of the full item description is required.
    # SQS Flag Options are:
    #   BASE, TAGS, DEAD_LETTER_SOURCE_QUEUES, ALL (default)
    # For instance: flags=FLAGS.TAGS | FLAGS.DEAD_LETTER_SOURCE_QUEUES

    print(json.dumps(queue, indent=2, sort_keys=True))

    {
        "_version": 1,
        "Region": "us-west-2",
        "Name": "MyQueue",
        "Arn": "arn:aws:sqs:us-west-2:012345678910:MyQueue",
        "Url": "https://sqs.us-west-2.amazonaws.com/012345678910/MyQueue"
        "DeadLetterSourceQueues": [
            "https://sqs.us-west-2.amazonaws.com/012345678910/MyDeadLetterQueue"   
        ],
        "Tags": {
            "TagKey": "TagValue"
        },
        "Attributes": {
            "MessageRetentionPeriod": "345600",
            "CreatedTimestamp": "1516728270",
            "ApproximateNumberOfMessagesNotVisible": "0",
            "ApproximateNumberOfMessages": "0",
            "ApproximateNumberOfMessagesDelayed": "0",
            "DelaySeconds": "0",
            "QueueArn": "arn:aws:sqs:us-west-2:012345678910:MyQueue",
            "MaximumMessageSize": "262144",
            "VisibilityTimeout": "30",
            "LastModifiedTimestamp": "1516746742",
            "ReceiveMessageWaitTimeSeconds": "0"
        }
    }
    
    # NOTE: `Attributes` is defaulted to "All", so it will return all attributes boto currently supports.


## Flags

The `get_queue` command accepts flags describing what parts of the structure to build out.

If not provided, `get_queue` assumes `FLAGS.ALL`.
