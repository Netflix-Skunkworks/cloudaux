# CloudAux CloudWatch Events

CloudAux can build out a JSON object describing an AWS CloudWatch Event configuration.

## Example

    from cloudaux.orchestration.aws.events import get_event

    conn = dict(
        account_number='111111111111',
        assume_role='SecurityMonkey')

    event = get_event('SomeCloudWatchEventRule', **conn)

    print(json.dumps(event, indent=2, sort_keys=True))

    {
        "Region": "us-east-1",
        "_version": 1,
        "State": "ENABLED",
        "Description": "ScheduledRule",
        "Targets": [
            {
                "Arn": "arn:aws:lambda:us-east-1:111111111111:function:MyLambdaFunction",
                "Id": "SomeFunction"
            }
        ],
        "Name": "SomeCloudWatchEventRule",
        "Arn": "arn:aws:events:us-east-1:111111111111:rule/SomeCloudWatchEventRule",
        "Rule": "rate(4 hours)"
    }


## Flags

The `get_event` command accepts flags describing what parts of the structure to build out.

    from cloudaux.orchestration.aws.events import FLAGS

    some_fields = FLAGS.DESCRIBE | FLAGS.TARGETS
    vault = get_event('SomeCloudWatchEventRule', flags=desired_flags, **conn)

If not provided, `get_event` assumes `FLAGS.ALL`, which recommended for most use cases.

- `BASE` - ARN, Name, Region, and Cloudaux implementation number
- `DESCRIPTION` - The event Description, State, and the rule Schedule Expression --or-- the Event Pattern.
- `TARGETS` - The CloudWatch Event Targets
- `ALL` - all items
