from cloudaux.aws.sts import sts_conn
from cloudaux.aws.decorators import rate_limited, paginated
from botocore.exceptions import ClientError


@sts_conn('events')
@rate_limited()
def describe_event_bus(client=None, **kwargs):
    return client.describe_event_bus()

