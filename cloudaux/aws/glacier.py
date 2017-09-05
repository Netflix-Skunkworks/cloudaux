import json

from cloudaux.aws.decorators import rate_limited, paginated
from cloudaux.aws.sts import sts_conn


@sts_conn('glacier')
@paginated('VaultList', request_pagination_marker="marker")
@rate_limited()
def list_vaults(client=None, **kwargs):
    return client.list_vaults()


@sts_conn('glacier')
@rate_limited()
def describe_vault(vault_name, client=None, **kwargs):
    vault_data = client.describe_vault(vaultName=vault_name)
    return_obj = dict()

    # some of these fields might not exist, that's ok
    for field in ['VaultARN', 'VaultName', 'CreationDate', 'LastInventoryDate', 'NumberOfArchives', 'SizeInBytes']:
        try:
            return_obj[field] = vault_data[field]
        except KeyError:
            pass

    return return_obj


@sts_conn('glacier')
@rate_limited()
def get_vault_access_policy(vault_name, client=None, **kwargs):
    try:
        return json.loads(client.get_vault_access_policy(vaultName=vault_name)['policy']['Policy'])
    except(client.exceptions.ResourceNotFoundException, KeyError):
        return None


@sts_conn('glacier')
@rate_limited()
def list_tags_for_vault(vault_name, client=None, **kwargs):
    try:
        return client.list_tags_for_vault(vaultName=vault_name)['Tags']
    except KeyError:
        return None
