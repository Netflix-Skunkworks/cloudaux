from cloudaux.aws.sts import sts_conn
from cloudaux.aws.decorators import rate_limited, paginated


@sts_conn('events')
@paginated('Rules', request_pagination_marker="NextToken",
           response_pagination_marker="NextToken")
@rate_limited()
def list_rules(client=None, **kwargs):
    """
    NamePrefix='string'
    """
    result = client.list_rules(**kwargs)
    if not result.get("Rules"):
        result.update({"Rules": []})

    return result


@sts_conn('events')
@rate_limited()
def describe_rule(client=None, **kwargs):
    """
    Name='string'
    """
    return client.describe_rule(**kwargs)


@sts_conn('events')
@paginated('Targets', request_pagination_marker="NextToken",
           response_pagination_marker="NextToken")
@rate_limited()
def list_targets_by_rule(client=None, **kwargs):
    """
    Rule='string'
    """
    result = client.list_targets_by_rule(**kwargs)
    if not result.get("Targets"):
        result.update({"Targets": []})

    return result
