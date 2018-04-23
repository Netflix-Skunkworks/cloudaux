from cloudaux.aws.decorators import rate_limited, paginated
from cloudaux.aws.sts import sts_conn


@sts_conn('ec2')
@paginated('SecurityGroups', request_pagination_marker="nexttoken")
@rate_limited()
def list_security_groups(client=None, **kwargs):
    return client.describe_security_groups()


@sts_conn('ec2')
@rate_limited()
def describe_security_group(sg_id, client=None, **kwargs):
    try:
        sg_data = client.describe_security_groups(GroupIds=[sg_id])['SecurityGroups'][0]
    except (KeyError, IndexError):
        return None

    return_obj = dict()

    for field in ['Description', 'GroupName', 'IpPermissions', 'OwnerId', 'GroupId', 'IpPermissionsEgress', 'VpcId']:
        try:
            return_obj[field] = sg_data[field]
        except KeyError:
            pass

    return return_obj
