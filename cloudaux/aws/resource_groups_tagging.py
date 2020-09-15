"""
Funcions for fetching resources using resourcegroupstaggingapi
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/resourcegroupstaggingapi.html
"""
from cloudaux import sts_conn
from cloudaux.aws.decorators import paginated


@sts_conn('resourcegroupstaggingapi', service_type='client')
@paginated('ResourceTagMappingList')
def get_resources(client, **kwargs):
    """
    Fetches the paginated list of  resources and their tags.
    list of supported resources:
    https://docs.aws.amazon.com/ARG/latest/userguide/supported-resources.html
    """
    return client.get_resources(**kwargs)
